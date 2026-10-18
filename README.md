# Vocabulary Notebook EN–VI

Ứng dụng web quản lý từ vựng Anh–Việt và lịch sử ôn tập, được thực hiện cho môn **72ITDS30103 – Software Development Platforms**.

## Tổng quan dự án

Vocabulary Notebook EN–VI giúp người học xây dựng sổ tay từ vựng cá nhân. Người dùng có thể thêm từ tiếng Anh, nghĩa tiếng Việt, từ loại và ghi chú; sau đó lưu kết quả mỗi lần ôn để theo dõi quá trình học.

Dự án hiện đã hoàn thành các mốc đến hết tuần 5:

- Quản lý từ vựng: xem danh sách, tìm kiếm, thêm, sửa và xóa.
- Quản lý lịch sử ôn tập cho từng từ.
- Chạy ứng dụng và PostgreSQL local bằng Docker Compose.
- Triển khai ứng dụng bằng Docker trên Render với HTTPS.
- Lưu dữ liệu production trên Supabase PostgreSQL.
- Tự động triển khai lại website khi có commit mới trên branch `main`.

Tính năng AI tạo câu ví dụ và ghi chú cách dùng sẽ được phát triển ở mốc tiếp theo của môn học.

## Thành viên

| Họ và tên | Mã sinh viên |
| --- | --- |
| Nguyễn Thành Trí | 2474802010400 |
| Phạm Thị Khánh Ngân | 2474802016786 |

## Website và liên kết

| Nội dung | Liên kết |
| --- | --- |
| Website đang hoạt động | [vocabulary-notebook-en-vn.onrender.com](https://vocabulary-notebook-en-vn.onrender.com) |
| Kiểm tra trạng thái dịch vụ | [Health check](https://vocabulary-notebook-en-vn.onrender.com/health/) |
| GitHub repository | [trithanh1577/vocabulary-notebook-en-vn](https://github.com/trithanh1577/vocabulary-notebook-en-vn) |
| Pull requests | [GitHub Pull Requests](https://github.com/trithanh1577/vocabulary-notebook-en-vn/pulls) |
| Render Dashboard | [dashboard.render.com](https://dashboard.render.com/) |
| Supabase Dashboard | [supabase.com/dashboard](https://supabase.com/dashboard) |
| Website local | [localhost:8000](http://localhost:8000) |

> Render sử dụng gói miễn phí nên website có thể mất một lúc để khởi động lại sau thời gian không có truy cập.

## Công nghệ sử dụng

- Python và Django.
- HTML và CSS.
- PostgreSQL.
- Docker và Docker Compose.
- GitHub để quản lý mã nguồn và Pull Request.
- Render để triển khai web service HTTPS.
- Supabase để cung cấp PostgreSQL trên cloud.
- Visual Studio Code để phát triển và chạy dự án.

## Chạy dự án trên Visual Studio Code

### Yêu cầu

- Visual Studio Code.
- Git.
- Docker Desktop đang chạy.

Mở thư mục dự án trong Visual Studio Code, sau đó chạy trong terminal:

```powershell
docker compose up --build
```

Truy cập [http://localhost:8000](http://localhost:8000). Docker Compose sẽ tự khởi động Django, PostgreSQL và áp dụng migrations.

Để dừng ứng dụng:

```powershell
docker compose down
```

## Biến môi trường

| Biến | Mục đích |
| --- | --- |
| `DATABASE_URL` | Chuỗi kết nối PostgreSQL local hoặc Supabase |
| `SECRET_KEY` | Khóa bí mật của Django |
| `DEBUG` | Bật chế độ phát triển ở local, tắt trên production |
| `ALLOWED_HOSTS` | Danh sách host được Django cho phép |

Không commit file `.env`, mật khẩu database, connection string hoặc API key lên GitHub.

## Cấu trúc dự án

```text
config/                     Cấu hình chung của Django
vocabulary/                 Ứng dụng quản lý từ vựng và lịch sử ôn tập
vocabulary/templates/       Giao diện HTML
vocabulary/static/          CSS và tài nguyên giao diện
.devcontainer/              Cấu hình Dev Container cho VS Code
.github/                    Mẫu Pull Request và cấu hình GitHub
.vscode/                    Extensions và tasks cho Visual Studio Code
Dockerfile                  Cấu hình image của ứng dụng
compose.yaml                Django và PostgreSQL cho môi trường local
render.yaml                 Blueprint triển khai trên Render
requirements.txt            Các thư viện Python
```

## Quy trình cập nhật website

1. Tạo một branch mới từ `main`.
2. Thực hiện thay đổi và commit trên branch đó.
3. Push branch lên GitHub và tạo Pull Request vào `main`.
4. Thành viên còn lại review và approve Pull Request.
5. Merge Pull Request vào `main`.
6. Render tự động build và cập nhật website từ branch `main`.

## CI/CD (tuần 6)

GitHub Actions chạy tự động khi tạo Pull Request vào `main` và khi có commit mới trên `main`. Quy trình cài thư viện, kiểm tra cấu hình Django, kiểm tra migrations và chạy bộ kiểm thử.

Render chỉ bắt đầu triển khai commit trên `main` sau khi các bước kiểm tra CI hoàn tất thành công. Vì vậy, hãy chờ GitHub Actions báo thành công trước khi merge Pull Request.
