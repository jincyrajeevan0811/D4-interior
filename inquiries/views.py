import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse

from core.choices import BuildingType, FinishTier, ServiceKind
from core.models import FAQ

from .forms import ContactForm, QuoteForm

logger = logging.getLogger(__name__)


def notify_team(request, inquiry):
    """Email the team about a new enquiry. Failures are logged, never shown to the visitor."""
    recipients = list(settings.INQUIRY_NOTIFY_EMAILS)
    if not recipients:
        return
    admin_url = request.build_absolute_uri(
        reverse("admin:inquiries_inquiry_change", args=[inquiry.pk])
    )
    lines = [
        f"New {inquiry.get_source_display().lower()} from {inquiry.name}",
        "",
        f"Phone: {inquiry.phone}",
        f"Email: {inquiry.email or '-'}",
        f"Prefers: {inquiry.get_preferred_contact_display()}",
        f"Service: {inquiry.get_service_display() or '-'}",
        f"Building: {inquiry.get_building_type_display() or '-'}",
        f"Plot location: {inquiry.plot_location or '-'}",
        f"Plot size: {inquiry.plot_size or '-'}",
        f"Built-up area: {inquiry.built_up_area or '-'} sq ft",
        f"Budget: {inquiry.get_budget_display() or '-'}",
        f"Timeline: {inquiry.get_timeline_display() or '-'}",
        "",
        inquiry.message or "",
        "",
        f"Open in admin: {admin_url}",
    ]
    try:
        send_mail(
            subject=f"[D4 Interiors] New enquiry: {inquiry.name}",
            message="\n".join(lines),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
        )
    except Exception:  # noqa: BLE001
        logger.exception("Could not send enquiry notification email")


def quote(request):
    if request.method == "POST":
        form = QuoteForm(request.POST, request.FILES)
        if form.is_valid():
            inquiry = form.save()
            notify_team(request, inquiry)
            request.session["last_inquiry_name"] = inquiry.name.split()[0]
            return redirect("inquiries:thanks")
    else:
        # Pre-fill from the estimator or a service page link.
        initial = {}
        q = request.GET
        if q.get("service") in ServiceKind.values:
            initial["service"] = q["service"]
        if q.get("building") in BuildingType.values:
            initial["building_type"] = q["building"]
        if q.get("tier") in FinishTier.values:
            initial["finish_tier"] = q["tier"]
        for key, field in (("area", "built_up_area"), ("floors", "floors"), ("low", "estimate_low"), ("high", "estimate_high")):
            if q.get(key, "").isdigit():
                initial[field] = int(q[key])
        form = QuoteForm(initial=initial)
    return render(request, "inquiries/quote.html", {"form": form})


def thanks(request):
    name = request.session.pop("last_inquiry_name", "")
    return render(request, "inquiries/thanks.html", {"first_name": name})


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            notify_team(request, inquiry)
            messages.success(request, "Message sent. We will call you back within one working day.")
            return redirect("inquiries:contact")
    else:
        form = ContactForm()
    return render(
        request,
        "inquiries/contact.html",
        {"form": form, "faqs": FAQ.objects.filter(is_active=True)[:6]},
    )
