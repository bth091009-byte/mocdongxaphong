from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
import config
from utils.auth import current_user, safe_next, set_learning_session, learning_days_left, csrf_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.app_context_processor
def inject_user():
    days = learning_days_left() if current_user() else 0
    return {
        "current_user": current_user(),
        "firebase_config": config.FIREBASE_WEB_CONFIG,
        "learning_active": days > 0,      # hiện nút "Học EDP" khi đã kích hoạt và còn hạn
        "learning_days_left": days,
        "csrf_token": csrf_token,
    }


@auth_bp.route("/dang-nhap")
def login():
    nxt = safe_next(request.args.get("next"))
    if current_user():
        return redirect(nxt or url_for("main.index"))
    return render_template("login.html", next_url=nxt or "")


@auth_bp.route("/api/auth/session", methods=["POST"])
def create_session():
    """Nhận Firebase ID token từ trình duyệt -> xác thực -> lưu user -> mở phiên đăng nhập."""
    data = request.get_json(silent=True) or {}
    id_token = data.get("id_token", "")
    if not id_token:
        return jsonify(error="Thiếu thông tin đăng nhập."), 400
    try:
        from utils.firebase import verify_id_token, upsert_user
        claims = verify_id_token(id_token)
        user = upsert_user(claims, full_name=data.get("full_name", ""))
    except Exception:
        import traceback
        traceback.print_exc()
        return jsonify(error="Không xác thực được tài khoản. Vui lòng thử lại."), 401

    session.clear()
    session.permanent = True
    session["user"] = {
        "uid": user["uid"],
        "email": user.get("email", ""),
        "full_name": user.get("full_name", ""),
        "photo_url": user.get("photo_url", ""),
    }
    set_learning_session(user)  # đăng nhập lại vẫn nhận đúng trạng thái học tập còn hạn
    return jsonify(ok=True, redirect=safe_next(data.get("next")) or url_for("main.index"))


@auth_bp.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify(ok=True, redirect=url_for("main.index"))
