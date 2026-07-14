from .models import SiteSettings, TrustBadge


def site_info(request):
    settings_obj = SiteSettings.get_solo()
    return {
        "SITE_NAME": settings_obj.site_name,
        "SITE_TAGLINE": settings_obj.tagline,
        "BUSINESS_PHONE": settings_obj.phone_display,
        "BUSINESS_PHONE_TEL": settings_obj.phone_tel,
        "BUSINESS_EMAIL": settings_obj.email,
        "BUSINESS_ADDRESS": settings_obj.address,
        "BUSINESS_HOURS": settings_obj.office_hours,
        "BUSINESS_MAP_EMBED_SRC": settings_obj.map_embed_src,
        "SITE_SETTINGS": settings_obj,
        "FOOTER_TRUST_BADGES": TrustBadge.objects.filter(placement="footer"),
    }
