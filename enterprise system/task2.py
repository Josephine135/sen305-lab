from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

from requests_app.models import Category, ServiceRequest

User = get_user_model()
requester = User.objects.get(username="requester1")
category = Category.objects.get(name="Electrical")


def make(**extra):
    values = dict(
        requester=requester, category=category,
        title="Synthetic rule test", description="Synthetic laboratory data.",
        location="Lab 1", priority=2,
    )
    values.update(extra)
    return ServiceRequest(**values)


def check(label, item):
    try:
        item.full_clean()
        print(label, "-> PASSED validation")
    except ValidationError as error:
        print(label, "-> REJECTED:", error.message_dict)


check("1. RESOLVED, no resolved_at, no summary", make(status="resolved"))
check("2. CLOSED, resolved_at set, blank summary",
      make(status="closed", resolved_at=timezone.now(), resolution_summary="   "))
check("3. RESOLVED, resolved_at and summary set",
      make(status="resolved", resolved_at=timezone.now(),
           resolution_summary="Replaced the faulty socket."))
check("4. OPEN, no summary needed", make(status="open"))
