from django.contrib import admin
from django.utils.html import format_html

from .models import Project, ProjectImage


def thumb(image, size=64):
    if not image:
        return format_html('<span style="color:#888">No photo</span>')
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:4px" alt="">',
        image.url,
        size,
        round(size * 0.7),
    )


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 3
    fields = ("preview", "image", "caption", "order")
    readonly_fields = ("preview",)

    @admin.display(description="Preview")
    def preview(self, obj):
        return thumb(obj.image if obj.pk else None, 90)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "cover",
        "title",
        "category",
        "building_type",
        "location",
        "area_sqft",
        "year",
        "status",
        "is_featured",
        "is_published",
        "order",
    )
    list_display_links = ("cover", "title")
    list_editable = ("is_featured", "is_published", "order")
    list_filter = ("category", "building_type", "status", "is_featured", "is_published", "year")
    search_fields = ("title", "location", "client", "summary")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("cover_preview", "before_after_preview")
    inlines = [ProjectImageInline]
    actions = ["publish", "unpublish", "feature", "unfeature"]
    list_per_page = 30
    save_on_top = True
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "building_type", "status")}),
        ("Project facts", {"fields": (("location", "client"), ("area_sqft", "plot_size"), ("floors", "duration_months", "year"))}),
        ("Story", {"fields": ("summary", "description", "scope")}),
        ("Cover photo", {"fields": ("cover_image", "cover_preview")}),
        (
            "Before and after (renovations)",
            {
                "fields": ("before_image", "after_image", "before_after_preview"),
                "description": "Upload both photos from the same angle. The website shows them with a drag slider.",
            },
        ),
        ("Visibility", {"fields": ("is_published", "is_featured", "order")}),
    )

    @admin.display(description="")
    def cover(self, obj):
        return thumb(obj.display_image, 56)

    @admin.display(description="Current cover")
    def cover_preview(self, obj):
        return thumb(obj.cover_image, 220)

    @admin.display(description="Preview")
    def before_after_preview(self, obj):
        if not obj.has_before_after:
            return "Add both photos to see the comparison."
        return format_html("{} &nbsp; {}", thumb(obj.before_image, 160), thumb(obj.after_image, 160))

    @admin.action(description="Publish selected projects")
    def publish(self, request, qs):
        n = qs.update(is_published=True)
        self.message_user(request, f"{n} project(s) published.")

    @admin.action(description="Hide selected projects from the website")
    def unpublish(self, request, qs):
        n = qs.update(is_published=False)
        self.message_user(request, f"{n} project(s) hidden.")

    @admin.action(description="Feature on the home page")
    def feature(self, request, qs):
        n = qs.update(is_featured=True)
        self.message_user(request, f"{n} project(s) featured.")

    @admin.action(description="Remove from the home page")
    def unfeature(self, request, qs):
        n = qs.update(is_featured=False)
        self.message_user(request, f"{n} project(s) removed from the home page.")
