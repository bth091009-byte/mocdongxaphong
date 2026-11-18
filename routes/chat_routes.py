import uuid
from flask import Blueprint, request, jsonify, session
from utils.chatbot import reply

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify(error="Bạn hãy nhập câu hỏi nhé."), 400

    step_id = data.get("step_id", 0)
    user_context = (data.get("user_context") or "").strip()[:300]
    sid = session.setdefault("sid", uuid.uuid4().hex)

    try:
        ans = reply(sid, msg[:500], step_id=step_id, user_context=user_context)
        return jsonify(reply=ans)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify(error=f"Lỗi: {e}"), 503