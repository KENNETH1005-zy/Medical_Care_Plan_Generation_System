from .models import CarePlan, Doctor, Order, Patient
from .tasks import generate_careplan_task


def create_careplan_and_enqueue(payload):
    patient_name = payload.get("patient_name") or "Unknown Patient"
    patient_email = payload.get("patient_email")
    doctor_name = payload.get("doctor_name")
    doctor_email = payload.get("doctor_email")
    patient_info = payload.get("patient_info")

    patient = Patient.objects.create(name=patient_name, email=patient_email)
    doctor = None
    if doctor_name or doctor_email:
        doctor = Doctor.objects.create(name=doctor_name or "Unknown Doctor", email=doctor_email)

    order = Order.objects.create(patient=patient, doctor=doctor, note=patient_info, status="PENDING")
    care_plan = CarePlan.objects.create(order=order, status="PENDING")
    generate_careplan_task.delay(care_plan.id)

    return care_plan


def get_careplan_status_payload(careplan_id):
    care_plan = CarePlan.objects.get(id=careplan_id)
    payload = {"status": care_plan.status}
    if care_plan.status == "COMPLETED":
        payload["content"] = care_plan.care_plan_text or ""
    return payload
