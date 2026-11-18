"""Nội dung 5 bước học EDP – làm xà phòng nho từ dầu ăn thải bằng bộ Kit Mộc Đông.

Công thức viết bằng LaTeX trong cặp $...$ (inline) hoặc $$...$$ (dòng riêng); trình duyệt hiển thị bằng KaTeX.
Nội dung do chúng ta soạn (không phải input người dùng) nên template được phép in HTML (|safe).
Riêng quiz / checklist-không-LaTeX / form đánh giá được template tự escape.

Mỗi bước có thêm:
  image, image_caption, checklist (tuỳ chọn), quiz, quick_prompts, ai_system_prompt
Mỗi mục trong instructions là dict:
  {"title": ..., "detail": ..., "image": ..., "caption": ...}
Toàn cục: CALC, FEEDBACK_QUESTIONS, RUBRIC_TABLE_1, RUBRIC_TABLE_2, GRADE_BANDS, grade()
"""

# Thông số bộ Kit (1 bánh ~100 g)
KIT_FACTS = (
    "Bộ Kit gồm 6 món: dầu ăn đã lọc sạch 55 g; dầu dừa 25 g; xút NaOH 99% 11,4 g; "
    "nước cất 26 g; nước ép nho tươi 5-8 g; tinh dầu nho/thảo dược 2 g (khoảng 40 giọt). "
    "Tổng 80 g dầu cần 11,4 g NaOH (đã trừ 5% superfat). Pha xút: rót khoảng 21 g nước cất vào Cốc B "
    "rồi đổ từ từ xút vào nước; chờ nguội còn 40-45 độ C. Nước ép nho và tinh dầu cho vào sau khi đạt Trace. "
    "Ủ 24-48 giờ rồi tháo khuôn, ủ chín 3-4 tuần. Đạt chuẩn khi pH 8,5-9,5."
)

# Hệ số cho máy tính công thức (Bước 3)
CALC = {
    "sap_oil": 0.135,      # SAP NaOH của dầu ăn thực vật
    "sap_coco": 0.183,     # SAP NaOH của dầu dừa
    "water_ratio": 1.84,   # kit: 21 g nước cho 11,4 g NaOH
    "default_oil": 55,
    "default_coco": 25,
    "default_sf": 5,
}

STEPS = [
    # ------------------------------------------------------------------ BƯỚC 1
    {
        "n": 1, "en": "ASK", "icon": "❓",
        "title": "Hỏi & khui bộ Kit",
        "short": "Hiểu bài toán tái chế dầu ăn thải và kiểm tra đủ 6 món trong bộ Kit.",
        "image": "/static/images/step1_2.jpg",
        "image_caption": "Toàn cảnh bộ Kit làm xà phòng nho Mộc Đông từ dầu ăn tái chế",
        "objectives": [
            "Giải thích được vì sao dầu ăn thải gây tắc cống và ô nhiễm nguồn nước.",
            "Kiểm tra đủ 6 món trong bộ Kit trước khi bắt tay vào làm.",
        ],
        "knowledge": [
            {"title": "Vì sao dầu ăn thải là vấn đề?",
             "body": r"Dầu ăn thải nổi trên mặt nước ($D \approx 0{,}92\ \text{g/cm}^3 < D_{\text{nước}}$), tạo váng cản oxy hòa tan, gây <b>tắc cống</b> và <b>ô nhiễm nguồn nước</b>."},
            {"title": "Giải pháp: tái chế thành xà phòng",
             "body": r"Biến chất thải thành sản phẩm sạch, an toàn với độ $\text{pH}$ từ $8{,}5$ đến $9{,}5$."},
        ],
        "instructions": [
            {
                "title": "Khui hộp và đối chiếu đủ 6 thành phần trong bộ Kit",
                "detail": "Đặt toàn bộ các gói/chai trong hộp Kit lên mặt bàn sạch và kiểm đếm theo danh sách 6 món bên dưới (định lượng chuẩn cho 1 bánh thành phẩm ~100 g): <b>55 g dầu ăn đã lọc sạch</b>, <b>25 g dầu dừa</b>, <b>11,4 g xút NaOH 99%</b>, <b>26 g nước cất</b>, <b>5–8 g nước ép nho tươi</b> và <b>2 g tinh dầu</b> (~40 giọt).",
                "image": "/static/images/edp/b1_1_khui_kit.jpg",
                "caption": "Bày đủ 6 thành phần nguyên liệu của bộ Kit ra bàn để kiểm đếm",
            },
            {
                "title": "Kiểm tra niêm phong gói xút NaOH & điều kiện bảo quản",
                "detail": "Quan sát túi/lọ <b>xút NaOH 99% (11,4 g)</b>: hạt xút phải khô ráo, tơi rời, không bị chảy nước hay đóng tảng cứng. Tuyệt đối <b>chưa mở nắp/miệng túi</b> ở bước này vì NaOH hút ẩm rất mạnh từ không khí.",
                "image": "/static/images/edp/b1_2_kiem_tra_naoh.jpg",
                "caption": "Kiểm tra độ kín của gói/lọ xút NaOH 99% trước khi thực hành",
            },
        ],
        "ordered": False,
        "checklist_title": "Kiểm tra Bộ Kit",
        "checklist": [
            "Gói/chai 1: Dầu ăn đã lọc sạch (55 g)",
            "Gói/chai 2: Dầu dừa (25 g)",
            "Gói 3: Xút NaOH 99% (11,4 g)",
            "Chai 4: Nước cất (26 g)",
            "Chai 5: Nước ép nho tươi (5 g – 8 g)",
            "Lọ 6: Tinh dầu nho / thảo dược (2 g ~ 40 giọt)",
        ],
        "safety": [
            "Giữ kín nắp gói NaOH để tránh hút ẩm.",
            "Chuẩn bị sẵn găng tay, kính bảo hộ, 2 cốc nhựa PP (hoặc thủy tinh) và khuôn silicon <b>trước khi</b> mở gói xút.",
            "Để bộ Kit xa tầm tay trẻ nhỏ; chỉ thực hành khi có người lớn hướng dẫn.",
        ],
        "steam": [
            {"k": "S", "label": "Khoa học", "text": "Tỷ trọng và tính kỵ nước của dầu; vì sao dầu nổi trên nước."},
            {"k": "M", "label": "Toán học", "text": "Đọc, đối chiếu và ước lượng khối lượng nguyên liệu trong Kit."},
        ],
        "quick_prompts": [
            "Vì sao không được đổ dầu ăn thải xuống cống?",
            "Mình thiếu một món trong Kit thì làm sao?",
            "Vì sao phải giữ kín gói NaOH?",
        ],
        "ai_system_prompt": (
            "Học sinh đang ở BƯỚC 1 (ASK): hiểu vấn đề dầu ăn thải và kiểm tra bộ Kit. "
            "Giúp em hiểu vì sao dầu thải gây tắc cống, cản oxy trong nước (dầu nhẹ hơn nước, D khoảng 0,92 g/cm3). "
            "Nếu em báo thiếu hoặc hỏng món nào trong Kit, khuyên liên hệ Mộc Đông, không tự thay bằng nguyên liệu khác, "
            "đặc biệt không tự mua hay thay xút. Nhắc giữ kín NaOH vì hút ẩm."
        ),
        "quiz": [
            {"q": "Dầu ăn thải gây hại gì cho nguồn nước?",
             "options": ["Tan hoàn toàn trong nước nên làm nước nhiều dinh dưỡng hơn",
                         "Nổi thành váng, cản oxy hòa tan và gây tắc cống",
                         "Chìm xuống đáy vì nặng hơn nước",
                         "Bay hơi hết nên không gây hại"],
             "correct": 1,
             "explain": "Dầu nhẹ hơn nước (khoảng 0,92 g/cm³) và không tan, nên nổi thành váng, cản oxy và dễ đóng cặn gây tắc đường ống."},
            {"q": "Trong bộ Kit, khối lượng dầu dừa là bao nhiêu?",
             "options": ["11,4 g", "25 g", "55 g", "80 g"],
             "correct": 1,
             "explain": "Dầu dừa 25 g; dầu ăn thải đã lọc 55 g; cộng lại là 80 g dầu. 11,4 g là khối lượng NaOH."},
            {"q": "Vì sao phải giữ kín nắp gói NaOH?",
             "options": ["Để xút không bay mùi", "Vì NaOH hút ẩm nên dễ vón cục và sai khối lượng",
                         "Để xút không bị lạnh", "Vì NaOH phát sáng khi gặp ánh nắng"],
             "correct": 1,
             "explain": "NaOH hút ẩm mạnh từ không khí, làm vón cục, chảy nước và gây sai lệch khi cân – ảnh hưởng độ an toàn của mẻ xà phòng."},
            {"q": "Món nào KHÔNG nằm trong bộ Kit?",
             "options": ["Nước cất", "Tinh dầu nho / thảo dược", "Dầu ô liu", "Xút NaOH 99%"],
             "correct": 2,
             "explain": "Bộ Kit có 6 món: dầu ăn đã lọc, dầu dừa, NaOH, nước cất, nước ép nho và tinh dầu. Không có dầu ô liu."},
        ],
    },
    # ------------------------------------------------------------------ BƯỚC 2
    {
        "n": 2, "en": "IMAGINE", "icon": "💡",
        "title": "Tưởng tượng & nguyên lý phản ứng",
        "short": "Nắm đúng 1 phản ứng tạo ra xà phòng và biết vì sao trộn 2 loại dầu.",
        "image": "/static/images/step2_2.jpg",
        "image_caption": "Sơ đồ nguyên lý phản ứng xà phòng hóa và vai trò từng nguyên liệu",
        "objectives": [
            "Viết và giải thích được phương trình phản ứng xà phòng hóa.",
            "Nêu được vai trò của từng nguyên liệu trong Kit, đặc biệt vì sao phải trộn dầu ăn thải với dầu dừa.",
        ],
        "knowledge": [
            {"title": "Phương trình xà phòng hóa",
             "body": r"""$$(\text{RCOO})_3\text{C}_3\text{H}_5 + 3\text{NaOH} \xrightarrow{t^\circ} 3\text{RCOONa} + \text{C}_3\text{H}_5(\text{OH})_3$$
<p class="note">Chất béo trong dầu + Xút → Xà phòng + Glycerol dưỡng ẩm</p>"""},
            {"title": "Vai trò từng món trong Kit",
             "body": r"""<ul>
<li><b>55 g dầu ăn thải (khoảng 70%):</b> tạo nền xà phòng dịu nhẹ, giữ ẩm.</li>
<li><b>25 g dầu dừa (khoảng 30%):</b> giúp bánh cứng chắc và tạo nhiều bọt to.</li>
<li><b>5 g – 8 g nước ép nho:</b> tạo màu tự nhiên và chống oxy hóa. <i>Lưu ý:</i> sắc tố nho gặp kiềm sẽ đổi sang màu xanh rêu hoặc nâu trầm tự nhiên, <b>không phải bị hỏng</b>.</li>
</ul>"""},
            {"title": "Cơ chế làm sạch (phân tử lưỡng cực)",
             "body": r"Phân tử xà phòng $\text{RCOONa}$ có <b>đuôi kỵ nước</b> ($-\text{R}$) bám vào vết dầu mỡ và <b>đầu ưa nước</b> ($-\text{COO}^-$) liên kết với nước, tạo các hạt <b>micelle</b> cuốn trôi vết bẩn."},
        ],
        "instructions": [
            {
                "title": "Sắp xếp nguyên liệu theo 3 cụm quy trình từ trái sang phải",
                "detail": "Xếp các lọ trên bàn theo đúng trình tự sử dụng: <b>Cụm 1 (Pha dầu):</b> dầu ăn thải → dầu dừa; <b>Cụm 2 (Pha kiềm):</b> nước cất → xút NaOH; <b>Cụm 3 (Hoàn thiện sau Trace):</b> nước ép nho → tinh dầu. Cách bố trí tuyến tính này giúp thao tác không bao giờ bị nhầm thứ tự.",
                "image": "/static/images/edp/b2_1_sap_xep_nguyen_lieu.jpg",
                "caption": "Xếp nguyên liệu từ trái sang phải theo đúng thứ tự pha chế",
            },
            {
                "title": "Dự đoán sự biến đổi màu sắc & tính chất bánh xà phòng",
                "detail": "Quan sát màu tím đỏ của nước ép nho tươi và hình dung sự thay đổi màu khi gặp dung dịch kiềm (sắc tố anthocyanin chuyển sang <b>xanh rêu hoặc nâu trầm tự nhiên</b>). Đồng thời đối chiếu vai trò tỷ lệ <b>70% dầu ăn thải + 30% dầu dừa</b> giúp bánh vừa cứng chắc nhiều bọt vừa dịu nhẹ trên da.",
                "image": "/static/images/edp/b2_2_sac_to_nho.jpg",
                "caption": "Sắc tố nho tự nhiên chuyển xanh rêu/nâu trầm khi gặp môi trường kiềm",
            },
        ],
        "ordered": False,
        "safety": [
            r"Phân biệt rõ xút ăn da ($\text{NaOH}$) với bột baking soda ($\text{NaHCO}_3$): <b>tuyệt đối không nhầm lẫn</b> hai loại này.",
            "Dán nhãn hoặc xếp riêng gói xút, tránh để lẫn với các gói bột khác trong bếp.",
        ],
        "steam": [
            {"k": "S", "label": "Khoa học", "text": "Phản ứng thủy phân este trong môi trường kiềm; cấu trúc micelle."},
            {"k": "A", "label": "Nghệ thuật", "text": "Màu tự nhiên của sắc tố nho thay đổi theo độ kiềm."},
        ],
        "quick_prompts": [
            "Giải thích phản ứng xà phòng hóa cho mình dễ hiểu hơn",
            "Vì sao phải trộn dầu ăn thải với dầu dừa?",
            "Màu nho chuyển xanh rêu có phải bị hỏng không?",
        ],
        "ai_system_prompt": (
            "Học sinh đang ở BƯỚC 2 (IMAGINE): nguyên lý phản ứng xà phòng hóa. "
            "Phương trình: chất béo + 3NaOH tạo muối natri của axit béo (xà phòng) + glycerol. "
            "Vai trò: dầu ăn thải (khoảng 70%) cho nền dịu, giữ ẩm; dầu dừa (khoảng 30%) cho độ cứng và bọt to; "
            "nước ép nho tạo màu và chống oxy hóa, sắc tố gặp kiềm đổi xanh rêu hoặc nâu trầm là bình thường. "
            "Giải thích bằng ví dụ gần gũi, ngắn gọn. Gợi mở để em tự suy luận thay vì đưa sẵn đáp án bài kiểm tra."
        ),
        "quiz": [
            {"q": "Phản ứng nào tạo ra xà phòng trong bộ Kit?",
             "options": ["Trung hòa axit mạnh bằng bazơ yếu", "Xà phòng hóa chất béo bằng NaOH",
                         "Nhiệt phân dầu ở nhiệt độ cao", "Hòa tan dầu vào nước cất"],
             "correct": 1,
             "explain": "Chất béo phản ứng với NaOH tạo muối natri của axit béo (xà phòng) và glycerol."},
            {"q": "Dầu dừa có vai trò chính nào trong công thức?",
             "options": ["Tạo màu xanh rêu", "Giúp bánh cứng chắc và tạo nhiều bọt to",
                         "Làm xút nguội nhanh hơn", "Khử hoàn toàn mùi dầu thải"],
             "correct": 1,
             "explain": "Dầu dừa giàu axit lauric, giúp bánh cứng và nhiều bọt. Dầu ăn thải đóng vai trò dịu nhẹ, giữ ẩm."},
            {"q": "Sau khi trộn, xà phòng chuyển sang màu xanh rêu hoặc nâu trầm. Điều này nghĩa là gì?",
             "options": ["Mẻ bị hỏng, phải bỏ", "Bình thường: sắc tố nho đổi màu trong môi trường kiềm",
                         "Đã cho thừa nước", "Xà phòng bị nhiễm khuẩn"],
             "correct": 1,
             "explain": "Sắc tố nho nhạy với độ pH nên đổi màu khi gặp kiềm. Đây là màu tự nhiên, không phải lỗi."},
            {"q": "Glycerol sinh ra cùng xà phòng có lợi gì?",
             "options": ["Dưỡng ẩm cho da", "Làm bánh xà phòng cháy sáng", "Làm tăng độ kiềm", "Không có tác dụng gì"],
             "correct": 0,
             "explain": "Glycerol là chất giữ ẩm tự nhiên, giúp xà phòng làm sạch mà không làm da quá khô."},
        ],
    },
    # ------------------------------------------------------------------ BƯỚC 3
    {
        "n": 3, "en": "PLAN", "icon": "📐",
        "title": "Lập kế hoạch & chuẩn bị góc thực hành",
        "short": "Chuẩn bị chi tiết bảo hộ, dụng cụ chịu kiềm và định lượng trước khi pha hóa chất.",
        "image": "/static/images/step3_2.jpg",
        "image_caption": "Bố trí góc thực hành an toàn với Cốc A, Cốc B, khuôn silicon và đồ bảo hộ",
        "objectives": [
            "Hiểu vì sao 80 g dầu cần đúng 11,4 g NaOH (superfat 5%).",
            "Chuẩn bị đầy đủ bảo hộ, dụng cụ chịu kiềm (Cốc A, Cốc B, khuôn) và chia sẵn nước cất trước khi mở gói xút.",
        ],
        "knowledge": [
            {"title": "Kiến thức định lượng (đã tính sẵn trong Kit)",
             "body": r"""Tổng $80\ \text{g}$ dầu ($55\ \text{g}$ dầu thải + $25\ \text{g}$ dầu dừa) cần đúng $11{,}4\ \text{g}$ $\text{NaOH}$ – đã trừ hao $5\%$ dư dầu để xà phòng mềm da, tuyệt đối không còn xút dư.
$$m_{\text{NaOH}} = (55 \times 0{,}135 + 25 \times 0{,}183) \times (1 - 0{,}05) = 12{,}0 \times 0{,}95 = 11{,}4\ \text{g}$$"""},
            {"title": "Superfat (dư dầu an toàn)",
             "body": r"Cố ý giảm lượng $\text{NaOH}$ khoảng $5\%$ so với lý thuyết để $\text{NaOH}$ phản ứng hết, không còn kiềm dư gây hại da; lượng dầu dư giúp dưỡng ẩm."},
            {"title": "Mẹo giữ dưỡng chất nho",
             "body": r"Chia chai nước cất $26\ \text{g}$: chỉ rót khoảng $21\ \text{g}$ vào Cốc B để pha xút. Phần nước ép nho ($5 - 8\ \text{g}$) để dành cho vào sau cùng, để nhiệt nóng không làm mất dưỡng chất."},
        ],
        "instructions": [
            {
                "title": "1. Trang bị đầy đủ đồ bảo hộ cá nhân & thông gió khu vực làm",
                "detail": "Đeo <b>găng tay cao su</b> (che kín cổ tay), <b>kính bảo hộ</b> chống bắn hóa chất, <b>khẩu trang</b> và mặc áo dài tay/tạp dề. Buộc gọn tóc, mở cửa sổ hoặc bật quạt thông gió nhẹ (không thổi thẳng vào bàn cân bột). Đặt sẵn 1 chai nước sạch gần tầm với để rửa tay khi cần.",
                "image": "/static/images/edp/b3_1_bao_ho.jpg",
                "caption": "Đeo đầy đủ găng tay cao su, kính bảo hộ và khẩu trang trước khi mở hóa chất",
            },
            {
                "title": "2. Chuẩn bị bộ dụng cụ chịu kiềm (Cốc A, Cốc B, que khuấy, khuôn)",
                "detail": "Lót giấy báo hoặc tấm trải nhựa lên mặt bàn phẳng, sạch và khô. Chuẩn bị đủ 4 dụng cụ đạt chuẩn chịu kiềm:<br>• <b>Cốc A (trộn dầu):</b> cốc nhựa PP (ký hiệu số 5 dưới đáy) hoặc thủy tinh chịu nhiệt dung tích <code>300–500 ml</code>.<br>• <b>Cốc B (pha dung dịch xút):</b> cốc nhựa PP dày hoặc thủy tinh chịu nhiệt dung tích <code>200–300 ml</code>.<br>• <b>Dụng cụ khuấy:</b> phới lồng inox, đũa thủy tinh hoặc thìa silicon (tuyệt đối không dùng thìa nhôm).<br>• <b>Khuôn silicon (~100–120 ml):</b> đặt sẵn trên một chiếc khay phẳng cứng để sau khi rót có thể bưng đi ủ mà không bị nghiêng đổ.",
                "image": "/static/images/edp/b3_2_dung_cu.jpg",
                "caption": "Bộ dụng cụ chuẩn: Cốc A, Cốc B nhựa PP/thủy tinh, phới inox/silicon và khuôn silicon đặt trên khay",
            },
            {
                "title": "3. Chia định lượng 21 g nước cất & kiểm tra độ lỏng của dầu dừa",
                "detail": "Mở chai nước cất <code>26 g</code>: rót khoảng <b>21 g (khoảng 4/5 chai)</b> vào sẵn lòng <b>Cốc B</b> để lát nữa hòa tan xút; giữ lại ~5 g nước cất còn lại trong chai. Kiểm tra gói/chai <b>dầu dừa (25 g)</b>: nếu dầu dừa bị đông trắng đặc do thời tiết mát, ngâm kín gói/chai dầu dừa vào bát nước ấm <code>45–50 °C</code> trong <code>2–3 phút</code> cho tan lỏng hoàn toàn. Để riêng nước ép nho (<code>5–8 g</code>) và tinh dầu (<code>2 g</code>) sang góc phải bàn.",
                "image": "/static/images/edp/b3_3_chia_nuoc_cat.jpg",
                "caption": "Rót sẵn ~21 g nước cất vào Cốc B và kiểm tra dầu dừa đã tan lỏng",
            },
            {
                "title": "4. Đối chiếu số liệu bằng Máy tính công thức bên dưới",
                "detail": "Dùng máy tính công thức ngay bên dưới (mặc định <code>55 g</code> dầu thải + <code>25 g</code> dầu dừa, superfat <code>5%</code>) để kiểm tra lại khối lượng <b>11,4 g NaOH</b> và <b>21,0 g nước pha xút</b> trước khi chuyển sang Bước 4 thực hành.",
                "image": "/static/images/edp/b3_4_kiem_tra_cong_thuc.jpg",
                "caption": "Đối chiếu khối lượng NaOH và nước pha xút bằng công cụ tính công thức",
            },
        ],
        "ordered": True,
        "checklist_title": "Checklist chuẩn bị 3 phút trước khi bắt đầu",
        "checklist": [
            "Đã đeo găng tay cao su, kính bảo hộ, khẩu trang và mở thoáng phòng.",
            "Đã có đủ Cốc A (trộn dầu), Cốc B (pha xút), phới inox/silicon và khuôn silicon đặt trên khay phẳng.",
            "Đã rót sẵn khoảng 21 g nước cất vào Cốc B; dầu dừa đã tan lỏng; nước ép nho & tinh dầu để riêng cho bước cuối.",
        ],
        "calculator": True,
        "safety_level": "",
        "safety": [
            r"""<b>Cấm kỵ:</b> tuyệt đối không dùng cốc / thìa bằng nhôm ($\text{Al}$) vì xút ăn mòn nhôm và sinh khí hydro dễ cháy nổ:
$$2\text{Al} + 2\text{NaOH} + 2\text{H}_2\text{O} \longrightarrow 2\text{NaAlO}_2 + 3\text{H}_2\uparrow$$""",
            "Chỉ dùng cốc nhựa PP (số 5) hoặc thủy tinh chịu nhiệt; chuẩn bị xong toàn bộ dụng cụ rồi mới mở gói xút.",
        ],
        "steam": [
            {"k": "M", "label": "Toán học", "text": "Tính tỷ lệ phần trăm khối lượng; bài toán trừ hao 5% superfat."},
            {"k": "E", "label": "Kỹ thuật", "text": "Bố trí góc thực hành: thứ tự thao tác, vị trí Cốc A / Cốc B để không lúng túng."},
        ],
        "quick_prompts": [
            "Vì sao 80 g dầu cần 11,4 g NaOH?",
            "Superfat 5% nghĩa là gì?",
            "Mình có thể dùng thìa inox được không?",
        ],
        "ai_system_prompt": (
            "Học sinh đang ở BƯỚC 3 (PLAN): chuẩn bị góc thực hành và hiểu số liệu định lượng. "
            "Số liệu kit: 55 g dầu thải x 0,135 + 25 g dầu dừa x 0,183 = 12,0 g NaOH lý thuyết; trừ 5% superfat được 11,4 g. "
            "Chia nước cất 26 g: khoảng 21 g vào Cốc B pha xút; nước ép nho để cho sau cùng. "
            "Cấm dụng cụ nhôm hoặc kẽm. Dụng cụ an toàn: nhựa PP, thủy tinh, inox. "
            "Không khuyến khích em tự đổi công thức hay tăng lượng NaOH; nếu em muốn thử công thức khác, giải thích rủi ro và khuyên hỏi người lớn."
        ),
        "quiz": [
            {"q": "Với 55 g dầu thải và 25 g dầu dừa, lượng NaOH sau khi trừ 5% superfat là bao nhiêu?",
             "options": ["9,6 g", "10,8 g", "11,4 g", "12,6 g"],
             "correct": 2,
             "explain": "55×0,135 + 25×0,183 = 12,0 g; nhân (1 − 0,05) được 11,4 g."},
            {"q": "Vì sao phải cố ý dùng ít NaOH hơn lý thuyết một chút (superfat)?",
             "options": ["Để tiết kiệm xút", "Để không còn xút dư gây hại da và còn dầu dưỡng ẩm",
                         "Để bánh xà phòng nặng hơn", "Để xà phòng có màu đậm hơn"],
             "correct": 1,
             "explain": "Superfat đảm bảo NaOH phản ứng hết; lượng dầu dư còn lại giúp bánh xà phòng dịu với da."},
            {"q": "Dụng cụ nào tuyệt đối KHÔNG được dùng khi pha xút?",
             "options": ["Cốc nhựa PP", "Cốc thủy tinh", "Thìa nhôm", "Khuôn silicon"],
             "correct": 2,
             "explain": "Xút ăn mòn nhôm và sinh khí hydro dễ cháy nổ."},
            {"q": "Nước ép nho nên được cho vào lúc nào?",
             "options": ["Pha chung với xút ở Cốc B", "Trộn sẵn với dầu ở Cốc A",
                         "Sau cùng, khi hỗn hợp đã đạt Trace", "Sau khi tháo khuôn"],
             "correct": 2,
             "explain": "Để dành đến cuối để nhiệt từ xút không làm mất dưỡng chất và màu của nho."},
        ],
    },
    # ------------------------------------------------------------------ BƯỚC 4
    {
        "n": 4, "en": "CREATE", "icon": "🧪",
        "title": "Thực hành làm xà phòng",
        "short": "Thực hiện chi tiết 5 thao tác chuẩn để đổ khuôn thành công bánh xà phòng nho ~100 g.",
        "image": "/static/images/step4.jpg",
        "image_caption": "Quy trình 5 thao tác tạo nhũ tương Trace, phối màu nho và đổ khuôn xà phòng",
        "objectives": [
            "Thực hiện đúng 5 thao tác: trộn dầu → pha xút → khuấy đạt Trace → thêm nho & tinh dầu → đổ khuôn.",
            "Nhận biết trạng thái Trace và biết cách ủ chín bánh xà phòng.",
        ],
        "knowledge": [
            {"title": r"Phản ứng cần quan sát: hòa tan $\text{NaOH}$",
             "body": r"""$$\text{NaOH}_{(r)} \xrightarrow{\text{H}_2\text{O}} \text{Na}^+_{(dd)} + \text{OH}^-_{(dd)} \quad (\Delta H < 0)$$
<p><b>Hiện tượng:</b> cốc nóng lên rất nhanh (tới khoảng $75^\circ\text{C}$), cần chờ nguội về khoảng $40 - 45^\circ\text{C}$ (sờ ngoài cốc thấy ấm nhẹ như nước tắm).</p>"""},
            {"title": "Trạng thái “Trace”",
             "body": r"""<p>Ban đầu dầu và dung dịch xút tách lớp. Khi khuấy liên tục, muối $\text{RCOONa}$ hình thành đóng vai trò chất nhũ hóa, kéo hai pha hòa quyện. Hỗn hợp chuyển từ lỏng sang <b>sệt đặc như sữa đặc</b>; nhấc que khuấy lên thấy để lại <b>vệt rõ</b> trên mặt gọi là Trace.</p>"""},
        ],
        "instructions": [
            {
                "title": "Thao tác 1 – Phối trộn hỗn hợp dầu nền (Cốc A)",
                "detail": "Rót toàn bộ <b>55 g dầu ăn đã lọc sạch</b> và <b>25 g dầu dừa</b> (đã tan lỏng hoàn toàn) vào <b>Cốc A</b>. Dùng phới/đũa khuấy nhẹ đều tay trong <code>30 giây</code> để hai loại dầu hòa quyện thành hỗn hợp vàng trong đồng nhất.",
                "image": "/static/images/edp/b4_1_tron_dau.jpg",
                "caption": "Trộn đều 55 g dầu ăn đã lọc sạch và 25 g dầu dừa trong Cốc A",
            },
            {
                "title": "Thao tác 2 – Pha dung dịch xút & chờ hạ nhiệt (Cốc B)",
                "detail": r"Kiểm tra trong <b>Cốc B</b> đã có sẵn <code>21 g</code> nước cất. Cắt miệng gói <b>11,4 g NaOH</b>, <b>đổ từ từ từng ít một xút VÀO nước</b> (tuyệt đối không đổ nước vào xút), vừa đổ vừa khuấy nhẹ theo một chiều cho hạt xút tan hết. Cốc B sẽ tỏa nhiệt nóng lên tới <code>70–75 °C</code> (đứng hơi nghiêng người, tránh hít hơi bốc lên). Đặt Cốc B yên trong <code>10–15 phút</code> (hoặc ngâm đáy cốc vào bát nước mát) cho tới khi dung dịch nguội về khoảng <b>40–45 °C</b> (sờ ngoài thành cốc thấy ấm nhẹ như nước tắm).",
                "image": "/static/images/edp/b4_2_pha_xut.jpg",
                "caption": "Đổ từ từ xút NaOH vào Cốc B chứa sẵn nước cất và chờ nguội về 40–45 °C",
            },
            {
                "title": "Thao tác 3 – Nhũ hóa & khuấy đạt trạng thái “Trace”",
                "detail": "Khi cả Cốc A và Cốc B đều ở mức ấm nhẹ <code>40–45 °C</code>, cầm Cốc B <b>rót thành dòng nhỏ từ từ</b> vào Cốc A, đồng thời khuấy liên tục. Khuấy đều tay theo <b>một chiều cố định</b> trong <code>10–15 phút</code> (nếu dùng máy đánh trứng mini, bật mức thấp và nghỉ 30 giây sau mỗi 1 phút). Hỗn hợp sẽ chuyển từ lỏng trong sang đục mờ rồi sánh đặc như <b>sữa đặc có đường</b>. Thử Trace: nhấc que khuấy lên và nhỏ vài giọt lên bề mặt — nếu <b>vệt kem nổi rõ 2–3 giây</b> rồi mới chìm xuống là đã đạt!",
                "image": "/static/images/edp/b4_3_khuay_trace.jpg",
                "caption": "Khuấy liên tục một chiều 10–15 phút cho tới khi hỗn hợp sệt đặc và để lại vệt Trace rõ",
            },
            {
                "title": "Thao tác 4 – Thêm nước ép nho & tinh dầu tạo hương",
                "detail": "Ngay khi hỗn hợp vừa đạt Trace, đổ <b>5–8 g nước ép nho tươi</b> và nhỏ hết <b>2 g tinh dầu</b> (~40 giọt) vào Cốc A. Khuấy đều tay thêm <code>1–2 phút</code> cho quyện đều màu và mùi thơm. Lưu ý: màu tím đỏ của nho sẽ chuyển sang <b>xanh rêu hoặc nâu trầm tự nhiên</b> khi gặp môi trường kiềm — đây là phản ứng chuẩn xác. Không khuấy quá lâu kẻo hỗn hợp đặc cứng khó rót.",
                "image": "/static/images/edp/b4_4_them_nho_tinh_dau.jpg",
                "caption": "Thêm 5–8 g nước ép nho và 2 g tinh dầu sau khi đạt Trace, khuấy đều 1–2 phút",
            },
            {
                "title": "Thao tác 5 – Đổ khuôn, gõ vỡ bọt khí & ủ chín 3–4 tuần",
                "detail": "Rót nhanh tay toàn bộ hỗn hợp vào <b>khuôn silicon</b> đã đặt sẵn trên khay phẳng. Cầm khay gõ nhẹ xuống mặt bàn <code>3–5 lần</code> cho vỡ hết bọt khí bên trong, giúp mặt bánh mịn láng không rỗ. Dùng màng bọc thực phẩm hoặc bìa cứng đậy kín mặt khuôn, đặt nơi khô ráo thoáng mát. Sau <b>24–48 giờ</b> bánh đông cứng chắc → nhẹ nhàng tách khỏi khuôn silicon. Xếp bánh lên giá thoáng khí, <b>ủ chín 3–4 tuần</b> (lật mặt bánh mỗi tuần 1 lần) để bay bớt nước (còn ~100 g) và hạ pH về mức an toàn <code>8,5–9,5</code>.",
                "image": "/static/images/edp/b4_5_do_khuon_u.jpg",
                "caption": "Rót vào khuôn silicon, gõ vỡ bọt khí và đậy kín ủ 24–48 giờ trước khi tháo khuôn",
            },
        ],
        "ordered": True,
        "safety_level": "high",
        "safety": [
            "<b>Bắt buộc:</b> đeo kính bảo hộ chống hóa chất, găng tay cao su, khẩu trang và làm ở nơi thông thoáng.",
            r"<b>Quy tắc vàng:</b> <b>đổ $\text{NaOH}$ VÀO nước – tuyệt đối không đổ nước vào $\text{NaOH}$</b> (sôi bắn vào mặt / tay).",
            "<b>Sơ cứu khẩn cấp:</b> nếu dính xút vào da hoặc mắt, lập tức xả dưới vòi nước sạch chảy liên tục <b>ít nhất 15 – 20 phút</b>, gọi người lớn và đến cơ sở y tế nếu mắt bị dính hoặc da rát nhiều. Không bôi giấm hay chanh lên vết bỏng kiềm.",
            "Cốc B nóng tới khoảng 75 °C: cầm cốc cẩn thận, không để trẻ nhỏ đến gần khu vực thực hành.",
        ],
        "steam": [
            {"k": "S", "label": "Khoa học", "text": "Phản ứng tỏa nhiệt khi hòa tan NaOH; hiện tượng nhũ hóa tạo Trace."},
            {"k": "T", "label": "Công nghệ", "text": "Dùng nhiệt kế / cảm giác tay để kiểm soát nhiệt độ; tối ưu cách khuấy."},
        ],
        "quick_prompts": [
            "Làm sao biết hỗn hợp đã đạt Trace?",
            "Khuấy mãi vẫn chưa đặc thì sao?",
            "Mình lỡ dính xút lên tay, phải làm gì?",
        ],
        "ai_system_prompt": (
            "Học sinh đang ở BƯỚC 4 (CREATE) – bước nguy hiểm nhất. AN TOÀN LÀ ƯU TIÊN SỐ 1. "
            "5 thao tác: (1) trộn dầu ở Cốc A; (2) pha xút: rót nước cất vào Cốc B trước rồi đổ từ từ xút VÀO nước, chờ nguội 40-45 độ C; "
            "(3) rót từ từ xút vào dầu, khuấy một chiều 10-15 phút đến Trace; (4) thêm nước ép nho 5-8 g và tinh dầu 2 g, khuấy 1-2 phút; "
            "(5) đổ khuôn silicon, gõ vỡ bọt khí, đậy kín, tháo khuôn sau 24-48 giờ, ủ 3-4 tuần. "
            "Nếu em nói dính xút vào da hoặc mắt hoặc nuốt phải: việc đầu tiên là bảo em xả nước sạch chảy liên tục ít nhất 15-20 phút, "
            "gọi người lớn ngay và đến cơ sở y tế; không bôi giấm hay chanh; ngắn gọn, bình tĩnh, rõ từng bước. "
            "Nếu khuấy lâu chưa đặc: có thể cần khuấy thêm, kiểm tra lại nhiệt độ; khuyên em dừng lại hỏi người lớn nếu có bất thường (tách lớp, bốc khói nhiều), "
            "không tự thêm xút hay nước."
        ),
        "quiz": [
            {"q": "Khi pha dung dịch xút, thứ tự đúng là gì?",
             "options": ["Đổ nước vào xút", "Đổ xút từ từ vào nước", "Đổ cả hai cùng lúc", "Trộn xút với dầu trước"],
             "correct": 1,
             "explain": "Luôn đổ XÚT VÀO NƯỚC. Đổ nước vào xút làm sôi bắn, rất nguy hiểm."},
            {"q": "Nên trộn dung dịch xút với dầu khi cả hai ở khoảng nhiệt độ nào?",
             "options": ["Khoảng 10 – 15 °C", "Khoảng 40 – 45 °C", "Khoảng 75 – 80 °C", "Trên 100 °C"],
             "correct": 1,
             "explain": "Cốc xút nóng tới ~75 °C khi pha, cần chờ nguội còn khoảng 40 – 45 °C trước khi trộn với dầu."},
            {"q": "“Trace” là trạng thái như thế nào?",
             "options": ["Hỗn hợp vẫn lỏng trong, tách lớp", "Hỗn hợp sệt như sữa đặc, nhấc que khuấy để lại vệt rõ",
                         "Hỗn hợp đã cứng như đá", "Hỗn hợp bốc khói trắng"],
             "correct": 1,
             "explain": "Ở Trace, dầu và xút đã nhũ hóa, hỗn hợp sệt đặc và để lại vệt trên bề mặt."},
            {"q": "Khi nào cho nước ép nho và tinh dầu vào?",
             "options": ["Trước khi pha xút", "Cùng lúc với xút", "Sau khi hỗn hợp đạt Trace", "Sau khi ủ 3 tuần"],
             "correct": 2,
             "explain": "Thêm sau Trace để giữ màu, mùi và dưỡng chất, rồi khuấy thêm 1 – 2 phút."},
            {"q": "Lỡ dính xút lên da, việc ĐẦU TIÊN cần làm là gì?",
             "options": ["Bôi giấm lên chỗ dính", "Lau khô bằng khăn giấy", "Xả nước sạch chảy liên tục ít nhất 15 – 20 phút",
                         "Chờ xem da có đỏ không"],
             "correct": 2,
             "explain": "Xả nước dồi dào và liên tục ngay lập tức; không bôi giấm hay chanh vì có thể gây tổn thương sâu hơn. Báo người lớn và đi y tế nếu cần."},
        ],
    },
    # ------------------------------------------------------------------ BƯỚC 5
    {
        "n": 5, "en": "IMPROVE", "icon": "🔍",
        "title": "Thử nghiệm & hoàn thiện sản phẩm",
        "short": "Kiểm tra độ an toàn trước khi dùng, đánh giá chất lượng và tự đánh giá năng lực.",
        "image": "/static/images/step5.jpg",
        "image_caption": "Kiểm tra độ pH bằng giấy quỳ tím, thử bọt rửa tay và đóng gói bánh xà phòng",
        "objectives": [
            "Kiểm tra độ pH và đánh giá chất lượng bánh xà phòng sau 3 – 4 tuần ủ.",
            "Ghi lại nhật ký mẻ, rút bài học cải tiến và tự đánh giá năng lực thực hiện quy trình EDP.",
        ],
        "knowledge": [
            {"title": "Vì sao pH giảm trong lúc ủ?",
             "body": r"""Trong lúc ủ, $\text{CO}_2$ trong không khí trung hòa nốt vi lượng kiềm ở bề mặt, đưa độ $\text{pH}$ từ khoảng $12$ xuống mức an toàn $8{,}5 - 9{,}5$:
$$2\text{NaOH} + \text{CO}_2 \longrightarrow \text{Na}_2\text{CO}_3 + \text{H}_2\text{O}$$"""},
        ],
        "instructions": [
            {
                "title": "1. Test độ pH bằng giấy quỳ tím (bắt buộc trước khi dùng)",
                "detail": r"Sau đủ <code>3–4 tuần</code> ủ chín, làm ướt mặt bánh xà phòng với vài giọt nước sạch, xoa tạo bọt nhẹ rồi áp mẩu giấy quỳ tím vào lớp bọt trong <code>5 giây</code>. Giấy chuyển <b>xanh lơ nhẹ ($\text{pH}$ $8{,}5 - 9{,}5$)</b> là đạt chuẩn. Nếu chuyển <b>xanh đậm ($\text{pH} > 10$)</b>, phải ủ thêm <code>1 tuần</code> rồi đo lại mới được dùng.",
                "image": "/static/images/edp/b5_1_test_ph.jpg",
                "caption": "Áp giấy quỳ tím vào lớp bọt xà phòng để kiểm tra ngưỡng pH an toàn 8,5–9,5",
            },
            {
                "title": "2. Test rửa tay thực tế & quan sát cảm quan",
                "detail": "Rửa tay trực tiếp với bánh xà phòng để đánh giá độ cứng chắc của khối (không bở nát), khả năng tạo bọt mịn (nhờ <code>25 g</code> dầu dừa), cảm giác ẩm mượt trên da sau khi lau khô (nhờ <code>55 g</code> dầu thải + glycerol + nho) và mùi hương tự nhiên.",
                "image": "/static/images/edp/b5_2_test_rua_tay.jpg",
                "caption": "Thử khả năng tạo bọt, làm sạch và độ dịu nhẹ trên da tay",
            },
            {
                "title": "3. Đóng gói hoàn thiện, chụp ảnh & nộp phiếu đánh giá",
                "detail": "Bọc bánh xà phòng bằng giấy kraft, dán nhãn Mộc Đông và chụp 1 bức ảnh rõ nét thành phẩm (chỉ chụp bánh xà phòng, không chụp mặt). Sau đó điền đầy đủ phiếu thu hoạch, tải ảnh lên và tự chấm 2 bảng rubric bên dưới.",
                "image": "/static/images/edp/b5_3_dong_goi.jpg",
                "caption": "Bọc giấy kraft, dán nhãn hoàn thiện sản phẩm và chụp ảnh báo cáo",
            },
        ],
        "ordered": True,
        "safety": [
            r"Tuyệt đối <b>không</b> dùng xà phòng lên da khi chưa đủ thời gian ủ chín hoặc khi giấy quỳ cho kết quả $\text{pH} > 10$ (xanh đậm).",
            "Nếu thấy da cay rát khi dùng thử, rửa sạch bằng nước nhiều lần và ngừng dùng bánh xà phòng đó.",
            "Khi chụp ảnh sản phẩm, chỉ chụp bánh xà phòng, không chụp khuôn mặt hay thông tin cá nhân.",
        ],
        "steam": [
            {"k": "S", "label": "Khoa học", "text": "Trung hòa kiềm bởi CO₂, đo pH bằng giấy quỳ."},
            {"k": "M", "label": "Toán học", "text": "Tính tổng điểm rubric, so sánh khối lượng bánh trước và sau khi ủ."},
            {"k": "A", "label": "Nghệ thuật", "text": "Thiết kế bao bì giấy kraft và nhãn mác cho sản phẩm."},
        ],
        "quick_prompts": [
            "Giấy quỳ ra xanh đậm thì mình làm gì?",
            "Xà phòng của mình còn mềm, nguyên nhân là gì?",
            "Gợi ý cách cải tiến mẻ sau giúp mình",
        ],
        "ai_system_prompt": (
            "Học sinh đang ở BƯỚC 5 (IMPROVE): thử nghiệm, đánh giá và cải tiến. "
            "Test pH: làm ướt bánh, tạo bọt, áp giấy quỳ; xanh lơ nhẹ (pH 8,5-9,5) là đạt; xanh đậm (pH trên 10) thì ủ thêm 1 tuần rồi test lại, không dùng trên da khi chưa đạt. "
            "Nguyên nhân thường gặp: xà phòng còn mềm (ủ chưa đủ, khuấy chưa tới Trace, cân sai), nứt (ủ quá nóng/gió), mùi dầu thải (lọc chưa kỹ). "
            "Giúp em phân tích nguyên nhân và đề xuất cải tiến cho mẻ sau (chỉ trong phạm vi kit, không khuyên tăng xút). "
            "Với phiếu đánh giá và 2 bảng rubric: giúp em hiểu tiêu chí và tự suy ngẫm, KHÔNG chấm điểm hộ hay viết hộ câu trả lời; "
            "nếu em nhờ viết hộ, hãy gợi ý cách nghĩ rồi để em tự viết."
        ),
        "quiz": [
            {"q": "Giấy quỳ tím áp vào bọt xà phòng chuyển xanh đậm (pH > 10). Nên làm gì?",
             "options": ["Dùng ngay vì xà phòng càng kiềm càng sạch", "Ủ thêm khoảng 1 tuần rồi test lại",
                         "Thêm nước vào bánh xà phòng", "Đổ bỏ và không dùng nữa"],
             "correct": 1,
             "explain": "pH cao nghĩa là còn kiềm bề mặt. Ủ thêm 1 tuần để CO₂ trung hòa, rồi test lại mới được dùng."},
            {"q": "Điều gì làm pH của bánh xà phòng giảm trong quá trình ủ?",
             "options": ["CO₂ trong không khí trung hòa kiềm bề mặt", "Ánh nắng trực tiếp phân hủy xút",
                         "Nước ép nho hấp thụ hết kiềm", "Nhiệt độ lạnh"],
             "correct": 0,
             "explain": "2NaOH + CO₂ → Na₂CO₃ + H₂O: kiềm dư vi lượng ở bề mặt được trung hòa dần."},
            {"q": "Thành phần nào chủ yếu giúp bánh xà phòng tạo nhiều bọt?",
             "options": ["Nước cất", "Dầu dừa", "Tinh dầu", "Nước ép nho"],
             "correct": 1,
             "explain": "Dầu dừa giàu axit lauric nên cho bọt to, nhiều và làm bánh cứng."},
            {"q": "Vì sao nên ghi nhật ký mẻ làm (thời gian khuấy, màu sắc…)?",
             "options": ["Chỉ để cô giáo chấm điểm", "Để phân tích nguyên nhân và cải tiến cho mẻ sau",
                         "Để bánh xà phòng cứng hơn", "Không cần thiết"],
             "correct": 1,
             "explain": "Dữ liệu ghi lại giúp bạn so sánh các mẻ, tìm nguyên nhân lỗi và điều chỉnh có căn cứ – đó là bước “Improve” của EDP."},
        ],
    },
]

TOTAL_STEPS = len(STEPS)

STEAM_NAMES = {"S": "Science", "T": "Technology", "E": "Engineering", "A": "Art", "M": "Mathematics"}


def get_step(n):
    return STEPS[n - 1] if 1 <= n <= TOTAL_STEPS else None


# =====================================================================
# PHIẾU ĐÁNH GIÁ BƯỚC 5
# =====================================================================
FEEDBACK_QUESTIONS = [
    {"key": "class_name", "label": "Lớp", "type": "text", "required": True, "maxlength": 40,
     "hint": "Ví dụ: 8A2"},
    {"key": "school", "label": "Trường", "type": "text", "required": True, "maxlength": 120,
     "hint": "Tên trường của bạn"},
    {"key": "learned", "label": "Kiến thức / kỹ năng em đã học được", "type": "textarea", "required": True, "maxlength": 1000,
     "hint": "Ví dụ: phản ứng xà phòng hóa, cách nhận biết Trace, đo pH..."},
    {"key": "unclear", "label": "Kiến thức em còn chưa rõ", "type": "textarea", "required": True, "maxlength": 1000,
     "hint": "Nếu đã hiểu hết, hãy ghi “Không có” và nêu một câu hỏi em muốn tìm hiểu thêm."},
    {"key": "lesson", "label": "Bài học rút ra & điều em sẽ cải tiến ở mẻ sau", "type": "textarea", "required": True, "maxlength": 1000,
     "hint": "Em sẽ làm khác đi điều gì? Vì sao?"},
    {"key": "batch_log", "label": "Nhật ký mẻ làm (không bắt buộc)", "type": "textarea", "required": False, "maxlength": 1000,
     "hint": "Khuấy bao lâu thì đặc, màu lên thế nào, gặp khó khăn gì..."},
]

RUBRIC_TABLE_1 = {
    "id": "r1",
    "title": "Bảng 1 – Đánh giá chất lượng kỹ thuật & cảm quan sản phẩm",
    "subtitle": "Chấm bánh xà phòng của bạn theo thang 1 – 4 cho mỗi tiêu chí (tối đa 20 điểm).",
    "max": 20,
    "criteria": [
        {"key": "ph", "label": "Độ pH an toàn (8,5 – 9,5)", "levels": [
            "pH > 10 hoặc không đo được",
            "pH 9,6 – 10, cần ủ thêm",
            "pH 8,5 – 9,5, giấy quỳ xanh lơ nhẹ",
            "pH ổn định 8,5 – 9,0, cảm giác da tốt"]},
        {"key": "structure", "label": "Độ cứng & kết cấu khối", "levels": [
            "Mềm, bở, vỡ vụn",
            "Còn mềm nhẹ hoặc có vết nứt",
            "Cứng vừa, tháo khuôn đẹp",
            "Cứng chắc, bề mặt mịn, không nứt"]},
        {"key": "foam", "label": "Khả năng tạo bọt & làm sạch", "levels": [
            "Bọt ít, rửa kém",
            "Bọt vừa, tẩy dầu trung bình",
            "Bọt nhiều, sạch dầu tốt",
            "Bọt dồi dào, sạch sâu, da không khô"]},
        {"key": "scent_color", "label": "Mùi hương & màu sắc tự nhiên", "levels": [
            "Mùi dầu thải rõ, màu xấu",
            "Mùi nhẹ, màu không đều",
            "Mùi nho / thảo mộc dễ chịu, màu đẹp",
            "Mùi thơm tự nhiên, màu xanh rêu / nâu trầm đẹp"]},
        {"key": "look", "label": "Thẩm mỹ hình dáng & đóng gói", "levels": [
            "Biến dạng, không đóng gói",
            "Hình dạng tạm ổn, nhãn sơ sài",
            "Đúng khuôn, bọc kraft + nhãn cơ bản",
            "Đẹp, nhãn rõ ràng, đóng gói chuyên nghiệp"]},
    ],
}

RUBRIC_TABLE_2 = {
    "id": "r2",
    "title": "Bảng 2 – Tự đánh giá năng lực thực hiện quy trình EDP",
    "subtitle": "Tự chấm năng lực của bạn theo thang 1 – 4 cho mỗi tiêu chí (tối đa 20 điểm).",
    "max": 20,
    "criteria": [
        {"key": "understanding", "label": "Mức độ hiểu nguyên lý khoa học (xà phòng hóa, pH, superfat)", "levels": [
            "Chỉ làm theo, không giải thích được",
            "Giải thích được một phần",
            "Giải thích rõ ràng hầu hết kiến thức",
            "Hiểu sâu và liên hệ được với thực tế"]},
        {"key": "precision", "label": "Tính chính xác khi thiết kế / cân đong công thức", "levels": [
            "Sai số lớn, thiếu nguyên liệu",
            "Sai số nhỏ hoặc quên 1 – 2 bước",
            "Cân đong đúng, đúng thứ tự",
            "Chính xác tuyệt đối và ghi nhật ký đầy đủ"]},
        {"key": "safety", "label": "Tuân thủ an toàn thí nghiệm", "levels": [
            "Thiếu găng / kính, đổ sai thứ tự",
            "Có dụng cụ nhưng còn sơ suất",
            "Đầy đủ bảo hộ, đúng quy trình an toàn",
            "Chủ động nhắc bạn bè, xử lý tình huống an toàn tốt"]},
        {"key": "analysis", "label": "Khả năng phân tích dữ liệu thử nghiệm (pH, bọt, lỗi)", "levels": [
            "Không ghi nhận / không phân tích",
            "Ghi nhận nhưng phân tích yếu",
            "Phân tích đúng nguyên nhân chính",
            "Phân tích sâu và đề xuất cải tiến cụ thể"]},
        {"key": "teamwork", "label": "Tinh thần hợp tác & cải tiến sản phẩm", "levels": [
            "Làm một mình, không chia sẻ",
            "Có chia sẻ nhưng ít đóng góp",
            "Hợp tác tốt, ghi nhận lỗi",
            "Chủ động cải tiến, chia sẻ kinh nghiệm với nhóm"]},
    ],
}

GRADE_BANDS = [[18, "Xuất sắc"], [16, "Đạt chuẩn"], [10, "Cần cải thiện"], [0, "Chưa đạt"]]


def grade(total):
    for lo, label in GRADE_BANDS:
        if total >= lo:
            return label
    return GRADE_BANDS[-1][1]