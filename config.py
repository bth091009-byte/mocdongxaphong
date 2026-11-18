import os
from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# ---- Firebase ----
# Cấu hình Web (public, dùng cho Firebase JS SDK ở trình duyệt)
FIREBASE_WEB_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY", ""),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN", ""),
    "projectId": os.getenv("FIREBASE_PROJECT_ID", ""),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET", ""),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID", ""),
    "appId": os.getenv("FIREBASE_APP_ID", ""),
}
# Khóa Service Account (BÍ MẬT, chỉ dùng ở server). Dùng 1 trong 2 cách:
FIREBASE_CREDENTIALS_FILE = os.getenv("FIREBASE_CREDENTIALS_FILE", "serviceAccountKey.json")
FIREBASE_CREDENTIALS_JSON = os.getenv("FIREBASE_CREDENTIALS_JSON", "")  # nội dung JSON (khi deploy)

SESSION_DAYS = int(os.getenv("SESSION_DAYS", "7"))

BRAND = "Mộc Đông"
SLOGAN = "Làm sạch & Nuôi dưỡng"

# Dễ mở rộng: thêm sản phẩm mới vào danh sách này
PRODUCTS = [{
    "slug": "yen-mach-nho",
    "name": "Xà phòng Yến mạch & Nho",
    "weight": "100g",
    "type": "Xà phòng handmade – Organic",
    "origin": "Made in Vietnam",
    "tags": ["Handmade", "Organic", "Made in Vietnam"],
    "benefit": "Làm sạch nhẹ nhàng và nuôi dưỡng da",
    "intro": "Thanh xà phòng được làm thủ công theo phương pháp xà phòng hóa truyền thống, kết hợp giữa sự sạch sẽ và sự dịu dàng. Không chỉ làm sạch bề mặt da, mà còn mang lại cảm giác mềm mại, dễ chịu sau mỗi lần sử dụng.",
    "benefits": [
        "Làm sạch nhẹ nhàng, không gây khô căng",
        "Hỗ trợ duy trì độ ẩm tự nhiên cho da",
        "Giúp da mềm mịn nhờ bột yến mạch",
        "Hương nho dịu nhẹ, thanh mát, không nồng",
    ],
    "suitable": "Phù hợp với da thường đến da khô, và những ai muốn tìm một lựa chọn làm sạch ít hóa chất mạnh.",
    "ingredients": [
        {"name": "Dầu dừa", "role": "Tạo bọt tốt, làm sạch hiệu quả"},
        {"name": "Dầu ô liu", "role": "Nuôi dưỡng, giúp da mềm mại và ẩm mượt"},
        {"name": "Bột yến mạch", "role": "Làm dịu da, tạo cảm giác mịn màng khi dùng"},
        {"name": "Tinh dầu nho", "role": "Mang hương thơm tự nhiên, thanh thoát"},
        {"name": "Nước cất", "role": "Nguyên liệu nền, tinh khiết"},
        {"name": "NaOH", "role": "Đã được xà phòng hóa hoàn toàn, không còn kiềm dư"},
    ],
    "ingredients_note": "Tất cả nguyên liệu đều được lựa chọn kỹ lưỡng và cân đối tỉ lệ để tạo nên thanh xà phòng vừa đủ sạch, vừa đủ dịu nhẹ.",
    "feel": "Khi tạo bọt, xà phòng cho lớp bọt mịn, không quá dày đặc. Hương nho thoang thoảng, dễ chịu. Sau khi rửa đi, da có cảm giác sạch sẽ nhưng vẫn giữ được độ mềm, không bị căng hay khô ráp như một số loại xà phòng mạnh.",
    "shelf_life": "12 tháng kể từ ngày sản xuất",
    "storage_short": "Nơi khô ráo, thoáng mát, tránh nắng trực tiếp và không ngâm lâu trong nước",
    "audience": "Người lớn, da thường – da khô. Phụ nữ mang thai và trẻ nhỏ nên thử trên vùng da nhỏ trước khi dùng toàn thân",
}]