from datetime import timedelta

from django import template
from django.db.models import Count
from django.utils import timezone

register = template.Library()


@register.filter
def inr(value):
    """Format a number the Indian way: 12,34,567."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return value
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if n < 0 else "") + s


@register.filter
def compact_sqft(value):
    """12000 -> 12k, 1500000 -> 15 lakh."""
    try:
        n = int(value)
    except (TypeError, ValueError):
        return value
    if n >= 100000:
        v = n / 100000
        return f"{v:.1f}".rstrip("0").rstrip(".") + " lakh"
    if n >= 1000:
        v = n / 1000
        return f"{v:.1f}".rstrip("0").rstrip(".") + "k"
    return str(n)


@register.inclusion_tag("admin/_dashboard.html")
def admin_dashboard():
    from inquiries.models import Inquiry
    from portfolio.models import Project

    today = timezone.localdate()
    month_start = today.replace(day=1)
    inquiries = Inquiry.objects.all()
    by_status = dict(inquiries.values_list("status").annotate(c=Count("id")))
    return {
        "new_count": by_status.get("new", 0),
        "month_count": inquiries.filter(created_at__date__gte=month_start).count(),
        "week_count": inquiries.filter(created_at__date__gte=today - timedelta(days=7)).count(),
        "due_count": inquiries.filter(follow_up_on__lte=today).exclude(status__in=["won", "lost"]).count(),
        "won_count": by_status.get("won", 0),
        "pipeline": [(label, by_status.get(value, 0), value) for value, label in Inquiry.Status.choices],
        "recent": inquiries[:6],
        "project_count": Project.objects.published().count(),
        "hidden_count": Project.objects.filter(is_published=False).count(),
        "by_category": [
            (label, Project.objects.published().filter(category=value).count(), value)
            for value, label in Project._meta.get_field("category").choices
        ],
    }
