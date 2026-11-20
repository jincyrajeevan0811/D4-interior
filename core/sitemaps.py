from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from portfolio.models import Project

from .models import Service


class StaticSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return ["core:home", "core:services", "portfolio:list", "core:estimate", "core:about", "inquiries:quote", "inquiries:contact"]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return Service.objects.filter(is_active=True)


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Project.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {"static": StaticSitemap, "services": ServiceSitemap, "projects": ProjectSitemap}
