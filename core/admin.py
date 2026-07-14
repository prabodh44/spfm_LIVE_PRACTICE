from django import forms
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse

from .widgets import CroppableImageWidget
from .models import (
    AboutPageContent,
    AboutStat,
    AboutValueCard,
    ContactMessage,
    ContactPageContent,
    GalleryImage,
    HomePageContent,
    HomeStat,
    HomeValuePoint,
    OurWorkPageContent,
    QuoteRequest,
    Service,
    ServiceArea,
    ServiceAreasPageContent,
    ServiceFeature,
    ServicesPageContent,
    SiteSettings,
    Testimonial,
    TrustBadge,
)


# ---------------------------------------------------------------------------
# Singleton page-content admin — the client just clicks straight into the
# one page they're editing, no "which row" confusion (US-7.9).
# ---------------------------------------------------------------------------

class SingletonAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.get_solo()
        url_name = f"admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change"
        return redirect(reverse(url_name, args=[obj.pk]))


# ===========================================================================
# 1. LEADS — quote requests & contact messages (Epic 6). No public
#    dashboard by design, but visible/searchable here for manual follow-up.
# ===========================================================================

@admin.register(QuoteRequest)
class QuoteRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "company_name", "phone", "email", "created_at", "is_actioned", "email_send_failed")
    list_filter = ("is_actioned", "email_send_failed")
    search_fields = ("name", "company_name", "email", "phone", "message")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "created_at", "is_read", "email_send_failed")
    list_filter = ("is_read", "email_send_failed")
    search_fields = ("name", "email", "phone", "message")
    readonly_fields = ("created_at",)


# ===========================================================================
# 2. SERVICES — the 7 categories + their sub-services (Epic 3 / US-7.3)
# ===========================================================================

class ServiceFeatureInline(admin.TabularInline):
    model = ServiceFeature
    extra = 1


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "icon_key", "is_active", "order")
    list_editable = ("is_active", "order")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ServiceFeatureInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "icon_key", "is_active", "order")}),
        ("Copy", {"fields": ("summary", "long_description")}),
    )


# ===========================================================================
# 3. GALLERY — "Our Work" photos (Epic 5 / US-7.4)
# ===========================================================================

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = "__all__"
        widgets = {
            "image": CroppableImageWidget(
                ratios=[
                    ("3:2 (for large images)", 3 / 2),
                    ("4:3 (gallery grid)", 4 / 3),
                    ("1:1 (square)", 1 / 1),
                    ("16:9 (wide)", 16 / 9),
                    ("Free", None),
                ]
            ),
        }


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    form = GalleryImageForm
    list_display = ("title", "category", "order", "image")
    list_editable = ("order",)
    list_filter = ("category",)
    fields = ("title", "category", "image", "alt_text", "placeholder_note", "order")


# ===========================================================================
# 4. SERVICE AREAS (Epic 4 / US-7.5)
# ===========================================================================

@admin.register(ServiceArea)
class ServiceAreaAdmin(admin.ModelAdmin):
    list_display = ("suburb", "region", "order")
    list_filter = ("region",)
    list_editable = ("order",)


# ===========================================================================
# 5. TESTIMONIALS (homepage social proof)
# ===========================================================================

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "author_role", "rating", "is_featured", "order")
    list_editable = ("order", "is_featured")


# ===========================================================================
# 6. TRUST BADGES — small credibility lines used on the home trust strip
#    and in the footer (also editable, per the "Full CMS" scope note).
# ===========================================================================

@admin.register(TrustBadge)
class TrustBadgeAdmin(admin.ModelAdmin):
    list_display = ("text", "placement", "order")
    list_filter = ("placement",)
    list_editable = ("order",)


# ===========================================================================
# 7. SITE SETTINGS — sitewide contact details, shown in header/footer
#    everywhere instantly when changed (US-7.6)
# ===========================================================================

@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    fieldsets = (
        ("Brand", {"fields": ("site_name", "tagline")}),
        ("Contact details", {"fields": ("phone_display", "phone_tel", "email", "address", "office_hours", "map_embed_src")}),
        ("Footer copy", {"fields": ("footer_about_text", "footer_fine_print")}),
        ("SEO default", {"fields": ("default_meta_description",)}),
    )


# ===========================================================================
# 8. PAGE CONTENT — every editable text block on each page (US-7.2)
# ===========================================================================

class HomePageContentForm(forms.ModelForm):
    class Meta:
        model = HomePageContent
        fields = "__all__"
        widgets = {
            "about_image": CroppableImageWidget(
                ratios=[
                    ("4:5 (about photo)", 4 / 5),
                    ("1:1 (square)", 1 / 1),
                    ("4:3 (standard)", 4 / 3),
                    ("Free", None),
                ]
            ),
        }


@admin.register(HomePageContent)
class HomePageContentAdmin(SingletonAdmin):
    form = HomePageContentForm
    fieldsets = (
        ("Hero", {
            "fields": (
                "hero_eyebrow", "hero_heading_line1", "hero_heading_emphasis", "hero_heading_line2_suffix",
                "hero_lede", "hero_primary_cta_text", "hero_secondary_cta_text",
                "hero_rating_text", "hero_job_card_number", "hero_job_card_service_line",
            ),
        }),
        ("Services section", {"fields": ("services_eyebrow", "services_heading", "services_body")}),
        ("About teaser section", {"fields": ("about_eyebrow", "about_heading", "about_body", "about_image")}),
        ("Service areas band", {"fields": ("areas_eyebrow", "areas_heading", "areas_body")}),
        ("Gallery section", {"fields": ("gallery_eyebrow", "gallery_heading", "gallery_body")}),
        ("Testimonials section", {"fields": ("testimonials_eyebrow", "testimonials_heading")}),
        ("Contact section", {"fields": ("contact_eyebrow", "contact_heading")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(HomeValuePoint)
class HomeValuePointAdmin(admin.ModelAdmin):
    list_display = ("title", "order")
    list_editable = ("order",)


@admin.register(HomeStat)
class HomeStatAdmin(admin.ModelAdmin):
    list_display = ("target", "label", "order")
    list_editable = ("order",)


@admin.register(AboutPageContent)
class AboutPageContentAdmin(SingletonAdmin):
    fieldsets = (
        ("Hero", {"fields": ("hero_eyebrow", "hero_heading", "hero_intro")}),
        ("Values section heading", {"fields": ("values_eyebrow", "values_heading")}),
        ("'Why us' section", {"fields": ("why_eyebrow", "why_heading", "why_body")}),
        ("Call to action", {"fields": ("cta_heading", "cta_body")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(AboutValueCard)
class AboutValueCardAdmin(admin.ModelAdmin):
    list_display = ("title", "icon_key", "order")
    list_editable = ("order",)


@admin.register(AboutStat)
class AboutStatAdmin(admin.ModelAdmin):
    list_display = ("value", "label", "order")
    list_editable = ("order",)


@admin.register(ServicesPageContent)
class ServicesPageContentAdmin(SingletonAdmin):
    fieldsets = (
        ("Hero", {"fields": ("hero_eyebrow", "hero_heading", "hero_intro")}),
        ("Call to action", {"fields": ("cta_heading", "cta_body")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(ServiceAreasPageContent)
class ServiceAreasPageContentAdmin(SingletonAdmin):
    fieldsets = (
        ("Hero", {"fields": ("hero_eyebrow", "hero_heading", "hero_intro")}),
        ("Areas list", {"fields": ("areas_note",)}),
        ("Call to action", {"fields": ("cta_heading", "cta_body")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(OurWorkPageContent)
class OurWorkPageContentAdmin(SingletonAdmin):
    fieldsets = (
        ("Hero", {"fields": ("hero_eyebrow", "hero_heading", "hero_intro")}),
        ("Call to action", {"fields": ("cta_heading", "cta_body")}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


@admin.register(ContactPageContent)
class ContactPageContentAdmin(SingletonAdmin):
    fieldsets = (
        ("Hero", {"fields": ("hero_eyebrow", "hero_heading", "hero_intro")}),
        ("Quote form prompt", {"fields": ("quote_prompt_text",)}),
        ("SEO", {"fields": ("meta_title", "meta_description")}),
    )


admin.site.site_header = "SP Facilities Management — Content Admin"
admin.site.site_title = "SP Facilities Management Admin"
admin.site.index_title = "Manage your website"
