from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .choices import FinishTier, ServiceKind


class SiteSettings(models.Model):
    """Single row of company details shown across the site. Edit it in the admin."""

    company_name = models.CharField(max_length=100, default="D4 Interiors")
    tagline = models.CharField(
        max_length=200,
        default="Builders, interior designers and renovators. From your plot to your keys.",
    )
    phone = models.CharField(max_length=30, blank=True, help_text="Shown in the header and footer, e.g. +91 98765 43210")
    whatsapp_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Digits only with country code, e.g. 919876543210. Leave blank to hide the WhatsApp button.",
    )
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    office_hours = models.CharField(max_length=120, blank=True, default="Mon to Sat, 9:30 am to 6:30 pm")
    map_embed_url = models.URLField(
        blank=True,
        max_length=1000,
        help_text="Google Maps → Share → Embed a map → copy only the src URL from the iframe code.",
    )
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)

    years_experience = models.PositiveIntegerField(default=0, help_text="Leave at 0 to hide this figure.")
    projects_completed = models.PositiveIntegerField(default=0, help_text="Leave at 0 to hide this figure.")
    sqft_delivered = models.PositiveIntegerField(default=0, help_text="Total square feet built. Leave at 0 to hide.")
    cities_served = models.PositiveIntegerField(default=0, help_text="Leave at 0 to hide this figure.")

    about_story = models.TextField(
        blank=True,
        help_text="A few paragraphs about the company for the About page. Separate paragraphs with a blank line.",
    )
    meta_description = models.CharField(
        max_length=300,
        blank=True,
        default="D4 Interiors builds homes, hospitals and commercial buildings end to end, designs interiors and renovates existing spaces.",
    )

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # The settings row should never be removed.

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    @property
    def has_stats(self):
        return any([self.years_experience, self.projects_completed, self.sqft_delivered, self.cities_served])

    @property
    def phone_link(self):
        return "".join(ch for ch in self.phone if ch.isdigit() or ch == "+")


class Service(models.Model):
    kind = models.CharField(max_length=20, choices=ServiceKind.choices, unique=True)
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.CharField(max_length=240, help_text="One or two sentences for cards and the home page.")
    description = models.TextField(help_text="Full description. Separate paragraphs with a blank line.")
    includes = models.TextField(
        blank=True,
        help_text="What this service covers. One item per line.",
    )
    suited_for = models.CharField(
        max_length=240,
        blank=True,
        help_text="e.g. Homes, hospitals, offices, shops",
    )
    image = models.ImageField(upload_to="services/", blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:service_detail", args=[self.slug])

    @property
    def includes_list(self):
        return [line.strip("-• ").strip() for line in self.includes.splitlines() if line.strip()]


class ProcessStep(models.Model):
    """A stage in the plot-to-keys process shown on the home and services pages."""

    order = models.PositiveIntegerField(default=0)
    title = models.CharField(max_length=80)
    description = models.TextField()
    duration_hint = models.CharField(max_length=60, blank=True, help_text="e.g. 1 to 2 weeks")

    class Meta:
        ordering = ["order"]
        verbose_name = "process stage"

    def __str__(self):
        return f"{self.order}. {self.title}"


class Testimonial(models.Model):
    """Real feedback from clients. Only add reviews you have permission to publish."""

    client_name = models.CharField(max_length=100)
    detail = models.CharField(max_length=140, blank=True, help_text="e.g. Villa owner, Kochi")
    quote = models.TextField()
    project = models.ForeignKey(
        "portfolio.Project", null=True, blank=True, on_delete=models.SET_NULL, related_name="testimonials"
    )
    rating = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "-id"]

    def __str__(self):
        return self.client_name


class FAQ(models.Model):
    question = models.CharField(max_length=240)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class EstimatorRate(models.Model):
    """Per-square-foot rates used by the cost estimator page."""

    kind = models.CharField(max_length=20, choices=ServiceKind.choices)
    tier = models.CharField(max_length=20, choices=FinishTier.choices)
    rate_min = models.PositiveIntegerField(help_text="Lowest rate in ₹ per sq ft")
    rate_max = models.PositiveIntegerField(help_text="Highest rate in ₹ per sq ft")
    tier_note = models.CharField(max_length=200, blank=True, help_text="What this finish level includes")

    class Meta:
        ordering = ["kind", "rate_min"]
        unique_together = [("kind", "tier")]
        verbose_name = "estimator rate"

    def __str__(self):
        return f"{self.get_kind_display()} · {self.get_tier_display()}"
