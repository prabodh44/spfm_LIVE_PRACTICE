from django import forms

from .models import ContactMessage, QuoteRequest


class QuoteRequestForm(forms.ModelForm):
    class Meta:
        model = QuoteRequest
        fields = ["name", "company_name", "email", "phone", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "field-input", "placeholder": "Your name"}
            ),
            "company_name": forms.TextInput(
                attrs={"class": "field-input", "placeholder": "Company name (optional)"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "field-input", "placeholder": "you@example.com"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "field-input", "placeholder": "04XX XXX XXX"}
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "field-input",
                    "placeholder": "Tell us a little about the job",
                    "rows": 3,
                }
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        email = cleaned_data.get("email")
        if not phone and not email:
            msg = "Please provide a phone number or an email address so we can reach you."
            self.add_error("phone", msg)
            self.add_error("email", msg)
        return cleaned_data


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "field-input", "placeholder": "Your name"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "field-input", "placeholder": "you@example.com"}
            ),
            "phone": forms.TextInput(
                attrs={"class": "field-input", "placeholder": "04XX XXX XXX (optional)"}
            ),
            "message": forms.Textarea(
                attrs={"class": "field-input", "placeholder": "How can we help?", "rows": 4}
            ),
        }

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        email = cleaned_data.get("email")
        if not phone and not email:
            msg = "Please provide a phone number or an email address so we can reach you."
            self.add_error("phone", msg)
            self.add_error("email", msg)
        return cleaned_data
