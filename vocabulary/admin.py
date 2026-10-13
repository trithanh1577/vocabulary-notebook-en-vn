from django.contrib import admin

from .models import ReviewLog, Word


class ReviewLogInline(admin.TabularInline):
    model = ReviewLog
    extra = 0


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("word", "part_of_speech", "meaning_vi", "updated_at")
    search_fields = ("word", "meaning_vi")
    inlines = (ReviewLogInline,)


@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ("word", "result", "reviewed_at")
    list_filter = ("result", "reviewed_at")
    search_fields = ("word__word", "note")
