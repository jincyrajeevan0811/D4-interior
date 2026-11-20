from django.core.validators import FileExtensionValidator
from django.db import models

from core.choices import BuildingType, FinishTier, ServiceKind


def validate_file_size(f):
    from django.core.exceptions import ValidationError

    if f.size > 10 * 1024 * 1024:
        raise ValidationError("Files must be 10 MB or smaller.")


class Inquiry(models.Model):
    class Source(models.TextChoices):
        QUOTE = "quote", "Quote request"
        CONTACT = "contact", "Contact form"
        ESTIMATOR = "estimator", "Cost estimator"

    class Status(models.TextChoices):
        NEW = "new", "New"
        CONTACTED = "contacted", "Contacted"
        SITE_VISIT = "site_visit", "Site visit planned"
        QUOTED = "quoted", "Quote sent"
        WON = "won", "Won"
        LOST = "lost", "Closed / lost"

    class Budget(models.TextChoices):
        UNDER_10L = "lt10l", "Under ₹10 lakh"
        L10_25 = "10-25l", "₹10 to 25 lakh"
        L25_50 = "25-50l", "₹25 to 50 lakh"
        L50_1CR = "50l-1cr", "₹50 lakh to 1 crore"
        OVER_1CR = "gt1cr", "Above ₹1 crore"
        UNSURE = "unsure", "Not sure yet"

    class Timeline(models.TextChoices):
        NOW = "now", "As soon as possible"
        M3 = "3m", "Within 3 months"
        M6 = "6m", "Within 6 months"
        LATER = "later", "Later than 6 months"
        EXPLORING = "exploring", "Just exploring"

    class Contact(models.TextChoices):
        PHONE = "phone", "Phone call"
        WHATSAPP = "whatsapp", "WhatsApp"
        EMAIL = "email", "Email"

    # What
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.QUOTE)
    service = models.CharField(max_length=20, choices=ServiceKind.choices, blank=True)
    building_type = models.CharField(max_length=20, choices=BuildingType.choices, blank=True)
    finish_tier = models.CharField(max_length=20, choices=FinishTier.choices, blank=True)

    # Plot / site
    plot_location = models.CharField(max_length=200, blank=True, verbose_name="Plot / site location")
    plot_size = models.CharField(max_length=60, blank=True, help_text="As the client wrote it, e.g. 10 cents")
    built_up_area = models.PositiveIntegerField(null=True, blank=True, verbose_name="Built-up area needed (sq ft)")
    floors = models.PositiveSmallIntegerField(null=True, blank=True)
    has_approved_plan = models.BooleanField(null=True, blank=True, verbose_name="Has an approved plan")
    budget = models.CharField(max_length=20, choices=Budget.choices, blank=True)
    timeline = models.CharField(max_length=20, choices=Timeline.choices, blank=True)
    message = models.TextField(blank=True)
    attachment = models.FileField(
        upload_to="inquiries/%Y/%m/",
        blank=True,
        validators=[
            FileExtensionValidator(["pdf", "jpg", "jpeg", "png", "webp", "dwg", "dxf"]),
            validate_file_size,
        ],
        help_text="Plot sketch, survey, plan or photos.",
    )
    estimate_low = models.PositiveIntegerField(null=True, blank=True, help_text="From the estimator, in ₹")
    estimate_high = models.PositiveIntegerField(null=True, blank=True, help_text="From the estimator, in ₹")

    # Who
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    preferred_contact = models.CharField(max_length=20, choices=Contact.choices, default=Contact.PHONE)

    # Admin tracking
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, db_index=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes. Never shown to the client.")
    follow_up_on = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "enquiry"
        verbose_name_plural = "enquiries"

    def __str__(self):
        return f"{self.name} ({self.get_service_display() or self.get_source_display()})"
