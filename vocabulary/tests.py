from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import ReviewLog, Word


class VocabularyPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="anything")
        self.client.force_login(self.user)
        self.word = Word.objects.create(
            owner=self.user,
            word="resilient",
            part_of_speech="adjective",
            meaning_vi="kiên cường",
            notes="Able to recover quickly.",
        )

    def test_word_list_shows_saved_words(self):
        response = self.client.get(reverse("word_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "resilient")
        self.assertContains(response, "kiên cường")

    def test_word_list_searches_english_and_vietnamese(self):
        english_response = self.client.get(reverse("word_list"), {"q": "resil"})
        vietnamese_response = self.client.get(reverse("word_list"), {"q": "kiên"})

        self.assertContains(english_response, "resilient")
        self.assertContains(vietnamese_response, "resilient")

    def test_word_can_be_added(self):
        response = self.client.post(
            reverse("word_create"),
            {
                "word": "curious",
                "part_of_speech": "adjective",
                "meaning_vi": "tò mò",
                "notes": "",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Word.objects.filter(
                owner=self.user, word="curious", meaning_vi="tò mò"
            ).exists()
        )

    def test_review_can_be_saved_and_listed(self):
        response = self.client.post(
            reverse("review_create", args=[self.word.pk]),
            {"result": ReviewLog.Result.REMEMBERED, "note": "Easy to recall."},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ReviewLog.objects.filter(
                word=self.word,
                result=ReviewLog.Result.REMEMBERED,
                note="Easy to recall.",
            ).exists()
        )
        history_response = self.client.get(reverse("review_list"))
        self.assertContains(history_response, "resilient")
        self.assertContains(history_response, "Easy to recall.")

    def test_health_check_returns_ok(self):
        response = self.client.get(reverse("health_check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class PracticeModeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="learner", password="anything")
        self.client.force_login(self.user)
        self.word = Word.objects.create(
            owner=self.user,
            word="careful",
            part_of_speech="adjective",
            meaning_vi="cẩn thận",
        )

    def test_collection_quiz_records_a_correct_answer(self):
        response = self.client.get(
            reverse("practice_session", kwargs={"mode": "collection"}),
            {"restart": "1"},
        )

        self.assertEqual(response.status_code, 200)
        state = self.client.session[f"practice_{self.user.pk}_collection"]
        answer = next(
            option for option in state["options"] if option["value"] == str(self.word.pk)
        )
        response = self.client.post(
            reverse("practice_session", kwargs={"mode": "collection"}),
            {"answer": answer["value"], "question_token": state["token"]},
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ReviewLog.objects.filter(
                word=self.word, result=ReviewLog.Result.REMEMBERED
            ).exists()
        )

    def test_unlearned_count_uses_the_latest_review(self):
        ReviewLog.objects.create(word=self.word, result=ReviewLog.Result.PRACTICE)
        ReviewLog.objects.create(word=self.word, result=ReviewLog.Result.REMEMBERED)

        response = self.client.get(reverse("practice_home"))

        self.assertContains(response, "0 từ cần ôn")

    @patch("vocabulary.views.generate_new_vocabulary")
    def test_unknown_new_word_is_added_to_collection(self, generate_words):
        generate_words.return_value = [
            {
                "word": "ponder",
                "part_of_speech": "verb",
                "meaning_vi": "suy ngẫm",
                "example_sentence": "She paused to ponder the question.",
                "usage_note": "Thường dùng khi suy nghĩ kỹ về một việc.",
            },
            {
                "word": "gather",
                "part_of_speech": "verb",
                "meaning_vi": "thu thập",
                "example_sentence": "They gather information before deciding.",
                "usage_note": "Có thể dùng cho đồ vật hoặc thông tin.",
            },
        ]

        response = self.client.get(
            reverse("practice_session", kwargs={"mode": "new"}),
            {"restart": "1"},
        )
        self.assertEqual(response.status_code, 200)
        state = self.client.session[f"practice_{self.user.pk}_new"]
        wrong_answer = next(option for option in state["options"] if not option["correct"])

        response = self.client.post(
            reverse("practice_session", kwargs={"mode": "new"}),
            {"answer": wrong_answer["value"], "question_token": state["token"]},
        )

        self.assertEqual(response.status_code, 302)
        new_word = Word.objects.get(owner=self.user, word="ponder")
        self.assertEqual(new_word.meaning_vi, "suy ngẫm")
        self.assertTrue(new_word.example_sentence)
        self.assertTrue(
            ReviewLog.objects.filter(
                word=new_word, result=ReviewLog.Result.PRACTICE
            ).exists()
        )

    @patch("vocabulary.views.generate_word_examples")
    def test_ai_suggestions_are_saved_for_a_word(self, generate_examples):
        generate_examples.return_value = {
            "example_sentence": "Be careful when crossing the road.",
            "usage_note": "Dùng để nhắc ai đó chú ý.",
            "part_of_speech": "adjective",
        }

        response = self.client.post(
            reverse("word_generate_ai", args=[self.word.pk])
        )

        self.assertEqual(response.status_code, 302)
        self.word.refresh_from_db()
        self.assertEqual(
            self.word.example_sentence, "Be careful when crossing the road."
        )
        self.assertEqual(self.word.usage_note, "Dùng để nhắc ai đó chú ý.")
