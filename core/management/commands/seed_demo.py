"""
Fill the site with starter content so you can see every page working.

    python manage.py seed_demo              # services, process, FAQs, rates, sample projects
    python manage.py seed_demo --no-projects
    python manage.py seed_demo --reset      # delete sample projects first

Sample projects are placeholders with drawn images. Replace them with your real
work in the admin before going live. No testimonials are created: only publish
real client feedback.
"""
import io
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from core.models import FAQ, EstimatorRate, ProcessStep, Service, SiteSettings
from portfolio.models import Project, ProjectImage

SERVICES = [
    {
        "kind": "construction",
        "title": "Turnkey construction",
        "summary": "We take your plot from soil test and foundation to a finished building and hand you the keys.",
        "description": (
            "Give us the plot and your brief. We prepare the design and structural drawings, support you through "
            "permit approvals, build the foundation and structure, complete electrical, plumbing and finishing work, "
            "and hand over a building that is ready to move into.\n\n"
            "You sign one contract and work with one project manager. Billing is stage-wise, so you pay as each "
            "stage is completed and checked."
        ),
        "includes": "Site survey and soil test\nArchitectural and structural drawings\nPermit and approval support\n"
        "Foundation, structure and roofing\nElectrical, plumbing and drainage\nFlooring, painting and finishing\n"
        "Interiors and landscaping on request\nFinal inspection and key handover",
        "suited_for": "Homes, villas, hospitals, clinics, offices, shops and commercial buildings",
        "order": 1,
    },
    {
        "kind": "interior",
        "title": "Interior design",
        "summary": "Planned, designed and fitted interiors for homes, clinics, offices and shops, built by others or by us.",
        "description": (
            "We plan the layout, show you 3D views before work starts, and build everything on site or in our "
            "workshop: modular kitchens, wardrobes, false ceilings, lighting, wall finishes and furniture.\n\n"
            "Materials and fittings are agreed in writing up front, so the finished room matches what you approved."
        ),
        "includes": "Space planning and 3D views\nModular kitchens and wardrobes\nFalse ceilings and lighting design\n"
        "TV units, storage and custom furniture\nWall finishes, panelling and flooring\nSoft furnishing and styling",
        "suited_for": "Apartments, villas, clinics, offices, showrooms and restaurants",
        "order": 2,
    },
    {
        "kind": "renovation",
        "title": "Renovation and reconstruction",
        "summary": "We repair, extend or rebuild existing buildings, from a kitchen remodel to adding a full floor.",
        "description": (
            "Older buildings need a careful start. We inspect the structure, check what can be kept, and plan the "
            "work so you can often stay in part of the building while we work.\n\n"
            "From waterproofing and re-roofing to adding floors or converting a home into a clinic, we handle the "
            "structural work and the finishing."
        ),
        "includes": "Structural inspection and repair\nAdding floors and extensions\nRe-roofing and waterproofing\n"
        "Kitchen and bathroom remodels\nRewiring and re-plumbing\nChange of use, e.g. home to clinic",
        "suited_for": "Homes, apartments, shops, offices and older commercial buildings",
        "order": 3,
    },
]

STEPS = [
    ("Site visit and brief", "We visit the plot, take measurements, check access and soil, and note everything you need from the building.", "1 week"),
    ("Design and estimate", "Floor plans, elevations and 3D views, followed by an itemised estimate you can compare line by line.", "2 to 4 weeks"),
    ("Approvals", "We prepare the drawings and documents for permits and support you through the approval process.", "2 to 8 weeks"),
    ("Foundation", "Setting out, excavation, footings and plinth, each checked before we move on.", "3 to 6 weeks"),
    ("Structure", "Columns, beams, slabs, walls and roof, with curing time built into the schedule.", "3 to 6 months"),
    ("Services", "Electrical, plumbing, drainage and any medical gas or HVAC lines the building needs.", "1 to 2 months"),
    ("Finishes and interiors", "Plastering, flooring, painting, doors, windows, kitchens and wardrobes.", "2 to 3 months"),
    ("Inspection and handover", "A joint walk-through, a snag list we close out, documents and warranty, then the keys.", "1 to 2 weeks"),
]

FAQS = [
    ("Do you work only on our plot, or do you help find land?",
     "We build on the plot you own. If you are still choosing land, we can visit shortlisted plots with you and point out anything that affects construction cost."),
    ("How is payment structured?",
     "Stage-wise. The contract lists each stage, what it includes and its share of the total. You pay as each stage is completed and checked."),
    ("Can you handle building permits?",
     "We prepare the drawings and documents and support you through the approval process. The application is made in the owner's name."),
    ("Do you build hospitals and commercial buildings as well as homes?",
     "Yes. We build homes, hospitals and clinics, offices, shops and other commercial buildings, and design interiors for all of them."),
    ("Is the site visit really free?",
     "Yes. The first visit to understand the plot and your brief is free and carries no obligation."),
    ("Can we take only the interior work?",
     "Yes. Interiors and renovation are offered on their own, including for buildings constructed by someone else."),
]

RATES = {
    "construction": [
        ("essential", 1800, 2200, "Standard tiles, branded paint, basic sanitary fittings"),
        ("premium", 2300, 2900, "Vitrified tiles, teak or engineered doors, mid-range fittings"),
        ("luxury", 3000, 4200, "Imported flooring, designer fittings, smart wiring"),
    ],
    "interior": [
        ("essential", 900, 1400, "Laminate finishes, standard hardware"),
        ("premium", 1500, 2400, "Acrylic or veneer finishes, soft-close hardware"),
        ("luxury", 2500, 4000, "Custom joinery, premium veneers, designer lighting"),
    ],
    "renovation": [
        ("essential", 700, 1200, "Repairs, repainting and essential replacements"),
        ("premium", 1300, 2000, "Re-plastering, new flooring and updated services"),
        ("luxury", 2100, 3200, "Structural changes with complete refinishing"),
    ],
}

PROJECTS = [
    ("construction", "home", "Two-storey family home", "Sample location", 2650, "8 cents", 2, 11, 2025, True,
     "A four-bedroom home built from an empty plot, with a sloped roof over the living area and a covered car porch."),
    ("construction", "hospital", "30-bed community clinic", "Sample location", 14200, "40 cents", 3, 18, 2024, True,
     "A three-floor clinic with outpatient wards, a minor theatre, lift core and medical gas lines, built and handed over ready to operate."),
    ("construction", "commercial", "Three-floor retail and office block", "Sample location", 9800, "22 cents", 3, 15, 2024, False,
     "Shops at street level with two floors of rentable office space above, designed for flexible partitioning."),
    ("construction", "home", "Single-storey courtyard house", "Sample location", 1850, "6 cents", 1, 9, 2025, False,
     "A compact home built around a central open courtyard for light and cross-ventilation."),
    ("interior", "apartment", "Three-bedroom apartment interiors", "Sample location", 1650, "", None, 3, 2025, True,
     "Modular kitchen, wardrobes, a TV wall and false ceilings, finished in light oak and white."),
    ("interior", "office", "Open-plan office for 40", "Sample location", 4200, "", None, 4, 2024, False,
     "Workstations, two meeting rooms, a pantry and acoustic ceiling panels for a growing software team."),
    ("interior", "hospital", "Dental clinic fit-out", "Sample location", 1200, "", None, 2, 2025, False,
     "Three treatment rooms, a sterilisation area and a calm waiting lounge with easy-clean finishes."),
    ("renovation", "home", "Thirty-year-old home, fully renovated", "Sample location", 2100, "10 cents", 2, 6, 2025, True,
     "New roof, rewiring, re-plumbing and a reworked ground floor plan with an open kitchen."),
    ("renovation", "commercial", "Showroom facade and interior rebuild", "Sample location", 3000, "", 2, 4, 2024, False,
     "A dated showroom given a new glass facade, mezzanine and lighting, completed while the upper floor stayed open."),
]

PALETTES = {
    "construction": [(214, 221, 224), (31, 42, 46), (232, 185, 49)],
    "interior": [(236, 228, 214), (122, 78, 45), (232, 185, 49)],
    "renovation": [(220, 228, 222), (77, 107, 92), (232, 185, 49)],
}


def _image(kind, seed, variant="normal", size=(1200, 900)):
    """Draw a simple placeholder illustration so cards don't look empty."""
    from PIL import Image, ImageDraw

    rnd = random.Random(seed)
    w, h = size
    bg, ink, accent = PALETTES[kind]
    if variant == "before":
        bg, ink = (196, 192, 184), (110, 104, 96)
    img = Image.new("RGB", size, bg)
    d = ImageDraw.Draw(img)
    for y in range(h):  # soft vertical gradient
        t = y / h
        c = tuple(int(bg[i] * (1 - t * 0.18)) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)

    ground = int(h * 0.78)
    d.rectangle([0, ground, w, h], fill=tuple(int(v * 0.8) for v in bg))

    if kind == "interior":
        d.rectangle([0, int(h * .7), w, h], fill=(198, 170, 130))
        sx = rnd.randint(120, 360)
        d.rectangle([sx, int(h * .52), sx + 520, int(h * .72)], fill=ink)
        d.rectangle([sx + 20, int(h * .46), sx + 500, int(h * .56)], fill=tuple(min(255, v + 40) for v in ink))
        lx = sx + 640
        d.line([(lx, 0), (lx, int(h * .3))], fill=(40, 40, 40), width=3)
        d.ellipse([lx - 50, int(h * .3), lx + 50, int(h * .38)], fill=accent)
        d.rectangle([int(w * .08), int(h * .14), int(w * .3), int(h * .42)], outline=ink, width=8)
        d.rectangle([w - 160, int(h * .45), w - 120, int(h * .7)], fill=(77, 107, 92))
    else:
        floors = rnd.choice([2, 3]) if kind == "construction" else 2
        bw = rnd.randint(int(w * .5), int(w * .68))
        bx = (w - bw) // 2
        fh = int(h * .2)
        top = ground - fh * floors
        body = (248, 248, 246) if variant != "before" else (170, 164, 154)
        d.rectangle([bx, top, bx + bw, ground], fill=body, outline=ink, width=6)
        for f in range(floors):
            y0 = top + f * fh
            d.line([(bx - 20, y0), (bx + bw + 20, y0)], fill=ink, width=10)
            for k in range(4):
                wx = bx + 40 + k * (bw - 80) // 4
                win_fill = accent if (variant != "before" and rnd.random() > .4) else (90, 100, 104)
                d.rectangle([wx, y0 + 40, wx + (bw - 80) // 4 - 30, y0 + fh - 40], fill=win_fill, outline=ink, width=4)
        d.polygon([(bx + bw * .45, top), (bx + bw * .75, top - 110), (bx + bw + 30, top)], fill=tuple(int(v * .9) for v in ink))
        d.rectangle([bx + bw // 2 - 40, ground - 150, bx + bw // 2 + 40, ground], fill=(122, 78, 45))
        if variant == "before":
            for _ in range(6):
                x, y = rnd.randint(bx, bx + bw), rnd.randint(top, ground)
                d.line([(x, y), (x + rnd.randint(-40, 40), y + rnd.randint(20, 70))], fill=(80, 74, 68), width=3)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = "Create starter content and sample projects for the D4 Interiors site."

    def add_arguments(self, parser):
        parser.add_argument("--no-projects", action="store_true", help="Skip sample projects.")
        parser.add_argument("--reset", action="store_true", help="Delete existing projects before seeding.")

    def handle(self, *args, **opts):
        s = SiteSettings.load()
        if not s.phone:
            s.phone = "+91 98765 43210"
            s.whatsapp_number = "919876543210"
            s.email = "hello@d4interiors.example"
            s.address = "Replace this with your office address\nin Admin → Site settings"
            s.save()
        self.stdout.write("Site settings ready (placeholder contact details, edit them in the admin).")

        for data in SERVICES:
            Service.objects.update_or_create(kind=data["kind"], defaults=data)
        self.stdout.write(f"{len(SERVICES)} services.")

        if not ProcessStep.objects.exists():
            for i, (title, desc, dur) in enumerate(STEPS, 1):
                ProcessStep.objects.create(order=i, title=title, description=desc, duration_hint=dur)
        self.stdout.write(f"{ProcessStep.objects.count()} process stages.")

        if not FAQ.objects.exists():
            for i, (q, a) in enumerate(FAQS, 1):
                FAQ.objects.create(order=i, question=q, answer=a)
        self.stdout.write(f"{FAQ.objects.count()} FAQs.")

        for kind, rows in RATES.items():
            for tier, lo, hi, note in rows:
                EstimatorRate.objects.get_or_create(
                    kind=kind, tier=tier, defaults={"rate_min": lo, "rate_max": hi, "tier_note": note}
                )
        self.stdout.write("Estimator rates (sample figures, review them in the admin).")

        if opts["no_projects"]:
            return
        if opts["reset"]:
            Project.objects.all().delete()
        if Project.objects.exists():
            self.stdout.write("Projects already exist, skipping sample projects.")
            return

        for i, (cat, btype, title, loc, area, plot, floors, months, year, featured, summary) in enumerate(PROJECTS):
            p = Project(
                title=title, category=cat, building_type=btype, location=loc, area_sqft=area, plot_size=plot,
                floors=floors, duration_months=months, year=year, is_featured=featured, summary=summary, order=i,
                description=summary + "\n\nThis is a sample project. Replace it with your own work in the admin.",
                scope="Site survey\nDesign and drawings\nExecution and supervision\nHandover",
            )
            p.cover_image.save(f"sample-{i}.jpg", _image(cat, i), save=False)
            if cat == "renovation":
                p.before_image.save(f"sample-{i}-before.jpg", _image(cat, i, "before"), save=False)
                p.after_image.save(f"sample-{i}-after.jpg", _image(cat, i), save=False)
            p.save()
            for g in range(3):
                im =ProjectImage(project=p, caption=f"Sample photo {g + 1}", order=g)
                im.image.save(f"sample-{i}-{g}.jpg", _image(cat, i * 10 + g + 1), save=True)
        self.stdout.write(self.style.SUCCESS(f"{len(PROJECTS)} sample projects with photos."))
