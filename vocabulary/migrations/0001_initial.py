import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Word",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("word", models.CharField(max_length=120, unique=True, verbose_name="Từ tiếng Anh")),
                ("part_of_speech", models.CharField(blank=True, max_length=60, verbose_name="Từ loại")),
                ("meaning_vi", models.TextField(verbose_name="Nghĩa tiếng Việt")),
                ("example_sentence", models.TextField(blank=True, verbose_name="Câu ví dụ")),
                ("usage_note", models.TextField(blank=True, verbose_name="Ghi chú cách dùng")),
                ("notes", models.TextField(blank=True, verbose_name="Ghi chú riêng")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Cập nhật lần cuối")),
            ],
            options={"verbose_name": "Từ vựng", "verbose_name_plural": "Từ vựng", "ordering": ["word"]},
        ),
        migrations.CreateModel(
            name="ReviewLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("result", models.CharField(choices=[("remembered", "Đã nhớ"), ("practice", "Cần ôn thêm")], default="practice", max_length=20, verbose_name="Kết quả")),
                ("note", models.CharField(blank=True, max_length=240, verbose_name="Ghi chú")),
                ("reviewed_at", models.DateTimeField(auto_now_add=True, verbose_name="Thời điểm ôn")),
                ("word", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="review_logs", to="vocabulary.word", verbose_name="Từ vựng")),
            ],
            options={"verbose_name": "Lần ôn tập", "verbose_name_plural": "Lịch sử ôn tập", "ordering": ["-reviewed_at"]},
        ),
    ]
