from .models import Service, SiteSettings


def site(request):
    """Company details and the service menu, available in every template."""
    return {
        "site": SiteSettings.load(),
        "nav_services": Service.objects.filter(is_active=True),
    }
