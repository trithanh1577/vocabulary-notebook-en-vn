import os
import random
import time
import uuid

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import OuterRef, Q, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import RegisterForm, ReviewLogForm, WordForm
from .gemini import GeminiServiceError, generate_new_vocabulary, generate_word_examples
from .models import ReviewLog, Word


PRACTICE_MODES = {
    "collection": "Ôn từ trong bộ sưu tập",
    "new": "Học từ mới với Gemini",
    "unlearned": "Ôn từ chưa thuộc",
}


def register(request):
    if request.user.is_authenticated:
        return redirect("word_list")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                is_first_account = not User.objects.filter(
                    is_staff=False, is_superuser=False
                ).exists()
                user = form.save()
                if is_first_account:
                    # Keep the existing single-user collection with the first account.
                    Word.objects.filter(owner__isnull=True).update(owner=user)
            login(request, user)
            messages.success(request, "Tạo tài khoản thành công. Chào mừng bạn!")
            return redirect("word_list")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("word_list")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            next_url = request.POST.get("next") or request.GET.get("next", "")
            if url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect("word_list")
    else:
        form = AuthenticationForm(request)

    return render(request, "registration/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Bạn đã đăng xuất.")
    return redirect("login")


def _words_to_review(user):
    latest_result = Subquery(
        ReviewLog.objects.filter(word_id=OuterRef("pk"))
        .order_by("-reviewed_at", "-pk")
        .values("result")[:1]
    )
    return Word.objects.filter(owner=user).annotate(
        latest_review_result=latest_result
    ).filter(
        latest_review_result=ReviewLog.Result.PRACTICE
    )


def _allow_ai_request(request):
    """Prevent accidental rapid repeat calls to the free API from one session."""
    now = time.time()
    session_key = f"gemini_last_request_{request.user.pk}"
    last_request = float(request.session.get(session_key, 0))
    if now - last_request < 10:
        return False
    request.session[session_key] = now
    return True


def _word_choices(word, user):
    candidates = [word]
    candidates.extend(
        Word.objects.filter(owner=user).exclude(pk=word.pk).order_by("?")[:8]
    )
    choices = []
    seen_meanings = set()
    for candidate in candidates:
        meaning = candidate.meaning_vi.strip()
        normalized = meaning.casefold()
        if not meaning or normalized in seen_meanings:
            continue
        seen_meanings.add(normalized)
        choices.append({"value": str(candidate.pk), "label": meaning})
        if len(choices) == 4:
            break
    random.shuffle(choices)
    return choices


def _new_word_choices(question, pool):
    options = [{"label": question["meaning_vi"], "correct": True}]
    seen = {question["meaning_vi"].strip().casefold()}
    distractors = []
    for item in pool:
        meaning = item["meaning_vi"].strip()
        normalized = meaning.casefold()
        if normalized in seen:
            continue
        seen.add(normalized)
        distractors.append({"label": meaning, "correct": False})
    random.shuffle(distractors)
    options.extend(distractors[:3])
    random.shuffle(options)
    return [{**option, "value": str(index)} for index, option in enumerate(options)]


def health_check(request):
    return JsonResponse({"status": "ok"})


@login_required
def word_list(request):
    query = request.GET.get("q", "").strip()
    words = Word.objects.filter(owner=request.user)
    if query:
        words = words.filter(
            Q(word__icontains=query)
            | Q(meaning_vi__icontains=query)
            | Q(part_of_speech__icontains=query)
        )
    return render(
        request,
        "vocabulary/word_list.html",
        {
            "words": words,
            "query": query,
            "total_words": Word.objects.filter(owner=request.user).count(),
        },
    )


@login_required
def word_detail(request, pk):
    word = get_object_or_404(Word, pk=pk, owner=request.user)
    return render(
        request,
        "vocabulary/word_detail.html",
        {"word": word, "review_form": ReviewLogForm()},
    )


@login_required
@require_POST
def word_generate_ai(request, pk):
    word = get_object_or_404(Word, pk=pk, owner=request.user)
    if not _allow_ai_request(request):
        messages.error(request, "Bạn vừa gửi yêu cầu AI. Chờ vài giây rồi thử lại nhé.")
        return redirect("word_detail", pk=word.pk)

    try:
        suggestion = generate_word_examples(
            word.word, word.meaning_vi, word.part_of_speech
        )
    except GeminiServiceError as error:
        messages.error(request, str(error))
        return redirect("word_detail", pk=word.pk)

    word.example_sentence = suggestion["example_sentence"]
    word.usage_note = suggestion["usage_note"]
    if not word.part_of_speech and suggestion["part_of_speech"]:
        word.part_of_speech = suggestion["part_of_speech"]
    word.save(
        update_fields=["example_sentence", "usage_note", "part_of_speech", "updated_at"]
    )
    messages.success(request, "Gemini đã tạo câu ví dụ và ghi chú cách dùng.")
    return redirect("word_detail", pk=word.pk)


@login_required
def word_create(request):
    if request.method == "POST":
        form = WordForm(request.POST)
        form.instance.owner = request.user
        if form.is_valid():
            word = form.save()
            messages.success(request, f"Đã thêm từ “{word.word}”.")
            return redirect("word_detail", pk=word.pk)
    else:
        form = WordForm()
    return render(request, "vocabulary/word_form.html", {"form": form, "is_edit": False})


@login_required
def word_update(request, pk):
    word = get_object_or_404(Word, pk=pk, owner=request.user)
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


@login_required
def word_delete(request, pk):
    word = get_object_or_404(Word, pk=pk, owner=request.user)
    if request.method == "POST":
        label = word.word
        word.delete()
        messages.success(request, f"Đã xóa từ “{label}” và lịch sử ôn tập của từ.")
        return redirect("word_list")
    return render(request, "vocabulary/word_confirm_delete.html", {"word": word})


@login_required
@require_POST
def review_create(request, pk):
    word = get_object_or_404(Word, pk=pk, owner=request.user)
    form = ReviewLogForm(request.POST)
    if form.is_valid():
        review = form.save(commit=False)
        review.word = word
        review.save()
        messages.success(request, "Đã lưu lần ôn tập.")
    else:
        messages.error(request, "Chưa lưu được lần ôn tập. Hãy kiểm tra thông tin.")
    return redirect("word_detail", pk=word.pk)


@login_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(
        ReviewLog.objects.select_related("word"), pk=pk, word__owner=request.user
    )
    word_pk = review.word_id
    review.delete()
    messages.success(request, "Đã xóa bản ghi ôn tập.")
    return redirect("word_detail", pk=word_pk)


@login_required
def review_list(request):
    query = request.GET.get("q", "").strip()
    reviews = ReviewLog.objects.filter(word__owner=request.user).select_related("word")
    if query:
        reviews = reviews.filter(
            Q(word__word__icontains=query) | Q(word__meaning_vi__icontains=query)
        )
    return render(
        request,
        "vocabulary/review_list.html",
        {"reviews": reviews[:100], "query": query},
    )


@login_required
def practice_home(request):
    return render(
        request,
        "vocabulary/practice_home.html",
        {
            "collection_count": Word.objects.filter(owner=request.user).count(),
            "unlearned_count": _words_to_review(request.user).count(),
            "gemini_configured": bool(os.getenv("GEMINI_API_KEY", "").strip()),
        },
    )


def _start_practice(request, mode, session_key):
    if mode == "collection":
        question_ids = list(
            Word.objects.filter(owner=request.user).values_list("pk", flat=True)
        )
        random.shuffle(question_ids)
        questions = question_ids
        pool = []
    elif mode == "unlearned":
        question_ids = list(
            _words_to_review(request.user).values_list("pk", flat=True)
        )
        random.shuffle(question_ids)
        questions = question_ids
        pool = []
    else:
        if not _allow_ai_request(request):
            messages.error(request, "Bạn vừa gửi yêu cầu AI. Chờ vài giây rồi thử lại nhé.")
            return False
        try:
            pool = generate_new_vocabulary(count=8)
        except GeminiServiceError as error:
            messages.error(request, str(error))
            return False

        saved_words = {
            saved.casefold()
            for saved in Word.objects.filter(owner=request.user).values_list(
                "word", flat=True
            )
        }
        pool = [item for item in pool if item["word"].casefold() not in saved_words]
        questions = pool[:5]
        if not questions:
            messages.info(
                request,
                "Gemini chưa tạo được từ mới khác với bộ sưu tập. Hãy thử lại sau.",
            )
            return False

    if not questions:
        if mode == "collection":
            messages.info(request, "Bộ sưu tập chưa có từ nào để kiểm tra.")
        else:
            messages.info(request, "Hiện chưa có từ nào được đánh dấu cần ôn thêm.")
        return False

    request.session[session_key] = {
        "questions": questions,
        "pool": pool,
        "index": 0,
        "options": [],
        "token": "",
    }
    return True


@login_required
def practice_session(request, mode):
    if mode not in PRACTICE_MODES:
        return redirect("practice_home")

    session_key = f"practice_{request.user.pk}_{mode}"
    state = request.session.get(session_key)
    if request.method == "GET" and (request.GET.get("restart") or not state):
        if not _start_practice(request, mode, session_key):
            return redirect("practice_home")
        state = request.session[session_key]
    if not state:
        return redirect("practice_home")

    questions = state["questions"]
    question_index = state["index"]
    total_questions = len(questions)
    if question_index >= total_questions:
        return render(
            request,
            "vocabulary/practice_session.html",
            {
                "mode": mode,
                "mode_label": PRACTICE_MODES[mode],
                "is_complete": True,
                "total_questions": total_questions,
            },
        )

    if mode == "new":
        question = questions[question_index]
        options = state.get("options") or _new_word_choices(question, state["pool"])
        question_word = question["word"]
        part_of_speech = question["part_of_speech"]
        correct_answer = question["meaning_vi"]
    else:
        question = Word.objects.filter(
            pk=questions[question_index], owner=request.user
        ).first()
        if question is None:
            state["index"] += 1
            state["options"] = []
            request.session[session_key] = state
            return redirect("practice_session", mode=mode)
        options = state.get("options") or _word_choices(question, request.user)
        question_word = question.word
        part_of_speech = question.part_of_speech
        correct_answer = question.meaning_vi

    if request.method == "POST":
        submitted_token = request.POST.get("question_token", "")
        if not state.get("token") or submitted_token != state["token"]:
            messages.error(request, "Câu trả lời này đã được xử lý hoặc hết hạn. Hãy tiếp tục.")
            return redirect("practice_session", mode=mode)

        selected_value = request.POST.get("answer", "")
        selected = next(
            (option for option in options if option["value"] == selected_value), None
        )
        if selected is None:
            messages.error(request, "Hãy chọn một đáp án trước khi tiếp tục.")
            return redirect("practice_session", mode=mode)

        if mode == "new":
            is_correct = selected["correct"]
            if is_correct:
                messages.success(
                    request,
                    f"Đúng rồi! “{question_word}” nghĩa là “{correct_answer}”.",
                )
            else:
                word, created = Word.objects.get_or_create(
                    owner=request.user,
                    word=question_word,
                    defaults={
                        "part_of_speech": part_of_speech,
                        "meaning_vi": correct_answer,
                        "example_sentence": question["example_sentence"],
                        "usage_note": question["usage_note"],
                        "notes": "Được thêm tự động từ chế độ học từ mới.",
                    },
                )
                if created:
                    ReviewLog.objects.create(
                        word=word,
                        result=ReviewLog.Result.PRACTICE,
                        note="Chưa thuộc - thêm từ bài học từ mới",
                    )
                messages.info(
                    request,
                    f"Chưa chính xác. “{question_word}” là “{correct_answer}” và đã được thêm vào bộ sưu tập.",
                )
        else:
            is_correct = selected_value == str(question.pk)
            result = (
                ReviewLog.Result.REMEMBERED
                if is_correct
                else ReviewLog.Result.PRACTICE
            )
            ReviewLog.objects.create(
                word=question,
                result=result,
                note="Bài tập từ vựng",
            )
            if is_correct:
                messages.success(
                    request,
                    f"Chính xác! “{question_word}” nghĩa là “{correct_answer}”.",
                )
            else:
                messages.error(
                    request,
                    f"Chưa đúng. “{question_word}” nghĩa là “{correct_answer}”.",
                )

        state["index"] += 1
        state["options"] = []
        state["token"] = ""
        request.session[session_key] = state
        return redirect("practice_session", mode=mode)

    if not state.get("options"):
        if mode == "new":
            options = _new_word_choices(question, state["pool"])
        else:
            options = _word_choices(question, request.user)
        state["options"] = options
        state["token"] = uuid.uuid4().hex
        request.session[session_key] = state

    return render(
        request,
        "vocabulary/practice_session.html",
        {
            "mode": mode,
            "mode_label": PRACTICE_MODES[mode],
            "question_word": question_word,
            "part_of_speech": part_of_speech,
            "options": state["options"],
            "question_token": state["token"],
            "question_number": question_index + 1,
            "total_questions": total_questions,
            "progress_percent": round((question_index + 1) / total_questions * 100),
            "is_new_vocabulary": mode == "new",
        },
    )
