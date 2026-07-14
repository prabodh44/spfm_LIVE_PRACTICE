"""
Admin widget for cropping images at upload time (US: "add a feature to
crop the uploaded image in the admin panel").

Design notes
------------
* Cropping happens entirely client-side in the browser (see
  static/admin/js/image_crop.js). When staff pick a new file in a field
  using this widget, a modal opens with a draggable crop box and a small
  set of aspect-ratio presets. On "Apply crop", the JS draws the chosen
  region onto a canvas and swaps the cropped result into the file input
  *before* the form is submitted — so the server just receives an
  already-cropped image and no view/model changes were required.
* This only fires when a *new* file is selected. Opening an existing,
  already-saved row and leaving the image untouched behaves exactly like
  a normal ClearableFileInput — there is no "re-crop this saved image"
  step, by design.
* The widget is reusable: pass a different `ratios` list per field so the
  presets offered match how that image is actually displayed on the site.
"""

import json

from django import forms


class CroppableImageWidget(forms.ClearableFileInput):
    """A ClearableFileInput that offers an in-browser crop step on new uploads.

    Args:
        ratios: list of (label, ratio) tuples, where `ratio` is a float
            (width / height) for a fixed-aspect preset, or None for a
            free-form crop option. The first entry is selected by default
            when the crop modal opens.
    """

    class Media:
        css = {"all": ("admin/css/image_crop.css",)}
        js = ("admin/js/image_crop.js",)

    def __init__(self, ratios=None, attrs=None, **kwargs):
        self.ratios = ratios or [("Free", None)]
        base_attrs = {"class": "crop-enabled-input"}
        if attrs:
            base_attrs.update(attrs)
        super().__init__(attrs=base_attrs, **kwargs)

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        ratio_payload = [{"label": label, "ratio": ratio} for label, ratio in self.ratios]
        context["widget"]["attrs"]["data-crop-ratios"] = json.dumps(ratio_payload)
        return context
