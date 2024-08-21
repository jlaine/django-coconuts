from django import forms


class PhotoForm(forms.Form):
    SIZE_CHOICES = (
        (128, "128"),
        (256, "256"),
        (800, "800"),
        (1024, "1024"),
        (1280, "1280"),
        (1600, "1600"),
        (2048, "2048"),
        (2560, "2560"),
    )

    size = forms.TypedChoiceField(choices=SIZE_CHOICES, coerce=int)
