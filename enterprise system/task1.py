from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from requests_app.models import Category, ServiceRequest

User = get_user_model()
requester, _ = User.objects.get_or_create(username="requester1")
electrical, _ = Category.objects.get_or_create(
    name="Electrical",
    defaults={"description": "Electrical faults and maintenance"},
)

now = timezone.now()

ServiceRequest.objects.create(
    requester=requester, category=electrical,
    title="Synthetic request A - due soon",
    description="Synthetic laboratory data.",
    location="Lab 1", priority=2,
    due_at=now + timedelta(hours=2),
)
ServiceRequest.objects.create(
    requester=requester, category=electrical,
    title="Synthetic request B - due later",
    description="Synthetic laboratory data.",
    location="Lab 2", priority=3,
    due_at=now + timedelta(days=3),
)

cutoff = now + timedelta(days=1)
qs = ServiceRequest.objects.filter(due_at__lt=cutoff)

print("Cutoff time:", cutoff)
print("Requests due before cutoff:")
for r in qs:
    print(" -", r.title, "| due:", r.due_at)
print("Count:", qs.count())
print("SQL:", qs.query)
