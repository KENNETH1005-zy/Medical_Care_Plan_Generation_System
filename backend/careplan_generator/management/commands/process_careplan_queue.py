import logging

from django.core.management.base import BaseCommand
from django.db import transaction
from decouple import config
import redis
import anthropic

from careplan_generator.models import CarePlan


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process all pending care plan tasks from Redis queue once."

    def handle(self, *args, **options):
        redis_url = config("REDIS_URL", default="redis://redis:6379/0")
        redis_client = redis.from_url(redis_url)

        anthropic_api_key = config("ANTHROPIC_API_KEY", default="")
        if not anthropic_api_key:
            self.stderr.write("ANTHROPIC_API_KEY is not configured.")
            return

        client = anthropic.Anthropic(api_key=anthropic_api_key)

        processed = 0
        while True:
            careplan_id = redis_client.lpop("careplan_queue")
            if careplan_id is None:
                break

            try:
                careplan_id = int(careplan_id)
            except (TypeError, ValueError):
                logger.warning("Invalid careplan id in queue: %s", careplan_id)
                continue

            try:
                care_plan = CarePlan.objects.select_related("order").get(id=careplan_id)
            except CarePlan.DoesNotExist:
                logger.warning("CarePlan not found: %s", careplan_id)
                continue

            care_plan.status = "PROCESSING"
            care_plan.save(update_fields=["status", "updated_at"])

            patient_info = care_plan.order.note or ""
            prompt_template = (
                "Generate a detailed care plan based on the patient information below.\n\n"
                f"Patient information: {patient_info}\n\n"
                "Care plan:"
            )

            try:
                message = client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt_template}],
                )
                generated_text = message.content[0].text if message.content else "No care plan generated."

                with transaction.atomic():
                    care_plan.care_plan_text = generated_text
                    care_plan.status = "COMPLETED"
                    care_plan.save(update_fields=["care_plan_text", "status", "updated_at"])
                processed += 1
            except Exception as exc:  # pragma: no cover - runtime safeguard
                care_plan.status = "FAILED"
                care_plan.care_plan_text = f"Failed to generate care plan: {exc}"
                care_plan.save(update_fields=["care_plan_text", "status", "updated_at"])
                logger.exception("Failed to process careplan %s", careplan_id)

        self.stdout.write(f"Processed {processed} care plan(s).")
