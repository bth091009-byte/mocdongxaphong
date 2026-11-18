"""Giai đoạn 2: kích hoạt học tập bằng mã trên bao bì sản phẩm.
Giai đoạn 3: module học 5 bước EDP (mọi route /hoc-edp* đều được learning_required bảo vệ)."""
import base64
import time
from flask import (Blueprint, render_template, request, redirect, url_for,
                   flash, session, abort)
import config
from utils.auth import (login_required, learning_required, current_user, safe_next,
                        check_learning_access, set_learning_session, csrf_valid)
from utils.firebase import (redeem_code, get_user, learning_status, ActivationError,
                            UploadError, get_progress, save_step_progress,
                            save_evaluation_and_feedback, get_user_edp_summary)
from utils.edp_content import (STEPS, TOTAL_STEPS, CALC, get_step,
                               FEEDBACK_QUESTIONS, RUBRIC_TABLE_1, RUBRIC_TABLE_2, grade)

learning_bp = Blueprint("learning", __name__)

MAX_FAILS = 5          # nhập sai tối đa 5 lần
LOCK_SECONDS = 300     # rồi khóa 5 phút (chống dò mã)

ALLOWED_IMAGE_MIMES = {
    "image/jpeg": "image/jpeg",
    "image/jpg": "image/jpeg",
    "image/png": "image/png",
    "image/webp": "image/webp",
}
MAX_IMAGE_BYTES = 850 * 1024  # giữ an toàn dưới giới hạn 1 MB của document Firestore


def _photo_to_data_url(photo):
    """Chuyển ảnh thành chuỗi Data URL Base64 để lưu thẳng vào Firestore (tương thích Vercel read-only)."""
    if not photo or not photo.filename:
        return None
    mime = ALLOWED_IMAGE_MIMES.get((photo.mimetype or "").lower())
    if not mime:
        raise UploadError("Chỉ hỗ trợ file ảnh định dạng JPG, PNG hoặc WEBP.")
    raw = photo.read()
    if not raw:
        raise UploadError("File ảnh trống hoặc không đọc được, vui lòng chọn lại.")
    if len(raw) > MAX_IMAGE_BYTES:
        raise UploadError("Ảnh sau khi nén vẫn lớn hơn 850 KB. Vui lòng chọn ảnh nhẹ hơn.")
    encoded = base64.b64encode(raw).decode("ascii")
    return f"data:{mime};base64,{encoded}"


@learning_bp.context_processor
def inject_brand():
    return {"brand": config.BRAND, "slogan": config.SLOGAN}


def _locked_seconds():
    until = session.get("code_lock_until", 0)
    return max(0, int(until - time.time()))


@learning_bp.route("/kich-hoat-hoc-tap", methods=["GET", "POST"])
@login_required
def activate():
    user = current_user()
    nxt = safe_next(request.values.get("next")) or ""
    error = None

    if request.method == "POST":
        wait = _locked_seconds()
        if not csrf_valid(request.form.get("csrf")):
            error = "Phiên làm việc đã hết hạn. Hãy tải lại trang và thử lại."
        elif wait:
            error = f"Bạn nhập sai quá nhiều lần. Hãy thử lại sau {-(-wait // 60)} phút."
        else:
            try:
                new_user = redeem_code(user["uid"], request.form.get("code", ""))
            except ActivationError as e:
                session["code_fails"] = session.get("code_fails", 0) + 1
                if session["code_fails"] >= MAX_FAILS:
                    session["code_lock_until"] = time.time() + LOCK_SECONDS
                    session["code_fails"] = 0
                error = str(e)
            except Exception:
                import traceback
                traceback.print_exc()
                error = "Hệ thống đang bận, vui lòng thử lại sau ít phút."
            else:
                session.pop("code_fails", None)
                session.pop("code_lock_until", None)
                set_learning_session(new_user)
                flash("Kích hoạt thành công! Bạn có 30 ngày để học làm xà phòng cùng Mộc Đông.", "ok")
                return redirect(nxt or url_for("learning.edp_home"))

    try:
        _ok, status, reason = check_learning_access(user["uid"])
    except Exception:
        status, reason = {"active": False, "expired": False, "days_left": 0, "expires_at": None}, None

    return render_template("activate.html", error=error, status=status, reason=reason,
                           next_url=nxt, locked=_locked_seconds())


# =====================================================================
# GIAI ĐOẠN 3: Module học EDP
# =====================================================================
def _first_unfinished(progress):
    done = set(progress["completed_steps"])
    for n in range(1, TOTAL_STEPS + 1):
        if n not in done:
            return n
    return TOTAL_STEPS


def _unlocked(n, progress):
    done = set(progress["completed_steps"])
    return n == 1 or (n - 1) in done or n in done


def _status():
    return learning_status(get_user(current_user()["uid"]))


def _grade_quiz(step, form):
    """Chấm điểm trắc nghiệm phía server. Ném ValueError nếu chọn thiếu câu."""
    questions = step.get("quiz", [])
    if not questions:
        return None
    answers = []
    score = 0
    for idx, q in enumerate(questions):
        raw = form.get(f"quiz_{idx}")
        if raw is None or not raw.isdigit():
            raise ValueError(f"Bạn chưa trả lời Câu {idx + 1} trong phần trắc nghiệm.")
        choice = int(raw)
        if not (0 <= choice < len(q["options"])):
            raise ValueError(f"Lựa chọn ở Câu {idx + 1} không hợp lệ.")
        answers.append(choice)
        if choice == q["correct"]:
            score += 1
    return {"answers": answers, "score": score, "total": len(questions)}


def _parse_rubric(table, form):
    """Đọc điểm thang 1-4 của từng tiêu chí trong 1 bảng rubric."""
    scores = {}
    total = 0
    for c in table["criteria"]:
        raw = form.get(f"{table['id']}_{c['key']}")
        if raw not in {"1", "2", "3", "4"}:
            raise ValueError(f"Vui lòng chấm đủ tiêu chí “{c['label']}” trong {table['title']}.")
        val = int(raw)
        scores[c["key"]] = val
        total += val
    return {"scores": scores, "total": total, "max": table["max"], "grade": grade(total)}


@learning_bp.route("/hoc-edp")
@learning_required
def edp_home():
    uid = current_user()["uid"]
    progress = get_progress(uid)
    done = set(progress["completed_steps"])
    steps = [{**s, "done": s["n"] in done, "unlocked": _unlocked(s["n"], progress)} for s in STEPS]
    return render_template("edp_home.html", status=_status(), progress=progress, steps=steps,
                           next_step=_first_unfinished(progress), total=TOTAL_STEPS)


@learning_bp.route("/hoc-edp/buoc/<int:n>")
@learning_required
def edp_step(n):
    step = get_step(n)
    if not step:
        abort(404)
    progress = get_progress(current_user()["uid"])
    if not _unlocked(n, progress):
        flash(f"Hãy hoàn thành Bước {n - 1} trước khi sang Bước {n} nhé!", "error")
        return redirect(url_for("learning.edp_step", n=_first_unfinished(progress)))

    saved_quiz = progress["quizzes"].get(str(n), {})
    saved_eval = progress["evaluation"] if n == TOTAL_STEPS else {}

    return render_template(
        "edp_step.html",
        status=_status(),
        progress=progress,
        step=step,
        steps=STEPS,
        total=TOTAL_STEPS,
        calc=CALC,
        is_done=n in progress["completed_steps"],
        saved_quiz=saved_quiz,
        saved_eval=saved_eval,
        feedback_questions=FEEDBACK_QUESTIONS,
        rubric_1=RUBRIC_TABLE_1,
        rubric_2=RUBRIC_TABLE_2,
        prev_step=get_step(n - 1),
        next_step=get_step(n + 1),
    )


@learning_bp.route("/hoc-edp/buoc/<int:n>/hoan-thanh", methods=["POST"])
@learning_bp.route("/hoc-edp/buoc/<int:n>/submit", methods=["POST"])
@learning_required
def edp_complete(n):
    step = get_step(n)
    if not step:
        abort(404)
    if not csrf_valid(request.form.get("csrf")):
        flash("Phiên làm việc đã hết hạn. Hãy tải lại trang và thử lại.", "error")
        return redirect(url_for("learning.edp_step", n=n))

    uid = current_user()["uid"]
    progress = get_progress(uid)
    if not _unlocked(n, progress):
        flash(f"Hãy hoàn thành Bước {n - 1} trước nhé!", "error")
        return redirect(url_for("learning.edp_step", n=_first_unfinished(progress)))

    try:
        quiz_result = _grade_quiz(step, request.form)
    except ValueError as e:
        flash(str(e), "error")
        return redirect(url_for("learning.edp_step", n=n) + "#quiz-sec")

    user = get_user(uid) or {}
    code = user.get("activation_code", "")

    if n < TOTAL_STEPS:
        try:
            save_step_progress(uid, n, quiz_result=quiz_result, activation_code=code)
        except Exception:
            import traceback
            traceback.print_exc()
            flash("Chưa lưu được tiến độ, vui lòng thử lại.", "error")
            return redirect(url_for("learning.edp_step", n=n))

        score_txt = f" (Trắc nghiệm: {quiz_result['score']}/{quiz_result['total']} câu đúng)" if quiz_result else ""
        flash(f"Đã hoàn thành Bước {n}: {step['title']}{score_txt}.", "ok")
        return redirect(url_for("learning.edp_step", n=n + 1))

    try:
        feedback_answers = {}
        for fq in FEEDBACK_QUESTIONS:
            val = (request.form.get(fq["key"]) or "").strip()[:fq["maxlength"]]
            if fq["required"] and not val:
                raise ValueError(f"Vui lòng điền mục “{fq['label']}”.")
            feedback_answers[fq["key"]] = val

        r1 = _parse_rubric(RUBRIC_TABLE_1, request.form)
        r2 = _parse_rubric(RUBRIC_TABLE_2, request.form)

        existing_img = (progress.get("evaluation") or {}).get("image_url", "")
        photo = request.files.get("product_image")
        if photo and photo.filename:
            image_url = _photo_to_data_url(photo)
        elif existing_img:
            image_url = existing_img
        else:
            raise UploadError("Vui lòng tải lên 1 ảnh chụp bánh xà phòng thành phẩm của bạn.")

        payload = {
            "feedback_answers": feedback_answers,
            "image_url": image_url,
            "rubric_1": r1,
            "rubric_2": r2,
            "combined_total": r1["total"] + r2["total"],
            "combined_max": r1["max"] + r2["max"],
        }
        progress = save_evaluation_and_feedback(uid, payload, quiz_result=quiz_result, activation_code=code)
    except (ValueError, UploadError) as e:
        flash(str(e), "error")
        return redirect(url_for("learning.edp_step", n=n) + "#eval-sec")
    except Exception:
        import traceback
        traceback.print_exc()
        flash("Chưa lưu được phiếu đánh giá, vui lòng thử lại.", "error")
        return redirect(url_for("learning.edp_step", n=n))

    flash("Chúc mừng! Bạn đã hoàn thành cả 5 bước EDP và lưu hồ sơ sản phẩm 🎉", "ok")
    return redirect(url_for("learning.edp_summary"))


@learning_bp.route("/hoc-edp/tong-ket")
@learning_bp.route("/hoc-edp/summary")
@learning_required
def edp_summary():
    uid = current_user()["uid"]
    summary = get_user_edp_summary(uid)
    progress = summary["progress"]
    if not progress["completed_all"]:
        flash("Hoàn thành đủ 5 bước để xem tổng kết nhé!", "error")
        return redirect(url_for("learning.edp_home"))
    return render_template(
        "edp_summary.html",
        status=_status(),
        student=summary["user"],
        progress=progress,
        evaluation=progress.get("evaluation", {}),
        quizzes=progress.get("quizzes", {}),
        steps=STEPS,
        total=TOTAL_STEPS,
        feedback_questions=FEEDBACK_QUESTIONS,
        rubric_1=RUBRIC_TABLE_1,
        rubric_2=RUBRIC_TABLE_2,
    )