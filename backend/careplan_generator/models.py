from django.db import models


class Patient(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Patient: {self.name}"


class Doctor(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Doctor: {self.name}"


class Order(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="orders")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} for {self.patient.name}"


class CarePlan(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="care_plans",
        null=True,
        blank=True,
    )
    care_plan_text = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CarePlan #{self.id} - Status: {self.status}"
