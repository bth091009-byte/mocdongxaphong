"""Firebase Admin: xác thực ID token + đọc/ghi Firestore (chỉ chạy ở server)."""
import json
import os
import re
import threading
import uuid
from datetime import datetime, timedelta, timezone

import firebase_admin
from firebase_admin import auth, credentials, firestore
from werkzeug.utils import secure_filename

import config

_lock = threading.Lock()


def _init():
    with _lock:
        if firebase_admin._apps:
            return
        if config.FIREBASE_CREDENTIALS_JSON:
            cred = credentials.Certificate(json.loads(config.FIREBASE_CREDENTIALS_JSON))
        else:
            cred = credentials.Certificate(config.FIREBASE_CREDENTIALS_FILE)
        firebase_admin.initialize_app(cred)


def db():
    _init()
    return firestore.client()


def verify_id_token(id_token):
    """Trả về dict claims nếu token hợp lệ, ngược lại ném lỗi."""
    _init()
    return auth.verify_id_token(id_token, clock_skew_seconds=10)


def _clean_name(name, email):
    name = re.sub(r"\s+", " ", (name or "")).strip()[:80]
    return name or (email.split("@")[0] if email else "Bạn")


def upsert_user(claims, full_name=""):
    """Tạo hồ sơ user trong Firestore lần đầu; những lần sau chỉ cập nhật last_login_at.
    Các field phân quyền (role, learning_activated...) chỉ do server quyết định."""
    uid = claims["uid"]
    email = claims.get("email", "")
    ref = db().collection("users").document(uid)
    snap = ref.get()
    if snap.exists:
        patch = {"last_login_at": firestore.SERVER_TIMESTAMP}
        old = snap.to_dict()
        if not old.get("photo_url") and claims.get("picture"):
            patch["photo_url"] = claims["picture"]
        ref.update(patch)
    else:
        ref.set({
            "uid": uid,
            "email": email,
            "full_name": _clean_name(claims.get("name") or full_name, email),
            "photo_url": claims.get("picture", ""),
            "role": "buyer",
            "learning_activated": False,
            "created_at": firestore.SERVER_TIMESTAMP,
            "last_login_at": firestore.SERVER_TIMESTAMP,
        })
    return ref.get().to_dict()


# =====================================================================
# GIAI ĐOẠN 2: Mã kích hoạt học tập
# =====================================================================
ACTIVATION_DAYS = 30


class ActivationError(Exception):
    """Lỗi nghiệp vụ khi nhập mã (thông báo hiển thị thẳng cho học sinh)."""


def normalize_code(raw):
    """Chuẩn hóa mã: bỏ khoảng trắng, viết hoa. Chỉ giữ chữ, số và dấu gạch ngang."""
    code = re.sub(r"\s+", "", (raw or "")).upper()
    if not re.fullmatch(r"[A-Z0-9\-]{4,40}", code):
        return ""
    return code


def _utcnow():
    return datetime.now(timezone.utc)


def get_user(uid):
    snap = db().collection("users").document(uid).get()
    return snap.to_dict() if snap.exists else None


def learning_status(user):
    """Từ hồ sơ user trong Firestore -> dict trạng thái học tập.
    active: còn quyền học | expired: từng kích hoạt nhưng đã hết hạn | days_left: số ngày còn lại."""
    user = user or {}
    exp = user.get("expires_at")
    if not user.get("learning_activated") or not exp:
        return {"active": False, "expired": False, "days_left": 0, "expires_at": None}
    left = (exp - _utcnow()).total_seconds()
    if left <= 0:
        return {"active": False, "expired": True, "days_left": 0, "expires_at": exp}
    return {"active": True, "expired": False,
            "days_left": max(1, -(-int(left) // 86400)),
            "expires_at": exp}


def deactivate_if_expired(uid):
    """Hết hạn -> tự tắt quyền học (learning_activated=False, role về buyer). Trả về True nếu vừa khóa."""
    ref = db().collection("users").document(uid)
    snap = ref.get()
    if not snap.exists:
        return False
    u = snap.to_dict()
    st = learning_status(u)
    if u.get("learning_activated") and st["expired"]:
        ref.update({"learning_activated": False, "role": "buyer"})
        return True
    return False


def redeem_code(uid, raw_code):
    """Dùng mã kích hoạt trong 1 transaction (2 người nhập cùng lúc thì chỉ 1 người thành công).
    Ném ActivationError nếu mã sai / đã dùng / hết hạn / user đang còn hạn."""
    code = normalize_code(raw_code)
    if not code:
        raise ActivationError("Mã chưa đúng định dạng. Hãy nhập lại đúng mã trên bao bì sản phẩm.")

    client = db()
    code_ref = client.collection("activation_codes").document(code)
    user_ref = client.collection("users").document(uid)

    @firestore.transactional
    def _run(tx):
        user_snap = user_ref.get(transaction=tx)
        if not user_snap.exists:
            raise ActivationError("Không tìm thấy tài khoản. Hãy đăng xuất rồi đăng nhập lại.")
        code_snap = code_ref.get(transaction=tx)
        if not code_snap.exists:
            raise ActivationError("Mã không tồn tại. Hãy kiểm tra lại mã trên bao bì sản phẩm.")

        c = code_snap.to_dict()
        now = _utcnow()
        u = user_snap.to_dict()

        if c.get("is_used"):
            if c.get("used_by") == uid:
                raise ActivationError("Bạn đã dùng mã này rồi.")
            raise ActivationError("Mã này đã được sử dụng bởi tài khoản khác.")

        c_exp = c.get("expires_at")
        if c_exp and c_exp <= now:
            raise ActivationError("Mã này đã hết hạn.")

        st = learning_status(u)
        if st["active"]:
            raise ActivationError(
                f"Tài khoản của bạn đang còn {st['days_left']} ngày học. Hãy dùng mã mới sau khi hết hạn.")

        expires = now + timedelta(days=ACTIVATION_DAYS)
        tx.update(code_ref, {
            "is_used": True,
            "used_by": uid,
            "activated_at": now,
            "expires_at": expires,
        })
        tx.update(user_ref, {
            "learning_activated": True,
            "activation_code": code,
            "activated_at": now,
            "expires_at": expires,
            "role": "student",
        })
        return {**u, "learning_activated": True, "activation_code": code,
                "activated_at": now, "expires_at": expires, "role": "student"}

    return _run(client.transaction())


# =====================================================================
# GIAI ĐOẠN 3: Tiến độ học EDP (collection learning_progress, document id = uid)
# =====================================================================
TOTAL_STEPS = 5
ALLOWED_IMG_EXT = {"jpg", "jpeg", "png", "webp"}
MAX_IMG_BYTES = 5 * 1024 * 1024  # 5 MB


class UploadError(Exception):
    """Lỗi khi tải ảnh sản phẩm lên."""


def get_progress(uid):
    """Trả về dict tiến độ đầy đủ (bao gồm quiz từng bước và evaluation Bước 5)."""
    snap = db().collection("learning_progress").document(uid).get()
    d = snap.to_dict() if snap.exists else {}
    steps = sorted({int(s) for s in d.get("completed_steps", []) if 1 <= int(s) <= TOTAL_STEPS})
    return {
        "completed_steps": steps,
        "completed_count": len(steps),
        "percent": round(len(steps) * 100 / TOTAL_STEPS),
        "completed_all": len(steps) == TOTAL_STEPS,
        "step_times": d.get("step_times", {}),
        "quizzes": d.get("quizzes", {}),
        "evaluation": d.get("evaluation", {}),
        "completed_at": d.get("completed_at"),
    }


def save_step_progress(uid, step, quiz_result=None, activation_code=""):
    """Lưu kết quả trắc nghiệm (nếu có) và đánh dấu hoàn thành 1 bước."""
    ref = db().collection("learning_progress").document(uid)
    now = _utcnow()

    @firestore.transactional
    def _run(tx):
        snap = ref.get(transaction=tx)
        d = snap.to_dict() if snap.exists else {}
        done = {int(s) for s in d.get("completed_steps", [])}
        times = dict(d.get("step_times", {}))
        quizzes = dict(d.get("quizzes", {}))

        if step not in done:
            done.add(step)
            times[str(step)] = now
        if quiz_result is not None:
            quizzes[str(step)] = {**quiz_result, "updated_at": now}

        patch = {
            "uid": uid,
            "completed_steps": sorted(done),
            "step_times": times,
            "quizzes": quizzes,
            "updated_at": now,
        }
        if not d.get("started_at"):
            patch["started_at"] = now
        if activation_code:
            patch["activation_code"] = activation_code
        if len(done) == TOTAL_STEPS and not d.get("completed_at"):
            patch["completed_at"] = now
        tx.set(ref, patch, merge=True)

    _run(db().transaction())
    return get_progress(uid)


def mark_step_complete(uid, step, activation_code=""):
    """Giữ tương thích ngược nếu nơi khác gọi hàm cũ."""
    return save_step_progress(uid, step, quiz_result=None, activation_code=activation_code)


def upload_product_image(uid, file_storage, static_folder):
    """Kiểm tra định dạng jpg/png/webp <= 5MB và lưu vào static/uploads/edp/.
    Trả về đường dẫn URL tương đối (/static/uploads/edp/...)."""
    if not file_storage or not getattr(file_storage, "filename", ""):
        raise UploadError("Vui lòng chọn ảnh sản phẩm của bạn.")

    filename = secure_filename(file_storage.filename)
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_IMG_EXT:
        raise UploadError("Chỉ chấp nhận ảnh định dạng JPG, PNG hoặc WEBP.")

    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size <= 0:
        raise UploadError("File ảnh bị rỗng, vui lòng chọn lại.")
    if size > MAX_IMG_BYTES:
        raise UploadError("Dung lượng ảnh vượt quá 5 MB. Hãy nén nhẹ ảnh trước khi tải lên.")

    upload_dir = os.path.join(static_folder, "uploads", "edp")
    os.makedirs(upload_dir, exist_ok=True)
    saved_name = f"{uid[:16]}_{uuid.uuid4().hex[:10]}.{ext}"
    file_storage.save(os.path.join(upload_dir, saved_name))
    return f"/static/uploads/edp/{saved_name}"


def save_evaluation_and_feedback(uid, payload, quiz_result=None, activation_code=""):
    """Lưu phiếu đánh giá Bước 5 (feedback + ảnh + 2 bảng rubric) và hoàn thành Bước 5."""
    ref = db().collection("learning_progress").document(uid)
    now = _utcnow()

    @firestore.transactional
    def _run(tx):
        snap = ref.get(transaction=tx)
        d = snap.to_dict() if snap.exists else {}
        done = {int(s) for s in d.get("completed_steps", [])}
        times = dict(d.get("step_times", {}))
        quizzes = dict(d.get("quizzes", {}))

        done.add(TOTAL_STEPS)
        times.setdefault(str(TOTAL_STEPS), now)
        if quiz_result is not None:
            quizzes[str(TOTAL_STEPS)] = {**quiz_result, "updated_at": now}

        eval_doc = {**payload, "submitted_at": now}
        patch = {
            "uid": uid,
            "completed_steps": sorted(done),
            "step_times": times,
            "quizzes": quizzes,
            "evaluation": eval_doc,
            "updated_at": now,
        }
        if not d.get("started_at"):
            patch["started_at"] = now
        if activation_code:
            patch["activation_code"] = activation_code
        if len(done) == TOTAL_STEPS and not d.get("completed_at"):
            patch["completed_at"] = now
        tx.set(ref, patch, merge=True)

    _run(db().transaction())
    return get_progress(uid)


def get_user_edp_summary(uid):
    """Lấy toàn bộ hồ sơ học tập EDP để hiển thị trang tổng kết."""
    return {
        "user": get_user(uid) or {},
        "progress": get_progress(uid),
    }