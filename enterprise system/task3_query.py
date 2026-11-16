from requests_app.models import ServiceRequest

queryset = (
    ServiceRequest.objects
    .filter(category__name="Electrical", status__in=["open", "assigned"])
    .order_by("priority", "created_at")
)

print("ROWS RETURNED:", queryset.count())
for r in queryset:
    print(" -", r.title, "| priority", r.priority, "|", r.status, "|", r.created_at)

print()
print("SQL:")
print(queryset.query)
print()
print("EXPLAIN:")
print(queryset.explain())
