from django.core.exceptions import ValidationError
from django.db import models

try:
    from PIL import Image
except ImportError:  # Pillow should always be installed, but don't hard-crash if not.
    Image = None


# ---------------------------------------------------------------------------
# Shared choices
# ---------------------------------------------------------------------------

ICON_CHOICES = [
    ("residential", "Residential (house icon)"),
    ("commercial", "Commercial (building icon)"),
    ("industrial", "Building & Industrial (factory icon)"),
    ("hospitality", "Hospitality & Kitchen (utensils icon)"),
    ("specialised", "Specialised (sparkles icon)"),
    ("aged_care", "Aged Care (heart icon)"),
    ("outdoor", "Outdoor (leaf icon)"),
    ("other", "Other (checkmark icon)"),
]


# ---------------------------------------------------------------------------
# Image resizing helper (US-7.7 — uploads are automatically optimised)
# ---------------------------------------------------------------------------

def resize_image_field(image_field_file, max_width=1600, max_height=1600, quality=85):
    """Downscale an uploaded image in place if it's larger than the max
    dimensions, and re-save it as an optimised JPEG/PNG. Safe to call on
    any ImageField after save() — silently does nothing if Pillow can't
    read the file for any reason.
    """
    if not image_field_file or Image is None:
        return
    try:
        image_field_file.open()
        img = Image.open(image_field_file)
        img_format = img.format or "JPEG"
        needs_resize = img.width > max_width or img.height > max_height
        if needs_resize:
            img.thumbnail((max_width, max_height), Image.LANCZOS)
        if needs_resize or img_format in ("JPEG", "JPG"):
            from io import BytesIO
            from django.core.files.base import ContentFile

            buffer = BytesIO()
            save_kwargs = {"quality": quality, "optimize": True} if img_format == "JPEG" else {"optimize": True}
            if img.mode in ("RGBA", "P") and img_format == "JPEG":
                img = img.convert("RGB")
            img.save(buffer, format=img_format, **save_kwargs)
            image_field_file.save(
                image_field_file.name.split("/")[-1],
                ContentFile(buffer.getvalue()),
                save=False,
            )
    except Exception:
        # Never let a thumbnailing failure break a content save.
        pass


# ---------------------------------------------------------------------------
# Singleton base (for one-row-per-page content models)
# ---------------------------------------------------------------------------

class SingletonModel(models.Model):
    """A model that only ever has a single row (pk=1). Lets the client edit
    page copy from the admin without needing to pick "which row" to edit.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # Singletons can't be deleted from the admin — only edited.

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


# ---------------------------------------------------------------------------
# Global site settings (header/footer/contact details) — Epic 7.6
# ---------------------------------------------------------------------------

class SiteSettings(SingletonModel):
    site_name = models.CharField(max_length=120, default="SP Facilities Management")
    tagline = models.CharField(max_length=160, default="Clean Spaces. Better Places.")

    phone_display = models.CharField(max_length=40, default="1300 000 000")
    phone_tel = models.CharField(
        max_length=40,
        default="+611300000000",
        help_text="Digits only, with country code, for tel: links, e.g. +611300000000",
    )
    email = models.EmailField(default="info@spfacilitiesmgmt.com.au")
    address = models.CharField(max_length=200, default="Suite 4, 120 Example Street, Sydney NSW 2000")
    office_hours = models.CharField(max_length=120, default="Mon–Sat, 6am–7pm")
    map_embed_src = models.URLField(
        max_length=500,
        default="https://www.google.com/maps?q=Sydney%20NSW&output=embed",
        help_text="The 'src' URL from a Google Maps embed iframe.",
    )

    footer_about_text = models.CharField(
        max_length=220,
        default="Servicing residential, commercial, industrial, hospitality, aged care and outdoor clients across Australia.",
    )
    footer_fine_print = models.CharField(
        max_length=200,
        default="Website content is placeholder copy pending final approval.",
    )

    default_meta_description = models.CharField(
        max_length=300,
        default=(
            "Professional residential, commercial, industrial, hospitality, aged care "
            "and outdoor cleaning services across Australia. Insured, reliable, and "
            "trusted. Get a free quote today."
        ),
        help_text="Used as the fallback meta description on any page without its own.",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"


class TrustBadge(models.Model):
    """A short trust/credibility line. Reused in two spots on the site,
    distinguished by `placement` — the homepage trust strip, and the footer.
    """

    PLACEMENT_CHOICES = [
        ("home_strip", "Homepage trust strip (under the hero)"),
        ("footer", "Footer trust & compliance list"),
    ]

    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES)
    text = models.CharField(max_length=80)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["placement", "order", "id"]
        verbose_name = "Trust Badge"

    def __str__(self):
        return f"{self.text} ({self.get_placement_display()})"


# ---------------------------------------------------------------------------
# Services (Epic 3 + Epic 7.3) — fully CMS-editable, replaces hardcoded list
# ---------------------------------------------------------------------------

class Service(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, help_text="Used in the page URL, e.g. 'residential'.")
    icon_key = models.CharField(
        max_length=20,
        choices=ICON_CHOICES,
        default="other",
        help_text="Controls which built-in icon/illustration is shown for this service.",
    )
    summary = models.CharField(max_length=240, help_text="Short one-line description shown on cards and lists.")
    long_description = models.TextField(
        blank=True,
        help_text="Optional extra paragraph shown on this service's own detail page.",
    )
    is_active = models.BooleanField(default=True, help_text="Untick to hide this service from the site without deleting it.")
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class ServiceFeature(models.Model):
    """One bullet-point sub-service/inclusion under a Service, e.g.
    'End-of-lease / bond-back cleaning' under Residential Cleaning.
    """

    service = models.ForeignKey(Service, related_name="features", on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["service", "order", "id"]
        verbose_name = "Service Feature (sub-service)"

    def __str__(self):
        return f"{self.text} ({self.service.name})"


# ---------------------------------------------------------------------------
# Service Areas (Epic 4 + Epic 7.5)
# ---------------------------------------------------------------------------

class ServiceArea(models.Model):
    """A suburb/region SP Facilities Management covers."""

    region = models.CharField(max_length=120, help_text="e.g. Greater Sydney")
    suburb = models.CharField(max_length=120)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "region", "suburb"]

    def __str__(self):
        return f"{self.suburb} ({self.region})"


# ---------------------------------------------------------------------------
# Testimonials (homepage social proof)
# ---------------------------------------------------------------------------

class Testimonial(models.Model):
    author_name = models.CharField(max_length=120)
    author_role = models.CharField(
        max_length=160, blank=True, help_text="e.g. Office Manager, Bright Point Offices"
    )
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)
    is_featured = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.author_name} ({self.rating}★)"


# ---------------------------------------------------------------------------
# Gallery ("Our Work") — Epic 5 + Epic 7.4
# ---------------------------------------------------------------------------

class GalleryImage(models.Model):
    """A photo of completed work, grouped by service category."""

    title = models.CharField(max_length=160)
    category = models.ForeignKey(
        Service, related_name="gallery_images", on_delete=models.SET_NULL, null=True, blank=True
    )
    image = models.ImageField(upload_to="gallery/", blank=True, null=True)
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Describes the photo for screen readers and SEO. Defaults to the title if left blank.",
    )
    placeholder_note = models.CharField(
        max_length=200,
        blank=True,
        help_text="Shown if no real image has been uploaded yet.",
    )
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image:
            resize_image_field(self.image)
            super().save(update_fields=["image"])

    @property
    def display_alt(self):
        return self.alt_text or self.title


# ---------------------------------------------------------------------------
# Page content — Epic 7.2 (client edits all text/images independently)
# ---------------------------------------------------------------------------

class HomePageContent(SingletonModel):
    hero_eyebrow = models.CharField(max_length=120, default="Est. for the long haul — Australia-wide")
    hero_heading_line1 = models.CharField(max_length=80, default="Clean spaces.")
    hero_heading_emphasis = models.CharField(max_length=80, default="Better")
    hero_heading_line2_suffix = models.CharField(max_length=40, default="places.")
    hero_lede = models.TextField(
        default=(
            "SP Facilities Management keeps homes, workplaces, and job sites running the "
            "way they should — properly maintained, properly documented, no shortcuts. "
            "Request a free quote and we'll write up the job before we start."
        )
    )
    hero_primary_cta_text = models.CharField(max_length=60, default="Request a Quote →")
    hero_secondary_cta_text = models.CharField(max_length=60, default="See the Services")
    hero_rating_text = models.CharField(max_length=20, default="4.9/5")
    hero_job_card_number = models.CharField(max_length=40, default="#SPC-0417")
    hero_job_card_service_line = models.CharField(max_length=120, default="Commercial Clean — Parramatta, NSW")

    services_eyebrow = models.CharField(max_length=80, default="What we handle")
    services_heading = models.CharField(max_length=160, default="Seven services. One crew you can call.")
    services_body = models.TextField(
        default=(
            "Every job leaves with a signed checklist — no guessing what got done. "
            "Pick a service below to see the scope, or tell us the job and we'll match the service."
        )
    )

    about_eyebrow = models.CharField(max_length=80, default="Why SP Facilities Management")
    about_heading = models.CharField(max_length=160, default="Run like a trade, not a call centre.")
    about_body = models.TextField(
        default=(
            "We started as a small crew doing end-of-lease cleans and grew because "
            "clients kept the same people coming back — not a rotating roster of "
            "strangers. Every site gets a documented checklist, a named point of "
            "contact, and a crew that actually knows the building."
        )
    )
    about_image = models.ImageField(upload_to="site/", blank=True, null=True)

    areas_eyebrow = models.CharField(max_length=80, default="Where we work")
    areas_heading = models.CharField(max_length=160, default="Service areas")
    areas_body = models.TextField(
        default="Check your suburb below. Not listed? Ask anyway — we're expanding routes monthly."
    )

    gallery_eyebrow = models.CharField(max_length=80, default="Recent jobs")
    gallery_heading = models.CharField(max_length=160, default="Our work")
    gallery_body = models.TextField(
        default="A running log of finished jobs, filed by service type. Photos below are placeholders until real project photos are supplied."
    )

    testimonials_eyebrow = models.CharField(max_length=80, default="Client notes")
    testimonials_heading = models.CharField(max_length=160, default="What sites tell us")

    contact_eyebrow = models.CharField(max_length=80, default="Get in touch")
    contact_heading = models.CharField(max_length=160, default="Tell us the job.")

    meta_title = models.CharField(max_length=160, blank=True, help_text="Leave blank to use the site default.")
    meta_description = models.CharField(max_length=300, blank=True, help_text="Leave blank to use the site default.")

    class Meta:
        verbose_name = "Home Page Content"
        verbose_name_plural = "Home Page Content"

    def __str__(self):
        return "Home Page Content"


class AboutPageContent(SingletonModel):
    hero_eyebrow = models.CharField(max_length=80, default="Our story")
    hero_heading = models.CharField(max_length=160, default="Built on reliability, one job at a time")
    hero_intro = models.TextField(
        default=(
            "SP Facilities Management started with a simple idea: cleaning should be "
            "dependable, thorough, and easy to book. Years on, that same standard "
            "guides every job we take on — from a single home to a multi-site "
            "commercial contract."
        )
    )

    values_eyebrow = models.CharField(max_length=80, default="What drives us")
    values_heading = models.CharField(max_length=160, default="Our values")

    why_eyebrow = models.CharField(max_length=80, default="Why customers choose us")
    why_heading = models.CharField(max_length=160, default="What makes us different")
    why_body = models.TextField(
        default=(
            "Anyone can send someone with a mop. We send a trained crew with a "
            "checklist built for your exact space — whether that's a single bathroom "
            "or an entire aged care wing — and we follow up to make sure the job met "
            "your standard, not just ours.\n\n"
            "Every booking starts with a free, no-obligation quote, so you know the "
            "price before we ever set foot on site."
        ),
        help_text="Separate paragraphs with a blank line.",
    )

    cta_heading = models.CharField(max_length=160, default="Ready to work with a team you can rely on?")
    cta_body = models.CharField(max_length=200, default="Get a free, no-obligation quote in minutes.")

    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "About Page Content"
        verbose_name_plural = "About Page Content"

    def __str__(self):
        return "About Page Content"


class AboutValueCard(models.Model):
    """The 3 'Professional / Reliable / Trusted'-style cards on the About page."""

    icon_key = models.CharField(max_length=20, choices=ICON_CHOICES, default="sparkles")
    title = models.CharField(max_length=60)
    description = models.CharField(max_length=220)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "About Page — Value Card"

    def __str__(self):
        return self.title


class AboutStat(models.Model):
    """The small stat row on the About page (e.g. '7 SERVICE CATEGORIES')."""

    value = models.CharField(max_length=20)
    label = models.CharField(max_length=60)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "About Page — Stat"

    def __str__(self):
        return f"{self.value} {self.label}"


class HomeValuePoint(models.Model):
    """The numbered 'Reliability / Professionalism / Trust' list on the homepage."""

    title = models.CharField(max_length=60)
    description = models.CharField(max_length=240)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Home Page — Value Point"

    def __str__(self):
        return self.title


class HomeStat(models.Model):
    """The animated stat counters on the homepage (e.g. '500+ Jobs Completed')."""

    target = models.CharField(max_length=20, help_text="e.g. 500+, 100%, 24h")
    label = models.CharField(max_length=60)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Home Page — Stat"

    def __str__(self):
        return f"{self.target} {self.label}"


class ServicesPageContent(SingletonModel):
    hero_eyebrow = models.CharField(max_length=80, default="Full service breakdown")
    hero_heading = models.CharField(max_length=160, default="Cleaning services for every space")
    hero_intro = models.TextField(
        default=(
            "Seven categories, one accountable team. Explore what's included in each "
            "service below, or request a free quote for a custom combination."
        )
    )
    cta_heading = models.CharField(max_length=160, default="Not sure which service you need?")
    cta_body = models.CharField(
        max_length=200, default="Tell us about the space and we'll recommend the right combination — free of charge."
    )

    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Services Page Content"
        verbose_name_plural = "Services Page Content"

    def __str__(self):
        return "Services Page Content"


class ServiceAreasPageContent(SingletonModel):
    hero_eyebrow = models.CharField(max_length=80, default="Where we work")
    hero_heading = models.CharField(max_length=160, default="Service areas across Australia")
    hero_intro = models.TextField(
        default=(
            "We cover metro and surrounding regions nationwide. Don't see your "
            "suburb listed? Ask us anyway — we're always expanding coverage."
        )
    )
    areas_note = models.CharField(
        max_length=200,
        default="Suburb list shown is a sample of coverage — contact us to confirm servicing for your exact address.",
    )
    cta_heading = models.CharField(max_length=160, default="Check if we cover your area")
    cta_body = models.CharField(
        max_length=200, default="Send us your suburb and we'll confirm availability along with your free quote."
    )

    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Service Areas Page Content"
        verbose_name_plural = "Service Areas Page Content"

    def __str__(self):
        return "Service Areas Page Content"


class OurWorkPageContent(SingletonModel):
    hero_eyebrow = models.CharField(max_length=80, default="Proof, not promises")
    hero_heading = models.CharField(max_length=160, default="Our work")
    hero_intro = models.TextField(
        default=(
            "A look at completed jobs across our service categories. Photos below "
            "are placeholders — real project photos will replace these once supplied."
        )
    )
    cta_heading = models.CharField(max_length=160, default="Want results like these?")
    cta_body = models.CharField(max_length=200, default="Get a free, no-obligation quote for your space today.")

    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Our Work Page Content"
        verbose_name_plural = "Our Work Page Content"

    def __str__(self):
        return "Our Work Page Content"


class ContactPageContent(SingletonModel):
    hero_eyebrow = models.CharField(max_length=80, default="We're here to help")
    hero_heading = models.CharField(max_length=160, default="Get in touch")
    hero_intro = models.TextField(
        default="Questions about a service, or ready for a free quote? Reach out however suits you best."
    )
    quote_prompt_text = models.CharField(
        max_length=200,
        default="Prefer a quote instead?",
        help_text="Shown next to a 'Use the quote form' link that opens the quote modal.",
    )

    meta_title = models.CharField(max_length=160, blank=True)
    meta_description = models.CharField(max_length=300, blank=True)

    class Meta:
        verbose_name = "Contact Page Content"
        verbose_name_plural = "Contact Page Content"

    def __str__(self):
        return "Contact Page Content"


# ---------------------------------------------------------------------------
# Leads — Epic 6 (no admin dashboard for browsing, but DB-backed + emailed)
# ---------------------------------------------------------------------------

class QuoteRequest(models.Model):
    """A free quote request submitted from anywhere on the site."""

    name = models.CharField(max_length=120)
    company_name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_actioned = models.BooleanField(default=False)
    email_send_failed = models.BooleanField(
        default=False,
        help_text="Set automatically if the owner notification email failed to send — check this submission manually.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Quote Request"

    def __str__(self):
        return f"{self.name} — {self.created_at:%d %b %Y}"

    def clean(self):
        super().clean()
        if not self.phone and not self.email:
            raise ValidationError("Please provide a phone number or an email address so we can reach you.")


class ContactMessage(models.Model):
    """A general enquiry from the Contact page."""

    name = models.CharField(max_length=120)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    email_send_failed = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Message"

    def __str__(self):
        return f"{self.name} - {self.created_at:%d %b %Y}"

    def clean(self):
        super().clean()
        if not self.phone and not self.email:
            raise ValidationError("Please provide a phone number or an email address so we can reach you.")
