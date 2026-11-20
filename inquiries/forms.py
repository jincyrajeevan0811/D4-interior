import re

from django import forms

from core.choices import BuildingType, FinishTier, ServiceKind

from .models import Inquiry

PHONE_RE = re.compile(r"^\+?[\d\s\-()]{7,20}$")


class HoneypotMixin(forms.Form):
    """A hidden field that people never see. Bots that fill it are rejected."""

    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Leave this field empty.")
        return ""


def clean_phone_value(value):
    value = (value or "").strip()
    if not PHONE_RE.match(value) or len(re.sub(r"\D", "", value)) < 7:
        raise forms.ValidationError("Enter a phone number with at least 7 digits, e.g. +91 98765 43210.")
    return value


class QuoteForm(HoneypotMixin, forms.ModelForm):
    YES_NO = [("", "Not sure"), ("yes", "Yes"), ("no", "No, we need one")]

    service = forms.ChoiceField(choices=ServiceKind.choices, widget=forms.RadioSelect, label="What do you need?")
    building_type = forms.ChoiceField(
        choices=[("", "Choose a building type")] + list(BuildingType.choices), label="Type of building"
    )
    finish_tier = forms.ChoiceField(
        choices=[("", "Not decided")] + list(FinishTier.choices), required=False, label="Finish level"
    )
    approved_plan = forms.ChoiceField(choices=YES_NO, required=False, label="Do you have an approved building plan?")

    class Meta:
        model = Inquiry
        fields = [
            "service",
            "building_type",
            "finish_tier",
            "plot_location",
            "plot_size",
            "built_up_area",
            "floors",
            "budget",
            "timeline",
            "message",
            "attachment",
            "name",
            "phone",
            "email",
            "preferred_contact",
            "estimate_low",
            "estimate_high",
        ]
        labels = {
            "plot_location": "Where is the plot or site?",
            "plot_size": "Plot size",
            "built_up_area": "Built-up area you need (sq ft)",
            "floors": "Number of floors",
            "budget": "Budget range",
            "timeline": "When do you want to start?",
            "message": "Anything else we should know?",
            "attachment": "Plot sketch, plan or photos (optional)",
            "name": "Your name",
            "phone": "Phone number",
            "email": "Email (optional)",
            "preferred_contact": "How should we reach you?",
        }
        widgets = {
            "plot_location": forms.TextInput(attrs={"placeholder": "Area, town or Google Maps link"}),
            "plot_size": forms.TextInput(attrs={"placeholder": "e.g. 8 cents or 40 × 60 ft"}),
            "built_up_area": forms.NumberInput(attrs={"min": 100, "step": 50, "placeholder": "e.g. 2200"}),
            "floors": forms.NumberInput(attrs={"min": 1, "max": 30, "placeholder": "e.g. 2"}),
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Rooms you need, style you like, existing structure on the plot…"}),
            "preferred_contact": forms.RadioSelect,
            "estimate_low": forms.HiddenInput,
            "estimate_high": forms.HiddenInput,
            "phone": forms.TextInput(attrs={"inputmode": "tel", "autocomplete": "tel"}),
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["budget"].choices = [("", "Choose a range")] + list(Inquiry.Budget.choices)
        self.fields["timeline"].choices = [("", "Choose a timeline")] + list(Inquiry.Timeline.choices)
        self.fields["plot_location"].required = True
        self.fields["attachment"].widget.attrs["accept"] = ".pdf,.jpg,.jpeg,.png,.webp,.dwg,.dxf"

    def clean_phone(self):
        return clean_phone_value(self.cleaned_data.get("phone"))

    def save(self, commit=True):
        inquiry = super().save(commit=False)
        plan = self.cleaned_data.get("approved_plan")
        inquiry.has_approved_plan = {"yes": True, "no": False}.get(plan)
        inquiry.source = Inquiry.Source.ESTIMATOR if inquiry.estimate_low else Inquiry.Source.QUOTE
        if commit:
            inquiry.save()
        return inquiry


class ContactForm(HoneypotMixin, forms.ModelForm):
    service = forms.ChoiceField(
        choices=[("", "General question")] + list(ServiceKind.choices), required=False, label="About"
    )

    class Meta:
        model = Inquiry
        fields = ["name", "phone", "email", "service", "message"]
        labels = {"name": "Your name", "phone": "Phone number", "email": "Email (optional)", "message": "Message"}
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
            "phone": forms.TextInput(attrs={"inputmode": "tel", "autocomplete": "tel"}),
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["message"].required = True

    def clean_phone(self):
        return clean_phone_value(self.cleaned_data.get("phone"))

    def save(self, commit=True):
        inquiry = super().save(commit=False)
        inquiry.source = Inquiry.Source.CONTACT
        if commit:
            inquiry.save()
        return inquiry
