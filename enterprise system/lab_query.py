from datetime import timedelta
from django.utils import timezone
from requests_app.models import ServiceRequest

cutoff = timezone.now() + timedelta(days=1)
qs = ServiceRequest.objects.filter(due_at__lt=cutoff)
print("Cutoff time:", cutoff)
for r in qs:
    print(" -", r.title, "| due:", r.due_at)
print("Count:", qs.count())
print("SQL:", qs.query)
