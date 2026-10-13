# Vocabulary Notebook EN–VI

Ứng dụng web nhỏ để lưu từ vựng tiếng Anh, nghĩa tiếng Việt và lịch sử ôn tập. Dự án được làm theo các mốc đầu của môn 72ITDS30103; giai đoạn hiện tại tập trung vào CRUD, Docker/Compose và chuẩn bị triển khai HTTPS. Tính năng AI tạo câu ví dụ và ghi chú cách dùng nằm ở mốc sau.

## Chạy trong VS Code

### Cần có

- Visual Studio Code và Git.
- Docker Desktop đã mở và báo Docker Engine đang chạy.
- VS Code extensions được đề xuất: Python, Docker, Dev Containers, GitHub Pull Requests and Issues.

Có thể mở thư mục dự án trong VS Code rồi chạy **Terminal → Run Task → Start local stack**, hoặc chạy lệnh sau trong terminal tích hợp:

```powershell
docker compose up --build
```

Mở <http://localhost:8000>. Khi chạy lần đầu, Docker cần tải image Python và PostgreSQL. Compose tự tạo database local, áp dụng migrations, rồi chạy web app. Dữ liệu database được giữ trong volume `postgres_data` qua các lần dừng/mở lại.

Muốn mở Python code bên trong container, dùng `Ctrl+Shift+P` → **Dev Containers: Reopen in Container**. Trong VS Code, chọn **Terminal → Run Task → Follow web logs** để xem log.

Để dừng app, nhấn `Ctrl+C`, hoặc chạy:

```powershell
docker compose down
```

Để xóa cả dữ liệu PostgreSQL local (thao tác này không thể khôi phục dữ liệu đã xóa):

```powershell
docker compose down --volumes
```

## Những gì có trong bản này

- Danh sách, tìm kiếm, thêm, sửa và xóa từ vựng.
- Chi tiết một từ và lịch sử ôn tập; thêm kết quả ôn tập và xóa bản ghi.
- Dockerfile, `.dockerignore` và Compose gồm Django/PostgreSQL để chạy từ clone sạch bằng một lệnh.
- Cấu hình Render Blueprint và biến môi trường để chuẩn bị URL HTTPS; database production dự kiến là Supabase PostgreSQL.
- Django admin ở `/admin/` (tạo tài khoản quản trị bằng `python manage.py createsuperuser` khi cần).

## Cấu hình và secrets

Compose chạy được mà không cần file `.env`, dùng thông tin mặc định chỉ dành cho môi trường local. Nếu muốn tùy chỉnh, copy `.env.example` thành `.env`. `.env` được Git bỏ qua.

Trên Render, đặt `DATABASE_URL` bằng connection string PostgreSQL của Supabase, giữ `DEBUG=0`, và sinh một `SECRET_KEY` riêng trong phần Environment. Không commit `.env`, connection string hay API key. Chưa cần API key ở giai đoạn này vì tính năng AI thuộc mốc sau.

## Chuẩn bị HTTPS trên Render + Supabase

1. Đưa repository của nhóm lên GitHub và kết nối repository đó với Render.
2. Tạo project PostgreSQL trên Supabase; lấy connection string PostgreSQL có SSL.
3. Tạo Web Service từ Blueprint `render.yaml`. Render đọc Dockerfile và cấp URL HTTPS `onrender.com`.
4. Điền `DATABASE_URL` trong Render Dashboard. `SECRET_KEY` được Blueprint tạo tự động; giữ `DEBUG=0`.
5. Mở URL Render và kiểm tra trang chính. Free Web Service có thể ngủ khi không có truy cập; mở URL trước buổi demo.

Blueprint không chứa credential thật. Việc tạo dịch vụ cloud cần đăng nhập vào tài khoản GitHub, Render và Supabase của nhóm. Không thêm thẻ thanh toán nếu nền tảng yêu cầu payment method; kiểm tra fallback theo yêu cầu môn học.

## Biến môi trường

| Tên | Local Compose | Production |
| --- | --- | --- |
| `DATABASE_URL` | Compose nối đến service `db` | Supabase PostgreSQL connection string |
| `SECRET_KEY` | Giá trị mặc định dùng riêng cho dev hoặc `.env` | Secret riêng do Render sinh |
| `DEBUG` | `1` | `0` |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Host Render được thêm tự động; có thể cấu hình thêm |

## Cấu trúc chính

```text
config/                 Django settings và URL gốc
vocabulary/             models, forms, views, migrations và templates
.devcontainer/          Mở môi trường Compose từ VS Code
.vscode/                Extensions và tasks dùng trong VS Code
Dockerfile              Image ứng dụng
compose.yaml            App + PostgreSQL cho phát triển local
render.yaml             Render Blueprint cho dịch vụ web
```

## Tiến độ theo mốc môn học

- Tuần 2: chuẩn bị dự án để đưa lên repo nhóm; bảo vệ `main`, pull request và phân quyền cần thực hiện trên GitHub của nhóm.
- Tuần 3: có Dockerfile và `.dockerignore`.
- Tuần 4: Compose khởi chạy app và database bằng một lệnh.
- Tuần 5: có cấu hình triển khai Render và kết nối Supabase; URL HTTPS thật cần được tạo trong tài khoản cloud của nhóm.

### Quy ước làm việc nhóm trên GitHub

Khi repository nhóm đã được clone và kết nối:

1. Tạo branch cho một thay đổi, ví dụ `feature/add-vocabulary-crud`.
2. Commit thay đổi trên branch đó và push lên GitHub.
3. Mở pull request vào `main`, giải thích thay đổi và nhờ thành viên còn lại review.
4. Merge sau khi được review. Không push trực tiếp lên `main`.

Trong Settings → Branches của repository, bật rule cho `main` để yêu cầu pull request và tối thiểu một approval. Việc bật rule cần quyền quản trị repository.

## Công nghệ

Python, Django, PostgreSQL, Docker Compose, Render, Supabase, HTML/CSS và GitHub.
