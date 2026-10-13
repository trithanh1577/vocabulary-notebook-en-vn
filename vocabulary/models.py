from django.db import models


class Word(models.Model):
    word = models.CharField("Từ tiếng Anh", max_length=120, unique=True)
    part_of_speech = models.CharField("Từ loại", max_length=60, blank=True)
    meaning_vi = models.TextField("Nghĩa tiếng Việt")
    example_sentence = models.TextField("Câu ví dụ", blank=True)
    usage_note = models.TextField("Ghi chú cách dùng", blank=True)
    notes = models.TextField("Ghi chú riêng", blank=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    updated_at = models.DateTimeField("Cập nhật lần cuối", auto_now=True)

    class Meta:
        ordering = ["word"]
        verbose_name = "Từ vựng"
        verbose_name_plural = "Từ vựng"

    def __str__(self):
        return self.word


class ReviewLog(models.Model):
    class Result(models.TextChoices):
        REMEMBERED = "remembered", "Đã nhớ"
        PRACTICE = "practice", "Cần ôn thêm"

    word = models.ForeignKey(
        Word,
        on_delete=models.CASCADE,
        related_name="review_logs",
        verbose_name="Từ vựng",
    )
    result = models.CharField(
        "Kết quả",
        max_length=20,
        choices=Result.choices,
        default=Result.PRACTICE,
    )
    note = models.CharField("Ghi chú", max_length=240, blank=True)
    reviewed_at = models.DateTimeField("Thời điểm ôn", auto_now_add=True)

    class Meta:
        ordering = ["-reviewed_at"]
        verbose_name = "Lần ôn tập"
        verbose_name_plural = "Lịch sử ôn tập"

    def __str__(self):
        return f"{self.word.word} — {self.get_result_display()}"
