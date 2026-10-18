from django.test import TestCase
from django.urls import reverse

from .models import ReviewLog, Word


class VocabularyPagesTests(TestCase):
    def setUp(self):
        self.word = Word.objects.create(
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
        self.assertTrue(Word.objects.filter(word="curious", meaning_vi="tò mò").exists())

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
