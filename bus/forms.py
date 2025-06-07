from django import forms
from django.core.exceptions import ValidationError

class ApplicationConfirmationForm(forms.Form):
    document = forms.FileField(
        widget=forms.FileInput(attrs={
            'style': 'font-size: 12px; padding: 2px; max-width: 60%;',
            'accept': '.jpg,.jpeg,.png'
        }),
        help_text="Bus Confirmation Email(image)"
    )
    def clean_document(self):
        file = self.cleaned_data.get('document')

        #Check file size
        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            raise ValidationError("File too large (max 5MB)")
        #Check file type
        valid_mime_types = ['image/jpeg', 'image/jpg', 'image/png']
        if file.content_type not in valid_mime_types:
            raise ValidationError("Unsupported file type")

        return file
    


