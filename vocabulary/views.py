from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ReviewLogForm, WordForm
from .models import ReviewLog, Word


def health_check(request):
    return JsonResponse({"status": "ok"})


def word_list(request):
    query = request.GET.get("q", "").strip()
    words = Word.objects.all()
    if query:
        words = words.filter(
            Q(word__icontains=query)
            | Q(meaning_vi__icontains=query)
            | Q(part_of_speech__icontains=query)
        )
    return render(
        request,
        "vocabulary/word_list.html",
        {"words": words, "query": query, "total_words": Word.objects.count()},
    )


def word_detail(request, pk):
    word = get_object_or_404(Word, pk=pk)
    return render(
        request,
        "vocabulary/word_detail.html",
        {"word": word, "review_form": ReviewLogForm()},
    )


def word_create(request):
    if request.method == "POST":
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.save()
            messages.success(request, f"Đã thêm từ “{word.word}”.")
            return redirect("word_detail", pk=word.pk)
    else:
        form = WordForm()
    return render(request, "vocabulary/word_form.html", {"form": form, "is_edit": False})


def word_update(request, pk):
    word = get_object_or_404(Word, pk=pk)
    if request.method == "POST":
        form = WordForm(request.POST, instance=word)
        if form.is_valid():
            form.save()
            messages.success(request, "Đã cập nhật từ vựng.")
            return redirect("word_detail", pk=word.pk)
    else:
        form = WordForm(instance=word)
    return render(
        request,
        "vocabulary/word_form.html",
        {"form": form, "word": word, "is_edit": True},
    )


def word_delete(request, pk):
    word = get_object_or_404(Word, pk=pk)
    if request.method == "POST":
        label = word.word
        word.delete()
        messages.success(request, f"Đã xóa từ “{label}” và lịch sử ôn tập của từ.")
        return redirect("word_list")
    return render(request, "vocabulary/word_confirm_delete.html", {"word": word})


@require_POST
def review_create(request, pk):
    word = get_object_or_404(Word, pk=pk)
    form = ReviewLogForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.word = word
        review.save()
        messages.success(request, "Đã lưu lần ôn tập.")
    else:
        messages.error(request, "Chưa lưu được lần ôn tập. Hãy kiểm tra thông tin.")
    return redirect("word_detail", pk=word.pk)


@require_POST
def review_delete(request, pk):
    review = get_object_or_404(ReviewLog.objects.select_related("word"), pk=pk)
    word_pk = review.word_id
    review.delete()
    messages.success(request, "Đã xóa bản ghi ôn tập.")
    return redirect("word_detail", pk=word_pk)


def review_list(request):
    query = request.GET.get("q", "").strip()
    reviews = ReviewLog.objects.select_related("word")
    if query:
        reviews = reviews.filter(
            Q(word__word__icontains=query) | Q(word__meaning_vi__icontains=query)
        )
    return render(
        request,
        "vocabulary/review_list.html",
        {"reviews": reviews[:100], "query": query},
    )
