from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'status': forms.Select(choices=Project.STATUS_CHOICES),
        }
    
    def clean_github_url(self):
        url = self.cleaned_data.get('github_url')
        if url:
            if not url.startswith('https://github.com/'):
                raise forms.ValidationError('Ссылка должна вести на GitHub (https://github.com/...)')
        return url
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name and len(name.strip()) < 1:
            raise forms.ValidationError('Название проекта не может быть пустым')
        return name.strip() if name else name