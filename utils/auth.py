"""Tiện ích đăng nhập dùng chung cho các route."""
from functools import wraps
from urllib.parse import urlparse
from flask import session, redirect, url_for, request, jsonify


def current_user():
    """Thông tin user rút gọn lưu trong session (None nếu chưa đăng nhập)."""
    return session.get("user")


def safe_next(target):
    """Chỉ cho phép chuyển hướng về đường dẫn nội bộ (chống open-redirect)."""
    if not target:
        return None
    u = urlparse(target)
    if u.scheme or u.netloc or not target.startswith("/") or target.startswith("//"):
        return None
    return target


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user():
            if request.path.startswith("/api/"):
                return jsonify(error="Bạn cần đăng nhập."), 401
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


# =====================================================================
# GIAI ĐOẠN 2: Kiểm tra quyền học tập (dùng chung cho mọi trang học)
# =====================================================================
import secrets
from datetime import datetime, timezone
from flask import flash


def set_learning_session(user_doc):
    """Ghi trạng thái học tập (rút gọn) vào session để navbar hiển thị nhanh, không cần gọi Firestore."""
    from utils.firebase import learning_status
    st = learning_status(user_doc)
    if st["active"]:
        session["learning_until"] = st["expires_at"].timestamp()
    else:
        session.pop("learning_until", None)


def learning_days_left():
    """Số ngày học còn lại theo session (0 nếu chưa kích hoạt / đã hết hạn). Dùng cho navbar."""
    until = session.get("learning_until")
    if not until:
        return 0
    left = until - datetime.now(timezone.utc).timestamp()
    return max(1, -(-int(left) // 86400)) if left > 0 else 0


def check_learning_access(uid):
    """Kiểm tra quyền học từ nguồn chuẩn (Firestore). Trả về (ok, status, reason).
    reason: None | "not_activated" | "expired". Hết hạn -> tự tắt quyền trong Firestore."""
    from utils.firebase import get_user, learning_status, deactivate_if_expired
    user = get_user(uid)
    st = learning_status(user)
    if st["active"]:
        set_learning_session(user)
        return True, st, None
    session.pop("learning_until", None)
    if st["expired"]:
        deactivate_if_expired(uid)
        return False, st, "expired"
    return False, st, "not_activated"


def learning_required(view):
    """Decorator bảo vệ route học tập:
    1) phải đăng nhập  2) learning_activated == True  3) expires_at còn hiệu lực.
    Không đạt -> chuyển về trang nhập mã kèm thông báo."""
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            if request.path.startswith("/api/"):
                return jsonify(error="Bạn cần đăng nhập."), 401
            return redirect(url_for("auth.login", next=request.path))
        try:
            ok, _st, reason = check_learning_access(user["uid"])
        except Exception:
            import traceback
            traceback.print_exc()
            if request.path.startswith("/api/"):
                return jsonify(error="Không kiểm tra được quyền học. Vui lòng thử lại."), 503
            flash("Không kiểm tra được quyền học tập lúc này. Vui lòng thử lại sau.", "error")
            return redirect(url_for("main.index"))
        if not ok:
            msg = ("Mã kích hoạt của bạn đã hết hạn 30 ngày. Hãy nhập mã mới để học tiếp."
                   if reason == "expired"
                   else "Bạn cần nhập mã kích hoạt trên bao bì sản phẩm để vào phần học.")
            if request.path.startswith("/api/"):
                return jsonify(error=msg, code=reason), 403
            flash(msg, "error")
            return redirect(url_for("learning.activate", next=request.path))
        return view(*args, **kwargs)
    return wrapper


# ---- CSRF đơn giản cho form POST ----
def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def csrf_valid(token):
    return bool(token) and secrets.compare_digest(token, session.get("csrf", ""))
