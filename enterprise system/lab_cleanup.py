from requests_app.models import ServiceRequest

for title in ["Synthetic request A - due soon", "Synthetic request B - due later"]:
    rows = list(ServiceRequest.objects.filter(title=title).order_by("created_at"))
    for extra in rows[1:]:
        extra.delete()
    print(title, "->", ServiceRequest.objects.filter(title=title).count(), "left")
