from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.choices import BuildingType, ServiceKind


class ProjectQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class Project(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "completed", "Completed"
        ONGOING = "ongoing", "Ongoing"

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    category = models.CharField(
        max_length=20,
        choices=ServiceKind.choices,
        help_text="Which service this project shows. Used for the portfolio filter.",
    )
    building_type = models.CharField(max_length=20, choices=BuildingType.choices, default=BuildingType.HOME)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.COMPLETED)

    location = models.CharField(max_length=120, blank=True)
    client = models.CharField(max_length=120, blank=True, help_text="Optional. Leave blank for private clients.")
    area_sqft = models.PositiveIntegerField(null=True, blank=True, verbose_name="Built-up area (sq ft)")
    plot_size = models.CharField(max_length=60, blank=True, help_text="e.g. 8 cents, 2400 sq ft")
    floors = models.PositiveSmallIntegerField(null=True, blank=True)
    duration_months = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Duration (months)")
    year = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Year completed")

    summary = models.CharField(max_length=260, help_text="One or two sentences for the project card.")
    description = models.TextField(blank=True, help_text="Separate paragraphs with a blank line.")
    scope = models.TextField(blank=True, help_text="Work we did, one item per line.")

    cover_image = models.ImageField(upload_to="projects/covers/", blank=True)
    before_image = models.ImageField(
        upload_to="projects/before-after/",
        blank=True,
        help_text="For renovations: a photo before work started. Shown with a drag slider against the 'after' photo.",
    )
    after_image = models.ImageField(upload_to="projects/before-after/", blank=True)

    is_featured = models.BooleanField(default=False, help_text="Show on the home page.")
    is_published = models.BooleanField(default=True, help_text="Untick to hide from the website.")
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ["order", "-year", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:150] or "project"
            slug, n = base, 2
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("portfolio:detail", args=[self.slug])

    @property
    def scope_list(self):
        return [line.strip("-• ").strip() for line in self.scope.splitlines() if line.strip()]

    @property
    def has_before_after(self):
        return bool(self.before_image and self.after_image)

    @property
    def display_image(self):
        if self.cover_image:
            return self.cover_image
        if self.after_image:
            return self.after_image
        first = self.images.first()
        return first.image if first else None


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=160, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"Image {self.pk}"
