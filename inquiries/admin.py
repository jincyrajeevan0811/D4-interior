import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html

from .models import Inquiry

STATUS_COLOURS = {
    "new": ("#7a4e2d", "#fff"),
    "contacted": ("#2f6f8f", "#fff"),
    "site_visit": ("#6a5acd", "#fff"),
    "quoted": ("#b8860b", "#fff"),
    "won": ("#2e7d32", "#fff"),
    "lost": ("#9e9e9e", "#fff"),
}


def make_status_action(status, label):
    def action(modeladmin, request, queryset):
        n = queryset.update(status=status)
        modeladmin.message_user(request, f"{n} enquiry(s) marked as “{label}”.")

    action.__name__ = f"mark_{status}"
    action.short_description = f"Mark as: {label}"
    return action


class FollowUpFilter(admin.SimpleListFilter):
    title = "follow-up"
    parameter_name = "follow_up"

    def lookups(self, request, model_admin):
        return [("due", "Due today or overdue"), ("upcoming", "Upcoming")]

    def queryset(self, request, queryset):
        today = timezone.localdate()
        if self.value() == "due":
            return queryset.filter(follow_up_on__lte=today).exclude(status__in=["won", "lost"])
        if self.value() == "upcoming":
            return queryset.filter(follow_up_on__gt=today)
        return queryset


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone_link",
        "service",
        "building_type",
        "plot_location",
        "budget",
        "status_badge",
        "follow_up_on",
        "created_at",
    )
    list_display_links = ("name",)
    list_filter = ("status", "source", "service", "building_type", "budget", "timeline", FollowUpFilter, "created_at")
    search_fields = ("name", "phone", "email", "plot_location", "message", "admin_notes")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at", "source", "attachment_link", "estimate_range")
    list_per_page = 40
    save_on_top = True
    fieldsets = (
        ("Track this enquiry", {"fields": (("status", "follow_up_on"), "admin_notes")}),
        ("Client", {"fields": (("name", "phone"), ("email", "preferred_contact"))}),
        (
            "Project",
            {
                "fields": (
                    ("service", "building_type", "finish_tier"),
                    ("plot_location", "plot_size"),
                    ("built_up_area", "floors", "has_approved_plan"),
                    ("budget", "timeline"),
                    "estimate_range",
                    "message",
                    "attachment",
                    "attachment_link",
                )
            },
        ),
        ("Record", {"fields": (("source", "created_at", "updated_at"),), "classes": ("collapse",)}),
    )
    actions = [make_status_action(value, label) for value, label in Inquiry.Status.choices] + ["export_csv"]

    @admin.display(description="Phone", ordering="phone")
    def phone_link(self, obj):
        digits = "".join(c for c in obj.phone if c.isdigit() or c == "+")
        return format_html('<a href="tel:{}">{}</a>', digits, obj.phone)

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        bg, fg = STATUS_COLOURS.get(obj.status, ("#666", "#fff"))
        return format_html(
            '<span style="background:{};color:{};padding:2px 9px;border-radius:999px;font-size:11px;white-space:nowrap">{}</span>',
            bg,
            fg,
            obj.get_status_display(),
        )

    @admin.display(description="Uploaded file")
    def attachment_link(self, obj):
        if not obj.attachment:
            return "None"
        return format_html('<a href="{}" target="_blank" rel="noopener">Open file</a>', obj.attachment.url)

    @admin.display(description="Estimator range")
    def estimate_range(self, obj):
        if not obj.estimate_low:
            return "-"
        return f"₹{obj.estimate_low:,} to ₹{(obj.estimate_high or obj.estimate_low):,}"

    @admin.action(description="Download selected as a spreadsheet (CSV)")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type="text/csv; charset=utf-8")
        stamp = timezone.localtime().strftime("%Y-%m-%d")
        response["Content-Disposition"] = f'attachment; filename="d4-enquiries-{stamp}.csv"'
        response.write("﻿")  # Lets Excel read ₹ and other characters correctly.
        writer = csv.writer(response)
        cols = [
            ("Received", lambda o: timezone.localtime(o.created_at).strftime("%Y-%m-%d %H:%M")),
            ("Status", lambda o: o.get_status_display()),
            ("Name", lambda o: o.name),
            ("Phone", lambda o: o.phone),
            ("Email", lambda o: o.email),
            ("Prefers", lambda o: o.get_preferred_contact_display()),
            ("Source", lambda o: o.get_source_display()),
            ("Service", lambda o: o.get_service_display()),
            ("Building", lambda o: o.get_building_type_display()),
            ("Finish", lambda o: o.get_finish_tier_display()),
            ("Plot location", lambda o: o.plot_location),
            ("Plot size", lambda o: o.plot_size),
            ("Built-up sq ft", lambda o: o.built_up_area or ""),
            ("Floors", lambda o: o.floors or ""),
            ("Approved plan", lambda o: {True: "Yes", False: "No"}.get(o.has_approved_plan, "")),
            ("Budget", lambda o: o.get_budget_display()),
            ("Timeline", lambda o: o.get_timeline_display()),
            ("Message", lambda o: o.message),
            ("Follow up on", lambda o: o.follow_up_on or ""),
            ("Notes", lambda o: o.admin_notes),
        ]
        writer.writerow([c[0] for c in cols])
        for obj in queryset:
            writer.writerow([c[1](obj) for c in cols])
        return response
