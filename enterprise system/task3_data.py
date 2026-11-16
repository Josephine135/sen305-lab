from django.contrib.auth import get_user_model
from django.utils import timezone

from requests_app.models import Category, ServiceRequest

if ServiceRequest.objects.filter(title__startswith="Synthetic T3").exists():
    print("Task 3 data already exists - nothing created.")
else:
    User = get_user_model()
    requester, _ = User.objects.get_or_create(username="requester1")
    electrical, _ = Category.objects.get_or_create(name="Electrical")
    ict, _ = Category.objects.get_or_create(
        name="ICT Support",
        defaults={"description": "Computers, networks and software"},
    )

    rows = [
        (electrical, "open", 1), (electrical, "open", 3),
        (electrical, "assigned", 2), (electrical, "assigned", 1),
        (electrical, "resolved", 2), (electrical, "open", 2),
        (ict, "open", 1), (ict, "assigned", 3),
        (ict, "resolved", 1), (ict, "open", 2),
        (ict, "assigned", 2), (ict, "open", 3),
    ]

    for number, (category, status, priority) in enumerate(rows, start=1):
        item = ServiceRequest(
            requester=requester, category=category,
            title="Synthetic T3 request %d" % number,
            description="Synthetic laboratory data.",
            location="Lab %d" % number, priority=priority, status=status,
        )
        if status == "resolved":
            item.resolved_at = timezone.now()
            item.resolution_summary = "Synthetic resolution."
        item.full_clean()
        item.save()

    print("Created", len(rows), "synthetic requests.")

print("Total requests:", ServiceRequest.objects.count())
print("Per category and status:")
from django.db.models import Count
for row in (ServiceRequest.objects.values("category__name", "status")
            .annotate(total=Count("id")).order_by("category__name", "status")):
    print(" ", row["category__name"], "|", row["status"], "|", row["total"])
