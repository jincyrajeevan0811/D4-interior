from django.shortcuts import get_object_or_404, render

from core.choices import ServiceKind

from .models import Project


def project_list(request):
    projects = Project.objects.published().prefetch_related("images")
    active = request.GET.get("category", "")
    if active not in ServiceKind.values:
        active = ""
    counts = {kind: 0 for kind in ServiceKind.values}
    for p in projects:
        counts[p.category] += 1
    filters = [("", "All work", len(projects))] + [
        (value, label, counts[value]) for value, label in ServiceKind.choices
    ]
    return render(
        request,
        "portfolio/list.html",
        {"projects": projects, "active": active, "filters": filters},
    )


def project_detail(request, slug):
    project = get_object_or_404(Project.objects.published().prefetch_related("images"), slug=slug)
    related = (
        Project.objects.published()
        .filter(category=project.category)
        .exclude(pk=project.pk)[:3]
    )
    return render(
        request,
        "portfolio/detail.html",
        {
            "project": project,
            "related": related,
            "testimonial": project.testimonials.filter(is_active=True).first(),
        },
    )
