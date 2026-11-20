# D4 Interiors website

The website and admin panel for **D4 Interiors**, a firm of builders, interior designers, renovators and turnkey contractors. It is built with Django, with no frontend framework: plain HTML templates, one CSS file and one small JavaScript file.

## What's on the site

| Page | What it does |
| --- | --- |
| **Home** (`/`) | An animated drawing in the hero builds a home stage by stage, from plot survey through foundation, structure and interiors to key handover. Below it: the services, recent work, the plot-to-keys process timeline (it fills in as you scroll), a link to the cost estimator, testimonials and FAQs. |
| **Services** (`/services/`) | Turnkey construction, interior design, and renovation and reconstruction, each with its own detail page showing what's included, indicative rates and related projects. |
| **Projects** (`/projects/`) | The portfolio, filterable by service (full builds, interiors, renovations). Each project has a spec sheet, a photo gallery with a full-screen viewer and, for renovations, a before-and-after slider you drag. |
| **Cost estimator** (`/cost-estimator/`) | Visitors choose a service, area and finish level and get a live price range in lakh or crore. "Get an exact quote" carries their choices into the quote form. |
| **Get a quote** (`/get-a-quote/`) | A three-step form covering the project, the plot (location, size, built-up area, floors, budget, timeline, approved plan, file upload for a plot sketch or plan) and contact details. |
| **Contact** (`/contact/`) | A short message form, contact details, a Google map and FAQs. |
| **About** (`/about/`) | The company story, track record and how the team works. |

There is also a floating WhatsApp button, click-to-call phone links, SEO tags, `sitemap.xml`, `robots.txt` and a custom 404 page. The layout works on mobile, keyboard navigation is supported, and animation is turned off for visitors whose device is set to reduce motion.

## Admin panel (`/admin/`)

- **Dashboard:** new enquiries to answer, follow-ups due, enquiries this week and month, the enquiry pipeline by status, the latest enquiries and portfolio counts by service.
- **Enquiries:** every quote request, contact message and estimator lead in one list. You can filter by status, service, building type, budget, timeline and follow-up date. Set a status (New → Contacted → Site visit planned → Quote sent → Won / Lost), add internal notes and a follow-up date, open uploaded plot files, and **download selected enquiries as a spreadsheet (CSV)**.
- **Projects:** add previous work with a cover photo, a gallery (upload several photos inline), before and after photos, and facts such as area, plot size, floors, duration and year. Projects can be published or hidden, featured on the home page, and ordered.
- **Website content:** services, process stages, FAQs, testimonials, cost-estimator rates and **Site settings** (phone, WhatsApp, email, address, map, social links, home-page figures and the About text).

New enquiries can also be emailed to you (see *Going live*).

## Run it on your computer

You need Python 3.10 or newer.

```bash
git clone https://github.com/jincyrajeevan0811/D4-interior.git
cd D4-interior
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_demo         # optional: sample services, FAQs, rates and 9 sample projects
python manage.py createsuperuser   # your admin login
python manage.py runserver
```

Open http://127.0.0.1:8000 for the site and http://127.0.0.1:8000/admin/ for the admin.

Run the tests with `python manage.py test`.

## Before you launch: replace the sample content

`seed_demo` fills the site so you can see every page working. Before going live, in the admin:

1. **Site settings:** enter your real phone number, WhatsApp number, email, address and Google Maps embed link. Fill in the home-page figures (years, projects, square feet, cities) only with numbers you can stand behind. Any figure left at 0 is hidden.
2. **Projects:** delete the sample projects (they are titled generically and say "Sample location") and add your real work with real photos.
3. **Estimator rates:** the seeded per-square-foot rates are placeholders. Set them to your own pricing.
4. **Testimonials:** none are seeded. Add only real feedback from clients who agreed to be quoted. The section stays hidden until you add one.
5. **Services, process stages and FAQs:** edit the wording to match how you work.

The four "How we work with you" points on the About page live in `templates/core/about.html`.

## Going live

1. Copy `.env.example` to `.env` and fill it in. At a minimum set `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False` and `DJANGO_ALLOWED_HOSTS`.
2. To receive an email for every new enquiry, set `INQUIRY_NOTIFY_EMAILS` and the `EMAIL_*` settings. For Gmail, use an app password.
3. Run:
   ```bash
   python manage.py migrate
   python manage.py collectstatic --noinput
   gunicorn d4site.wsgi
   ```
4. Uploaded photos and files are stored in `media/`. Point your web server at that folder for `/media/`, or set `DJANGO_SERVE_MEDIA=True` on simple hosting.

The project uses SQLite, which suits a site of this size. Back up `db.sqlite3` and `media/` regularly. PythonAnywhere, Render, Railway and any VPS can all run it.

## Project layout

```
d4site/        settings and URLs
core/          home, services, about, estimator, site settings, FAQs, testimonials, admin dashboard
portfolio/     projects and their photos
inquiries/     quote and contact forms, enquiry admin with CSV export and email alerts
templates/     page templates (base.html holds the header and footer)
static/css/    site.css (all site styles) and admin.css (admin branding)
static/js/     site.js (hero animation, filters, slider, gallery, multi-step form, estimator)
```

### Design notes

The look borrows from a builder's own drawings. The palette is slate ink `#1F2A2E`, concrete `#E4E3DF`, plaster white `#F8F8F6`, teak `#7A4E2D` for buttons and surveyor-tape yellow `#E8B931`, which is used for dimension lines (each project card shows its built-up area as one). The typeface is Archivo; headings use its wide width. All colours are CSS variables at the top of `static/css/site.css`.
