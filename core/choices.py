"""Shared choice lists used across the site, admin and forms."""
from django.db import models


class ServiceKind(models.TextChoices):
    CONSTRUCTION = "construction", "Turnkey construction"
    INTERIOR = "interior", "Interior design"
    RENOVATION = "renovation", "Renovation & reconstruction"


class BuildingType(models.TextChoices):
    HOME = "home", "Home / villa"
    APARTMENT = "apartment", "Apartment / flat"
    HOSPITAL = "hospital", "Hospital / clinic"
    COMMERCIAL = "commercial", "Commercial building"
    OFFICE = "office", "Office"
    RETAIL = "retail", "Shop / showroom"
    HOSPITALITY = "hospitality", "Hotel / restaurant"
    INSTITUTION = "institution", "School / institution"
    OTHER = "other", "Other"


class FinishTier(models.TextChoices):
    ESSENTIAL = "essential", "Essential"
    PREMIUM = "premium", "Premium"
    LUXURY = "luxury", "Luxury"
