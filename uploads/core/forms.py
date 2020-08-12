from django import forms

from uploads.core.models import Document
from multiupload.fields import MultiFileField


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('description', 'document', )


class UploadForm(forms.Form):

    attachments = MultiFileField(min_num=1, max_num=10, max_file_size=1024*1024*5)
