from django.contrib.auth.models import User
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings

from inquiries.models import Inquiry
from portfolio.models import Project

from .templatetags.d4 import inr


class SiteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_demo", "--no-projects", stdout=open("/dev/null", "w"))
        cls.p1 = Project.objects.create(title="Villa", category="construction", summary="A villa", area_sqft=2000, is_featured=True)
        cls.p2 = Project.objects.create(title="Flat interiors", category="interior", summary="Flat")
        cls.hidden = Project.objects.create(title="Secret", category="renovation", summary="x", is_published=False)

    def test_public_pages_load(self):
        for url in ["/", "/about/", "/services/", "/services/turnkey-construction/", "/cost-estimator/",
                    "/projects/", "/projects/?category=interior", self.p1.get_absolute_url(),
                    "/get-a-quote/", "/contact/", "/sitemap.xml", "/robots.txt"]:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_unpublished_project_is_hidden(self):
        self.assertEqual(self.client.get(self.hidden.get_absolute_url()).status_code, 404)
        self.assertNotContains(self.client.get("/projects/"), "Secret")

    def test_inr_format(self):
        self.assertEqual(inr(12345678), "1,23,45,678")
        self.assertEqual(inr(999), "999")

    @override_settings(INQUIRY_NOTIFY_EMAILS=["team@example.com"])
    def test_quote_submission(self):
        data = {
            "service": "construction", "building_type": "hospital", "plot_location": "Kochi",
            "name": "Anil", "phone": "+91 99999 88888", "preferred_contact": "phone", "approved_plan": "yes",
            "attachment": SimpleUploadedFile("plot.pdf", b"%PDF-1.4"),
        }
        r = self.client.post("/get-a-quote/", data)
        self.assertRedirects(r, "/get-a-quote/sent/")
        i = Inquiry.objects.get()
        self.assertTrue(i.has_approved_plan)
        self.assertEqual(len(mail.outbox), 1)
        i.attachment.delete()

    def test_quote_rejects_bad_phone_and_bots(self):
        base = {"service": "interior", "building_type": "home", "plot_location": "x", "name": "A", "preferred_contact": "phone"}
        self.client.post("/get-a-quote/", {**base, "phone": "abc"})
        self.client.post("/get-a-quote/", {**base, "phone": "9876543210", "website": "http://spam"})
        self.assertEqual(Inquiry.objects.count(), 0)

    def test_contact_form(self):
        r = self.client.post("/contact/", {"name": "Priya", "phone": "9876543210", "message": "Call me"}, follow=True)
        self.assertContains(r, "Message sent")
        self.assertEqual(Inquiry.objects.get().source, "contact")

    def test_admin_dashboard_and_csv(self):
        Inquiry.objects.create(name="Lead", phone="9876543210")
        User.objects.create_superuser("boss", "b@example.com", "pw-123456!")
        self.client.login(username="boss", password="pw-123456!")
        self.assertContains(self.client.get("/admin/"), "New enquiries to answer")
        ids = list(Inquiry.objects.values_list("id", flat=True))
        r = self.client.post("/admin/inquiries/inquiry/", {"action": "export_csv", "_selected_action": ids})
        self.assertEqual(r["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("Lead", r.content.decode("utf-8-sig"))
