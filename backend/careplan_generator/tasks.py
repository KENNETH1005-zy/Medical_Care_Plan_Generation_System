from anthropic import Anthropic
from celery import shared_task
from decouple import config
from django.db import transaction

from .models import CarePlan


@shared_task(bind=True, max_retries=3)
def generate_careplan_task(self, careplan_id):
    careplan = CarePlan.objects.select_related("order", "order__patient", "order__doctor").get(id=careplan_id)

    with transaction.atomic():
        careplan.status = "PROCESSING"
        careplan.save(update_fields=["status", "updated_at"])
        if careplan.order:
            careplan.order.status = "PROCESSING"
            careplan.order.save(update_fields=["status"])

    try:
        client = Anthropic(api_key=config("ANTHROPIC_API_KEY"))

        patient_name = careplan.order.patient.name if careplan.order else "Unknown"
        doctor_name = careplan.order.doctor.name if careplan.order and careplan.order.doctor else "Unknown"
        order_note = careplan.order.note if careplan.order and careplan.order.note else ""

        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": f"Generate a medical care plan.\nPatient: {patient_name}\nDoctor: {doctor_name}\nNote: {order_note}",
                }
            ],
        )

        care_plan_text = message.content[0].text if message and message.content else ""
    except Exception as exc:
        if self.request.retries < self.max_retries:
            countdown = 2 ** self.request.retries
            raise self.retry(exc=exc, countdown=countdown)

        with transaction.atomic():
            careplan.status = "FAILED"
            careplan.save(update_fields=["status", "updated_at"])
            if careplan.order:
                careplan.order.status = "FAILED"
                careplan.order.save(update_fields=["status"])
        raise

    with transaction.atomic():
        careplan.care_plan_text = care_plan_text
        careplan.status = "COMPLETED"
        careplan.save(update_fields=["care_plan_text", "status", "updated_at"])
        if careplan.order:
            careplan.order.status = "COMPLETED"
            careplan.order.save(update_fields=["status"])

    return careplan.id
