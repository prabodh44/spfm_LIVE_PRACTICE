# SP Facilities Management — Website

A Django website for SP Facilities Management: Home, About Us, Services (7
categories + individual detail pages), Service Areas, Our Work (gallery),
Contact, and a site-wide Free Quote form.

This is a **Full CMS** build — every piece of text and every image on the
public site (services, sub-services, page copy, gallery photos, service
areas, testimonials, trust badges, and all sitewide contact details) is
editable from the Django admin. No code changes are needed to update
content.

Every quote/contact submission is saved to the database (visible in the
Django admin under **Leads**) and triggers an email notification to the
business owner, plus a confirmation email back to the visitor. SMS
notification via Twilio is supported and optional. There's intentionally no
public-facing leads dashboard — leads are only visible in `/admin/`.

---

## 1. Requirements

- Python 3.11+ (3.12 recommended)
- pip

## 2. Local setup

```bash
# 1. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy the environment file and edit as needed
cp .env.example .env

# 4. Run migrations
python manage.py migrate

# 5. Seed sample services, service areas, testimonials, trust badges and
#    gallery placeholders — gives you a fully populated site to start from
python manage.py seed_sample_data

# 6. Create an admin login
python manage.py createsuperuser

# 7. Run the dev server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** for the site and
**http://127.0.0.1:8000/admin/** to manage everything else.

In development, new quote/contact submissions print their notification
emails straight to your terminal (no real email setup needed) so you can
see the flow working immediately.

## 3. Project structure

```
spfm/
├── manage.py
├── requirements.txt
├── .env.example              # copy to .env and fill in real values
├── spfm/                      # project settings
│   ├── settings.py
│   ├── urls.py
├── core/                      # the main app
│   ├── models.py              # every editable content type — see below
│   ├── forms.py                # QuoteRequestForm, ContactForm
│   ├── views.py                # all page views + form handling
│   ├── notifications.py        # email + SMS notification logic
│   ├── admin.py                 # admin site configuration
│   ├── management/commands/seed_sample_data.py
│   └── templates/core/         # page templates
├── templates/base.html         # shared header/nav/footer/quote modal
├── static/                     # css, js, brand images
└── media/                       # uploaded photos (via admin)
```

## 4. What's editable in the admin, and where

Everything below is a Django admin model — no code changes needed for any
of it:

| Admin section | Controls |
|---|---|
| **Leads → Quote Requests / Contact Messages** | Every form submission. Flagged automatically if the owner notification email failed to send. |
| **Services** | The 7 service categories: name, slug, icon, summary, and their sub-service bullet points (edit inline on the same page). Add, edit, deactivate, or delete services freely — the Home, Services, Service Areas–adjacent, and gallery filter lists all update automatically. |
| **Gallery Images** | "Our Work" photos — title, which service it belongs to, the image itself (auto-resized on upload), and alt text. |
| **Service Areas** | Suburbs + region groupings shown on the Service Areas page and the homepage. |
| **Testimonials** | Homepage client quotes. |
| **Trust Badges** | The small credibility lines shown in the homepage trust strip and the footer. |
| **Site Settings** | Sitewide brand name, tagline, phone, email, address, office hours, map embed, footer copy — changes apply instantly across every page (header/footer/contact info). |
| **Home / About / Services / Service Areas / Our Work / Contact Page Content** | Every heading, intro paragraph, and call-to-action on each page, plus an SEO title + meta description per page. |
| **Home Page — Value Points / Stats**, **About Page — Value Cards / Stats** | The small numbered value list and animated stat counters on the homepage, and the icon cards + stat row on the About page. |

The **Site Settings**, and each **Page Content** admin entry, are
"singletons" — there's only ever one row, so clicking into that admin
section takes you straight to the edit form instead of a confusing list.

## 5. Turning on real email notifications

By default (dev), notification emails just print to the console. To send
real emails:

1. In `.env`, set `DJANGO_EMAIL_BACKEND=smtp`.
2. Fill in `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` for your
   provider (Gmail app password, Zoho, SendGrid, AWS SES, etc — all work the
   same way with SMTP).
3. Set `OWNER_NOTIFICATION_EMAIL` to the inbox that should receive new leads.

If a notification email genuinely fails to send, the submission is still
saved to the database and is flagged with `email_send_failed` in the admin
so it can be followed up manually — nothing is silently lost.

## 6. Notes on how the quote form works

- Fields are: **Name, Company Name (optional), Email, Phone, Message**.
  Either a phone number or an email is required (not both) so the business
  can always reach the person back.
- The quote form appears in three places (the header/footer modal, an
  inline panel on each service's detail page, and an inline "work order"
  panel on the homepage) — all three save to the same `QuoteRequest` model.
- If a submission fails validation, the page re-renders with everything the
  visitor typed still filled in — nothing is lost — and the relevant quote
  panel (modal or inline) reopens automatically to show the error.
- On a successful submission, the page redirects with a success message and
  clears the form (there's nothing left to preserve at that point).
