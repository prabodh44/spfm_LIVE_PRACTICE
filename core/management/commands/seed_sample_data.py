from django.core.management.base import BaseCommand

from core.models import (
    AboutStat,
    AboutValueCard,
    GalleryImage,
    HomeStat,
    HomeValuePoint,
    Service,
    ServiceArea,
    ServiceFeature,
    Testimonial,
    TrustBadge,
)

SERVICES = [
    {
        "slug": "residential",
        "name": "Residential Cleaning",
        "icon_key": "residential",
        "summary": "Regular, one-off, and end-of-lease cleans that keep your home spotless.",
        "features": [
            "Weekly, fortnightly or one-off house cleans",
            "End-of-lease / bond-back cleaning",
            "Move-in / move-out deep cleans",
            "Spring cleaning and seasonal refreshes",
        ],
    },
    {
        "slug": "commercial",
        "name": "Commercial Cleaning",
        "icon_key": "commercial",
        "summary": "Reliable office and retail cleaning that keeps your business presentable.",
        "features": [
            "Daily, weekly or after-hours office cleaning",
            "Retail store and shopfront cleaning",
            "Strata and common-area cleaning",
            "Washroom and kitchenette servicing",
        ],
    },
    {
        "slug": "industrial",
        "name": "Building & Industrial Cleaning",
        "icon_key": "industrial",
        "summary": "Heavy-duty cleaning for warehouses, factories, and construction sites.",
        "features": [
            "Warehouse and factory floor cleaning",
            "Post-construction and builder's cleans",
            "High-level and machinery-area cleaning",
            "Waste removal and site tidy-ups",
        ],
    },
    {
        "slug": "hospitality",
        "name": "Hospitality & Kitchen Cleaning",
        "icon_key": "hospitality",
        "summary": "Compliant, food-safe cleaning for cafes, restaurants, and commercial kitchens.",
        "features": [
            "Commercial kitchen deep cleans",
            "Range hood and exhaust degreasing",
            "Dining area and front-of-house cleaning",
            "Health-code compliant sanitising",
        ],
    },
    {
        "slug": "specialised",
        "name": "Specialised Cleaning Services",
        "icon_key": "specialised",
        "summary": "Carpet, floor, window, and high-pressure cleaning for a deeper clean.",
        "features": [
            "Carpet and upholstery steam cleaning",
            "Hard floor stripping, sealing and polishing",
            "Internal and external window cleaning",
            "High-pressure washing for driveways and facades",
        ],
    },
    {
        "slug": "aged-care",
        "name": "Aged Care Cleaning",
        "icon_key": "aged_care",
        "summary": "Gentle, hygienic cleaning for aged care facilities and retirement living.",
        "features": [
            "Infection-control compliant cleaning",
            "Resident room and common-area servicing",
            "Scheduled cleaning around care routines",
            "Trained, police-checked cleaning staff",
        ],
    },
    {
        "slug": "outdoor",
        "name": "Outdoor Services",
        "icon_key": "outdoor",
        "summary": "Exterior cleaning that keeps grounds and outdoor areas looking their best.",
        "features": [
            "Driveway, path and paving cleaning",
            "Building exterior and gutter cleaning",
            "Car park and loading-dock cleaning",
            "Outdoor furniture and signage cleaning",
        ],
    },
]

SERVICE_AREAS = {
    "Greater Sydney": ["Parramatta", "Liverpool", "Chatswood", "Bondi", "Penrith"],
    "Greater Melbourne": ["CBD", "St Kilda", "Dandenong", "Ringwood", "Werribee"],
    "Greater Brisbane": ["CBD", "Chermside", "Ipswich", "Logan", "Redcliffe"],
    "Perth Metro": ["CBD", "Joondalup", "Fremantle", "Rockingham"],
}

TESTIMONIALS = [
    {
        "author_name": "Rachel M.",
        "author_role": "Homeowner, Parramatta NSW",
        "quote": "Our end-of-lease clean was spotless — got our full bond back without a single question.",
        "rating": 5,
    },
    {
        "author_name": "David T.",
        "author_role": "Office Manager, Bright Point Offices",
        "quote": "Reliable, on time, every week. Our office has never looked better.",
        "rating": 5,
    },
    {
        "author_name": "Aged Care Facility Manager",
        "author_role": "Melbourne VIC",
        "quote": "Professional, careful and always compliant with our infection-control standards.",
        "rating": 5,
    },
]

TRUST_STRIP = ["Fully Insured", "Vetted Crews", "Same-Week Quotes", "Site-Specific Checklists"]
FOOTER_TRUST = ["Fully insured", "Police-checked staff", "Satisfaction guaranteed"]

HOME_VALUES = [
    ("Reliability", "If we're booked in, we show up — and if something changes, you hear it from us first."),
    ("Professionalism", "Uniformed, insured crews who treat your site like it's the only one on the books."),
    ("Trust", "Signed checklists on every job, so nothing's left to memory."),
]

HOME_STATS = [("500+", "Jobs Completed"), ("100%", "Insured Crews"), ("24h", "Reply Time")]

ABOUT_VALUE_CARDS = [
    ("sparkles", "Professional", "Trained crews, consistent checklists, and a standard that doesn't slip between visits."),
    ("residential", "Reliable", "We turn up when we say we will — no chasing, no guesswork, no last-minute cancellations."),
    ("aged_care", "Trusted", "Fully insured and police-checked staff, so you can hand over the keys with confidence."),
]

ABOUT_STATS = [("7", "SERVICE CATEGORIES"), ("100%", "INSURED CREWS"), ("AU", "WIDE COVERAGE"), ("24H", "TYPICAL REPLY TIME")]


class Command(BaseCommand):
    help = "Seeds sample services, service areas, testimonials, trust badges, and gallery placeholders."

    def handle(self, *args, **options):
        self._seed_services()
        self._seed_service_areas()
        self._seed_testimonials()
        self._seed_trust_badges()
        self._seed_home_values_and_stats()
        self._seed_about_values_and_stats()
        self._seed_gallery_placeholders()
        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully."))

    def _seed_services(self):
        for order, data in enumerate(SERVICES):
            service, _ = Service.objects.update_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "icon_key": data["icon_key"],
                    "summary": data["summary"],
                    "order": order,
                    "is_active": True,
                },
            )
            if not service.features.exists():
                for f_order, text in enumerate(data["features"]):
                    ServiceFeature.objects.create(service=service, text=text, order=f_order)
        self.stdout.write("  Services + sub-services seeded.")

    def _seed_service_areas(self):
        if ServiceArea.objects.exists():
            return
        order = 0
        for region, suburbs in SERVICE_AREAS.items():
            for suburb in suburbs:
                ServiceArea.objects.create(region=region, suburb=suburb, order=order)
                order += 1
        self.stdout.write("  Service areas seeded.")

    def _seed_testimonials(self):
        if Testimonial.objects.exists():
            return
        for order, t in enumerate(TESTIMONIALS):
            Testimonial.objects.create(order=order, **t)
        self.stdout.write("  Testimonials seeded.")

    def _seed_trust_badges(self):
        if not TrustBadge.objects.filter(placement="home_strip").exists():
            for order, text in enumerate(TRUST_STRIP):
                TrustBadge.objects.create(placement="home_strip", text=text, order=order)
        if not TrustBadge.objects.filter(placement="footer").exists():
            for order, text in enumerate(FOOTER_TRUST):
                TrustBadge.objects.create(placement="footer", text=text, order=order)
        self.stdout.write("  Trust badges seeded.")

    def _seed_home_values_and_stats(self):
        if not HomeValuePoint.objects.exists():
            for order, (title, desc) in enumerate(HOME_VALUES):
                HomeValuePoint.objects.create(title=title, description=desc, order=order)
        if not HomeStat.objects.exists():
            for order, (target, label) in enumerate(HOME_STATS):
                HomeStat.objects.create(target=target, label=label, order=order)
        self.stdout.write("  Home page value points + stats seeded.")

    def _seed_about_values_and_stats(self):
        if not AboutValueCard.objects.exists():
            for order, (icon_key, title, desc) in enumerate(ABOUT_VALUE_CARDS):
                AboutValueCard.objects.create(icon_key=icon_key, title=title, description=desc, order=order)
        if not AboutStat.objects.exists():
            for order, (value, label) in enumerate(ABOUT_STATS):
                AboutStat.objects.create(value=value, label=label, order=order)
        self.stdout.write("  About page value cards + stats seeded.")

    def _seed_gallery_placeholders(self):
        if GalleryImage.objects.exists():
            return
        order = 0
        for service in Service.objects.all():
            for i in range(1, 3):
                GalleryImage.objects.create(
                    title=f"{service.name} — job {i}",
                    category=service,
                    order=order,
                )
                order += 1
        self.stdout.write("  Gallery placeholders seeded (upload real photos in admin to replace them).")
