from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactForm, QuoteRequestForm
from .models import (
    AboutPageContent,
    AboutStat,
    AboutValueCard,
    ContactPageContent,
    GalleryImage,
    HomePageContent,
    HomeStat,
    HomeValuePoint,
    OurWorkPageContent,
    Service,
    ServiceArea,
    ServiceAreasPageContent,
    ServicesPageContent,
    Testimonial,
    TrustBadge,
)
from .notifications import notify_new_contact_message, notify_new_quote_request


# ---------------------------------------------------------------------------
# Small shared helpers
# ---------------------------------------------------------------------------

def _handle_quote_post(request):
    """Processes a submitted quote form (from the modal, the homepage
    work-order panel, or a service detail page's inline panel).

    Returns a tuple (quote_form, open_quote_modal, redirected_response).
    If `redirected_response` is not None, the caller should return it
    immediately (successful submission — safe to redirect since there's
    no data left to preserve). Otherwise the caller should keep rendering
    its own template with `quote_form` (bound, with errors) and
    `open_quote_modal` in the context, so entered data isn't lost.
    """
    quote_form = QuoteRequestForm(request.POST)
    if quote_form.is_valid():
        quote = quote_form.save()
        notify_new_quote_request(quote)
        messages.success(
            request,
            "Thanks! Your free quote request has been sent — we'll be in touch shortly.",
        )
        return quote_form, False, redirect(request.path)

    messages.error(request, "Please check the highlighted fields and submit the quote form again.")
    open_quote_modal = request.POST.get("quote_source") == "modal"
    return quote_form, open_quote_modal, None


def _flat_service_areas(limit=None):
    areas = ServiceArea.objects.all()
    flat = [f"{a.suburb}, {a.region.replace('Greater ', '')}" for a in areas]
    return flat[:limit] if limit else flat


def _grouped_service_areas():
    grouped = {}
    for area in ServiceArea.objects.all():
        grouped.setdefault(area.region, []).append(area.suburb)
    return grouped


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------

def home(request):
    quote_form = QuoteRequestForm()
    open_quote_modal = False

    if request.method == "POST" and request.POST.get("form_id") == "quote_form":
        quote_form, open_quote_modal, redirected = _handle_quote_post(request)
        if redirected:
            return redirected

    content = HomePageContent.get_solo()
    gallery = GalleryImage.objects.select_related("category")[:6]

    context = {
        "content": content,
        "services": Service.objects.filter(is_active=True),
        "testimonials": Testimonial.objects.filter(is_featured=True)[:3],
        "quote_form": quote_form,
        "open_quote_modal": open_quote_modal,
        "flat_areas": _flat_service_areas(limit=12),
        "gallery_preview": gallery,
        "trust_strip_badges": TrustBadge.objects.filter(placement="home_strip"),
        "home_values": HomeValuePoint.objects.all(),
        "home_stats": HomeStat.objects.all(),
    }
    return render(request, "core/home.html", context)


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------

def about(request):
    quote_form = QuoteRequestForm()
    open_quote_modal = False

    if request.method == "POST" and request.POST.get("form_id") == "quote_form":
        quote_form, open_quote_modal, redirected = _handle_quote_post(request)
        if redirected:
            return redirected

    context = {
        "content": AboutPageContent.get_solo(),
        "value_cards": AboutValueCard.objects.all(),
        "stats": AboutStat.objects.all(),
        "quote_form": quote_form,
        "open_quote_modal": open_quote_modal,
    }
    return render(request, "core/about.html", context)


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------

def services(request):
    quote_form = QuoteRequestForm()
    open_quote_modal = False

    if request.method == "POST" and request.POST.get("form_id") == "quote_form":
        quote_form, open_quote_modal, redirected = _handle_quote_post(request)
        if redirected:
            return redirected

    context = {
        "content": ServicesPageContent.get_solo(),
        "services": Service.objects.filter(is_active=True),
        "quote_form": quote_form,
        "open_quote_modal": open_quote_modal,
    }
    return render(request, "core/services.html", context)


def service_detail(request, slug):
    service = Service.objects.filter(slug=slug, is_active=True).prefetch_related("features").first()

    quote_form = QuoteRequestForm()

    if request.method == "POST" and request.POST.get("form_id") == "quote_form":
        quote_form, _open_modal_unused, redirected = _handle_quote_post(request)
        if redirected:
            return redirected
        # The quote form on this page is shown inline (not in the modal),
        # so validation errors are already visible right there — no need
        # to also pop the header modal open.

    if not service:
        return redirect("services")

    context = {
        "service": service,
        "quote_form": quote_form,
        "open_quote_modal": False,
    }
    return render(request, "core/service_detail.html", context)


# ---------------------------------------------------------------------------
# Service Areas
# ---------------------------------------------------------------------------

def service_areas(request):
    quote_form = QuoteRequestForm()
    open_quote_modal = False

    if request.method == "POST" and request.POST.get("form_id") == "quote_form":
        quote_form, open_quote_modal, redirected = _handle_quote_post(request)
        if redirected:
            return redirected

    context = {
        "content": ServiceAreasPageContent.get_solo(),
        "grouped_areas": _grouped_service_areas(),
        "quote_form": quote_form,
        "open_quote_modal": open_quote_modal,
    }
    return render(request, "core/service_areas.html", context)


# ---------------------------------------------------------------------------
# Our Work (gallery)
# ---------------------------------------------------------------------------

def our_work(request):
    quote_form = QuoteRequestForm()
    open_quote_modal = False

    if request.method == "POST" and request.POST.get("form_id") == "quote_form":
        quote_form, open_quote_modal, redirected = _handle_quote_post(request)
        if redirected:
            return redirected

    context = {
        "content": OurWorkPageContent.get_solo(),
        "gallery": GalleryImage.objects.select_related("category"),
        "filter_services": Service.objects.filter(is_active=True),
        "quote_form": quote_form,
        "open_quote_modal": open_quote_modal,
    }
    return render(request, "core/our_work.html", context)


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------

def contact(request):
    quote_form = QuoteRequestForm()
    contact_form = ContactForm()
    open_quote_modal = False

    if request.method == "POST" and request.POST.get("form_id") == "contact_form":
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            msg = contact_form.save()
            notify_new_contact_message(msg)
            messages.success(request, "Thanks for reaching out! We'll get back to you shortly.")
            return redirect("contact")
        messages.error(request, "Please check the highlighted fields and send your message again.")

    elif request.method == "POST" and request.POST.get("form_id") == "quote_form":
        quote_form, open_quote_modal, redirected = _handle_quote_post(request)
        if redirected:
            return redirected

    context = {
        "content": ContactPageContent.get_solo(),
        "contact_form": contact_form,
        "quote_form": quote_form,
        "open_quote_modal": open_quote_modal,
    }
    return render(request, "core/contact.html", context)
