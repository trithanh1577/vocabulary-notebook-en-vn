from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import ReviewLog, Word


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username",)
        labels = {"username": "Tên đăng nhập"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Mật khẩu"
        self.fields["password1"].help_text = ""
        self.fields["password2"].label = "Nhập lại mật khẩu"
        self.fields["password2"].help_text = ""


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
