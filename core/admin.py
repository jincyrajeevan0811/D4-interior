from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .models import FAQ, EstimatorRate, ProcessStep, Service, SiteSettings, Testimonial


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Company", {"fields": ("company_name", "tagline", "meta_description", "about_story")}),
        ("Contact details", {"fields": ("phone", "whatsapp_number", "email", "address", "office_hours", "map_embed_url")}),
        ("Social links", {"fields": ("instagram_url", "facebook_url", "youtube_url", "linkedin_url"), "classes": ("collapse",)}),
        (
            "Figures shown on the home page",
            {
                "fields": ("years_experience", "projects_completed", "sqft_delivered", "cities_served"),
                "description": "Only figures above 0 are shown. Use real numbers you can stand behind.",
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        # There is only one settings row, so go straight to editing it.
        obj = SiteSettings.load()
        return redirect(reverse("admin:core_sitesettings_change", args=[obj.pk]))


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "kind", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    fields = ("kind", "title", "slug", "summary", "description", "includes", "suited_for", "image", "order", "is_active")


@admin.register(ProcessStep)
class ProcessStepAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "duration_hint")
    list_display_links = ("title",)
    list_editable = ("order",)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("client_name", "detail", "project", "rating", "is_active", "order")
    list_editable = ("is_active", "order")
    autocomplete_fields = ("project",)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(EstimatorRate)
class EstimatorRateAdmin(admin.ModelAdmin):
    list_display = ("kind", "tier", "rate_min", "rate_max", "tier_note")
    list_editable = ("rate_min", "rate_max")
    list_filter = ("kind",)
