import re
import google.generativeai as genai
import config
from utils.edp_content import KIT_FACTS, get_step


def clean_text(text):
    """Xóa ký hiệu markdown để khung chat hiển thị chữ thường, gọn gàng."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text, flags=re.S)
    text = re.sub(r"__(.+?)__", r"\1", text, flags=re.S)
    text = re.sub(r"^\s*[\*\-•]\s+", "- ", text, flags=re.M)
    text = re.sub(r"(?<!\w)\*(\S.*?\S|\S)\*(?!\w)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.M)
    text = text.replace("`", "")
    return text.strip()


SHOP_SYSTEM_INSTRUCTION = """Bạn là trợ lý ảo của thương hiệu Mộc Đông Handmade Soap.
Tên bạn là Mộc Đông Bot, nói chuyện thân thiện, dịu dàng, gần gũi như người bạn, luôn dùng tiếng Việt dễ hiểu.

Kiến thức chính bạn nắm vững:
- Sản phẩm: Xà phòng Yến mạch & Nho (100g)
- Thành phần: Dầu dừa, dầu ô liu, tinh dầu nho, bột yến mạch, nước cất, NaOH (đã xà phòng hóa hoàn toàn)
- Công dụng: Làm sạch nhẹ nhàng + nuôi dưỡng da
- Hướng dẫn sử dụng: Làm ướt cơ thể -> thoa đều tạo bọt -> massage nhẹ -> rửa sạch
- Bảo quản: Nơi khô ráo, thoáng mát, tránh nắng trực tiếp, không ngâm lâu trong nước
- Hạn sử dụng: 12 tháng kể từ ngày sản xuất

Cách trả lời:
- Ngắn gọn, rõ ràng, dễ thương, không dùng markdown rối.
- Nếu khách hỏi ngoài phạm vi sản phẩm (bệnh lý da nặng, dị ứng nghiêm trọng...) thì khuyên gặp bác sĩ da liễu.
"""

BASE_EDP_INSTRUCTION = f"""Bạn là Mộc Đông Bot – trợ lý thực hành STEM/EDP đồng hành cùng học sinh làm xà phòng nho từ dầu ăn thải bằng bộ Kit Mộc Đông.
Giọng điệu: thân thiện, bình tĩnh, dễ hiểu, xưng "mình" và gọi học sinh là "bạn".
Quy tắc trình bày: trả lời ngắn gọn (3–6 câu), rõ ý, KHÔNG dùng ký tự markdown (** hoặc #).

Thông số chuẩn của bộ Kit Mộc Đông:
{KIT_FACTS}
"""

_sessions = {}  # key: f"{sid}:{step_id}" -> ChatSession


def _build_instruction(step_id, user_context=""):
    step = get_step(step_id) if step_id else None
    if not step:
        return SHOP_SYSTEM_INSTRUCTION
    parts = [
        BASE_EDP_INSTRUCTION,
        f"Ngữ cảnh hiện tại: Bước {step['n']} ({step['en']}) – {step['title']}.",
        step.get("ai_system_prompt", ""),
    ]
    if user_context:
        parts.append(f"Thông tin bổ sung từ thao tác hiện tại của học sinh: {user_context}")
    return "\n\n".join(p for p in parts if p)


def _model(system_instruction):
    genai.configure(api_key=config.GEMINI_API_KEY)
    return genai.GenerativeModel(
        config.GEMINI_MODEL,
        system_instruction=system_instruction,
        generation_config={"max_output_tokens": 350, "temperature": 0.6},
    )


def reply(sid, message, step_id=0, user_context=""):
    if not config.GEMINI_API_KEY:
        raise RuntimeError("Thiếu GEMINI_API_KEY")
    try:
        step_id = int(step_id or 0)
    except (TypeError, ValueError):
        step_id = 0

    session_key = f"{sid}:{step_id}"
    chat = _sessions.get(session_key)
    if chat is None:
        instruction = _build_instruction(step_id, user_context)
        chat = _sessions[session_key] = _model(instruction).start_chat(history=[])
    elif user_context:
        message = f"[Bối cảnh hiện tại: {user_context}]\nCâu hỏi của học sinh: {message}"

    return clean_text(chat.send_message(message).text)