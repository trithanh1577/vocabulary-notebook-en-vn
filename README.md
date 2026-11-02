# Vocabulary Notebook EN–VI

Ứng dụng web giúp người học lưu từ vựng tiếng Anh, nghĩa tiếng Việt và lịch sử ôn tập. Dự án được thực hiện cho môn **72ITDS30103 – Software Development Platforms**.

## Tổng quan

Mỗi người dùng có tài khoản và bộ sưu tập từ riêng. Người dùng có thể tìm, thêm, sửa, xóa từ; ghi lại mình đã nhớ hay cần ôn thêm; và xem lại lịch sử học. Ứng dụng có ba chế độ luyện tập: kiểm tra từ đã lưu, học từ mới do Gemini gợi ý, và ôn các từ được đánh dấu cần ôn thêm.

Gemini cũng có thể tạo câu ví dụ tiếng Anh và ghi chú cách dùng bằng tiếng Việt cho một từ. Tính năng AI là tùy chọn: các chức năng quản lý từ, tài khoản và ôn từ đã lưu vẫn dùng được khi chưa cấu hình API key.

## Chức năng

- Đăng ký, đăng nhập và đăng xuất.
- Dữ liệu từ vựng và lịch sử ôn tập được phân tách theo tài khoản.
- Tìm kiếm từ theo từ tiếng Anh, nghĩa tiếng Việt hoặc từ loại.
- Thêm, sửa, xóa từ; ghi chú và xem lịch sử ôn của từng từ.
- Trắc nghiệm nghĩa từ trong bộ sưu tập.
- Ôn lại từ có kết quả gần nhất là “Cần ôn thêm”.
- Học từ mới do Gemini tạo; nếu trả lời sai, từ và thông tin gợi ý được thêm vào bộ sưu tập để ôn tiếp.
- Tạo câu ví dụ và ghi chú cách dùng bằng Gemini từ trang chi tiết từ.

## Công nghệ và dịch vụ

- Python 3.12, Django 5.2.
- HTML và CSS; giao diện được phục vụ bởi Django và WhiteNoise.
- PostgreSQL cho Docker Compose local và cơ sở dữ liệu production trên Supabase.
- Docker và Docker Compose để chạy ứng dụng trong môi trường nhất quán.
- GitHub và GitHub Actions để quản lý mã nguồn, Pull Request và CI.
- Render để build Docker image và host website.
- Gemini API cho các chức năng gợi ý học tập (không bắt buộc).
- Visual Studio Code để mở, sửa và chạy dự án.

## Website và liên kết

| Nội dung | Liên kết |
| --- | --- |
| Website | [vocabulary-notebook-en-vn.onrender.com](https://vocabulary-notebook-en-vn.onrender.com) |
| Health check | [vocabulary-notebook-en-vn.onrender.com/health/](https://vocabulary-notebook-en-vn.onrender.com/health/) |
| GitHub repository | [trithanh1577/vocabulary-notebook-en-vn](https://github.com/trithanh1577/vocabulary-notebook-en-vn) |
| Pull Requests | [Danh sách Pull Request](https://github.com/trithanh1577/vocabulary-notebook-en-vn/pulls) |
| Render Dashboard | [dashboard.render.com](https://dashboard.render.com/) |
| Supabase Dashboard | [supabase.com/dashboard](https://supabase.com/dashboard) |
| Google AI Studio | [aistudio.google.com](https://aistudio.google.com/) |

Render gói miễn phí có thể tạm dừng dịch vụ khi ít hoạt động; lượt truy cập đầu tiên sau đó có thể cần chờ ứng dụng khởi động lại.

## Cấu trúc dự án

```text
config/
  settings.py                 Cấu hình Django, cơ sở dữ liệu, bảo mật và static files
  urls.py                     Các URL gốc: admin, health check, tài khoản và app
  wsgi.py                     Điểm khởi chạy ứng dụng WSGI cho Gunicorn

vocabulary/
  admin.py                    Đăng ký model để xem trong Django Admin
  apps.py                     Cấu hình Django app
  forms.py                    Form từ vựng, lịch sử ôn và đăng ký
  gemini.py                   Gọi Gemini API và kiểm tra dữ liệu trả về
  models.py                   Model Word và ReviewLog
  urls.py                     URL của từ vựng, ôn tập và lịch sử
  views.py                    Xử lý đăng nhập, dữ liệu từ, luyện tập và AI
  tests.py                    Kiểm thử các luồng chính của ứng dụng
  migrations/                 Lịch sử thay đổi cấu trúc cơ sở dữ liệu
  templates/
    registration/             Giao diện đăng nhập và đăng ký
    vocabulary/               Giao diện danh sách, chi tiết, form và bài ôn
  static/vocabulary/          CSS và hình ảnh giao diện, gồm penguin-logo.jpg

.devcontainer/                Cấu hình môi trường Dev Container cho VS Code
.github/
  workflows/ci.yml            GitHub Actions: kiểm tra cấu hình, migrations, static và tests
  PULL_REQUEST_TEMPLATE.md    Mẫu nội dung Pull Request
.vscode/
  extensions.json             Gợi ý extensions cho workspace
  tasks.json                  Các task có thể chạy từ Visual Studio Code

.dockerignore                 Loại file không cần gửi vào Docker build context
.env.example                  Ví dụ biến môi trường; không chứa API key thật
.gitignore                    Loại file local và file bí mật khỏi Git
Dockerfile                    Build image và chạy Django bằng Gunicorn trên Render
compose.yaml                  Chạy Django và PostgreSQL local bằng Docker Compose
manage.py                     Lệnh quản trị Django
README.md                     Tài liệu dự án này
render.yaml                   Blueprint cấu hình dịch vụ Render
requirements.txt              Danh sách thư viện Python
```

## Chạy local bằng Docker Desktop

### Yêu cầu

- Visual Studio Code (hoặc terminal bất kỳ).
- Git.
- Docker Desktop đang chạy.

Mở thư mục repository trong VS Code. Có thể tạo file `.env` từ file mẫu để tùy chỉnh cấu hình local:

```powershell
Copy-Item .env.example .env
```

`GEMINI_API_KEY` có thể để trống nếu chỉ dùng chức năng từ vựng và ôn các từ đã lưu. Để dùng chức năng AI, điền API key vào `.env` ở máy local.

Khởi động Django và PostgreSQL:

```powershell
docker compose up --build
```

Mở [http://localhost:8000](http://localhost:8000). Compose tự chạy migrations và thu thập static files khi khởi động.

Nhấn `Ctrl+C` để dừng tiến trình, sau đó chạy:

```powershell
docker compose down
```

Dữ liệu PostgreSQL local nằm trong Docker volume `postgres_data` và vẫn còn sau lệnh `docker compose down`. Lệnh `docker compose down -v` xóa volume này cùng dữ liệu local.

## Cấu hình môi trường

| Biến | Bắt buộc | Mục đích |
| --- | --- | --- |
| `SECRET_KEY` | Production: có | Khóa bí mật Django. Render tạo giá trị qua `render.yaml`. |
| `DEBUG` | Không | Bật lỗi phát triển local; phải tắt trên production. |
| `ALLOWED_HOSTS` | Tùy môi trường | Danh sách hostname Django chấp nhận. |
| `DATABASE_URL` | Production: có | Chuỗi kết nối PostgreSQL, trên Render lấy từ Supabase. Compose tự cấu hình database local. |
| `GEMINI_API_KEY` | Chỉ khi dùng AI | API key Gemini. Tên biến phải viết đúng chính tả này. |
| `GEMINI_MODEL` | Không | Tên model Gemini; nếu bỏ trống, ứng dụng dùng giá trị mặc định trong code. |
| `PORT` | Render tự cấp | Cổng mà web service phải lắng nghe; Dockerfile dùng `10000` làm giá trị dự phòng. |

Trên Render, cấu hình các secret trong **Web Service → Environment**. Không ghi API key, mật khẩu database, `SECRET_KEY` production hoặc nội dung `.env` vào README, mã nguồn hay GitHub. Nếu một key đã bị chia sẻ, hãy thu hồi key cũ và tạo key mới.

## Dữ liệu và tài khoản

Mỗi từ được gắn với tài khoản tạo ra từ đó; các trang danh sách, chi tiết, tìm kiếm, luyện tập và lịch sử chỉ truy vấn dữ liệu của người đang đăng nhập. Xóa một từ sẽ xóa các bản ghi ôn tập liên quan.

Ứng dụng hiện không áp đặt quy tắc độ mạnh mật khẩu. Người dùng vẫn nên tự chọn mật khẩu khó đoán và không dùng chung với dịch vụ khác.

## AI và quyền riêng tư

Khi gọi Gemini, ứng dụng gửi từ tiếng Anh, nghĩa tiếng Việt và từ loại liên quan để tạo nội dung học tập. API key chỉ được đọc ở phía máy chủ từ `GEMINI_API_KEY`, không nhúng vào JavaScript hoặc template. Có giới hạn thời gian giữa các yêu cầu để tránh gọi API liên tục ngoài ý muốn.

Nếu key chưa được cấu hình hoặc Gemini gặp lỗi, ứng dụng báo lỗi thân thiện; các chức năng không dùng AI vẫn hoạt động.

## Kiểm tra tự động

GitHub Actions chạy khi có Pull Request vào `main` hoặc commit mới trên `main`. Workflow cài dependencies rồi chạy:

- `python manage.py check` để kiểm tra cấu hình Django.
- `python manage.py makemigrations --check --dry-run` để phát hiện model thay đổi nhưng chưa có migration.
- `python manage.py collectstatic --noinput` để kiểm tra thu thập static files.
- `python manage.py test` để chạy tests.

## Cập nhật website

1. Tạo branch làm việc từ `main`.
2. Thay đổi mã nguồn, sau đó commit và push branch lên GitHub.
3. Mở Pull Request từ branch đó vào `main`.
4. Chờ CI hoàn tất và nhờ thành viên review theo quy trình nhóm.
5. Merge Pull Request vào `main`.
6. Render build và deploy phiên bản mới theo cấu hình Blueprint.

Các thay đổi ảnh, HTML và CSS cũng cần được commit/push để Render nhận được. Dockerfile chạy `collectstatic` trong quá trình build để đóng gói CSS và hình ảnh trong `vocabulary/static/`.
