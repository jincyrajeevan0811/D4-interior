from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from portfolio.models import Project

from .choices import BuildingType, FinishTier, ServiceKind
from .models import FAQ, EstimatorRate, ProcessStep, Service, Testimonial


def home(request):
    # The home grid is one large card plus two (3) or plus five (6), so trim to fit.
    featured = list(Project.objects.published().filter(is_featured=True)[:6])
    if len(featured) < 3:
        featured = list(Project.objects.published()[:6])
    featured = featured[:6] if len(featured) >= 6 else featured[:3]
    return render(
        request,
        "core/home.html",
        {
            "services": Service.objects.filter(is_active=True),
            "featured": featured,
            "steps": ProcessStep.objects.all(),
            "testimonials": Testimonial.objects.filter(is_active=True)[:6],
            "faqs": FAQ.objects.filter(is_active=True)[:5],
        },
    )


def about(request):
    return render(
        request,
        "core/about.html",
        {"steps": ProcessStep.objects.all(), "services": Service.objects.filter(is_active=True)},
    )


def service_list(request):
    return render(
        request,
        "core/services.html",
        {"services": Service.objects.filter(is_active=True), "steps": ProcessStep.objects.all()},
    )


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug, is_active=True)
    return render(
        request,
        "core/service_detail.html",
        {
            "service": service,
            "projects": Project.objects.published().filter(category=service.kind)[:6],
            "steps": ProcessStep.objects.all() if service.kind == ServiceKind.CONSTRUCTION else None,
            "rates": EstimatorRate.objects.filter(kind=service.kind),
            "faqs": FAQ.objects.filter(is_active=True)[:4],
        },
    )


def estimate(request):
    rates = {}
    for r in EstimatorRate.objects.all():
        rates.setdefault(r.kind, {})[r.tier] = {"min": r.rate_min, "max": r.rate_max, "note": r.tier_note}
    return render(
        request,
        "core/estimate.html",
        {
            "rates": rates,
            "kinds": ServiceKind.choices,
            "tiers": FinishTier.choices,
            "building_types": BuildingType.choices,
        },
    )


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /get-a-quote/sent/",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def page_not_found(request, exception):
    return render(request, "404.html", status=404)
