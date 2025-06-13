from django import forms
from django.contrib.auth import password_validation, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=150, required=True, label=_("First name")
    )
    last_name = forms.CharField(
        max_length=150, required=True, label=_("Last name")
    )

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "password1",
            "password2",
        )

    def clean_username(self):
        username = self.cleaned_data["username"]
        qs = User.objects.exclude(pk=self.instance.pk)
        if qs.filter(username=username).exists():
            raise forms.ValidationError(
                _("User with this username already exists.")
            )
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class CustomUserChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

    first_name = forms.CharField(required=True, label=_("First name"))
    last_name = forms.CharField(required=True, label=_("Last name"))
    username = forms.CharField(required=True, label=_("Username"))

    new_password1 = forms.CharField(
        required=False,
        label=_("New password"),
        widget=forms.PasswordInput,
    )
    new_password2 = forms.CharField(
        required=False,
        label=_("Confirm new password"),
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username"]

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")

        if p1 or p2:
            if not p1:
                self.add_error(
                    "new_password1", _("Please enter the new password.")
                )
            if not p2:
                self.add_error(
                    "new_password2", _("Please confirm the new password.")
                )
            if p1 and p2:
                if p1 != p2:
                    self.add_error(
                        "new_password2", _("Passwords do not match.")
                    )
                else:
                    try:
                        password_validation.validate_password(p1, self.instance)
                    except ValidationError as e:
                        self.add_error("new_password1", e)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("new_password1")
        if new_password:
            user.set_password(new_password)
            if commit:
                user.save()
                if self.request:
                    update_session_auth_hash(self.request, user)
        else:
            if commit:
                user.save()
        return user
