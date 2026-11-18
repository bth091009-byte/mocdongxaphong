"""Tạo mã kích hoạt học tập trong Firestore.
Chạy từ thư mục gốc project:   python -m scripts.tao_ma 20        (tạo 20 mã)
                               python -m scripts.tao_ma 5 MD      (tiền tố MD -> MD-XXXX-XXXX)
In danh sách mã ra màn hình và lưu vào file ma_kich_hoat.txt để in lên bao bì."""
import secrets
import sys
from datetime import datetime, timezone

from firebase_admin import firestore
from utils.firebase import db

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # bỏ O/0/I/1 cho dễ đọc


def gen(prefix):
    part = lambda: "".join(secrets.choice(ALPHABET) for _ in range(4))
    return f"{prefix}-{part()}-{part()}"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    prefix = (sys.argv[2] if len(sys.argv) > 2 else "MD").upper()
    col = db().collection("activation_codes")
    made = []
    while len(made) < n:
        code = gen(prefix)
        ref = col.document(code)
        if ref.get().exists:
            continue
        ref.set({
            "code": code,
            "is_used": False,
            "used_by": None,
            "activated_at": None,
            "expires_at": None,   # được đặt = lúc kích hoạt + 30 ngày
            "created_at": firestore.SERVER_TIMESTAMP,
        })
        made.append(code)
    with open("ma_kich_hoat.txt", "a", encoding="utf-8") as f:
        f.write(f"# {datetime.now(timezone.utc).isoformat()}\n" + "\n".join(made) + "\n")
    print("\n".join(made))
    print(f"\nĐã tạo {len(made)} mã (lưu thêm vào ma_kich_hoat.txt)")


if __name__ == "__main__":
    main()
