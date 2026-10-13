from django import forms

from .models import ReviewLog, Word


class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ["word", "part_of_speech", "meaning_vi", "notes"]
        widgets = {
            "word": forms.TextInput(attrs={"placeholder": "Ví dụ: resilient"}),
            "part_of_speech": forms.TextInput(attrs={"placeholder": "Ví dụ: adjective"}),
            "meaning_vi": forms.Textarea(attrs={"rows": 3, "placeholder": "Nghĩa của từ bằng tiếng Việt"}),
            "notes": forms.Textarea(attrs={"rows": 3, "placeholder": "Mẹo nhớ hoặc ngữ cảnh của bạn"}),
        }


class ReviewLogForm(forms.ModelForm):
    class Meta:
        model = ReviewLog
        fields = ["result", "note"]
        widgets = {
            "note": forms.TextInput(attrs={"placeholder": "Ghi chú ngắn (không bắt buộc)"}),
        }
