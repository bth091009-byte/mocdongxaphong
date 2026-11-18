(function () {
  function getUserContext() {
    const oilEl = document.getElementById("c-oil");
    const cocoEl = document.getElementById("c-coco");
    const sfEl = document.getElementById("c-sf");
    if (oilEl && cocoEl && sfEl) {
      return `Đang tính thử: ${oilEl.value}g dầu ăn thải, ${cocoEl.value}g dầu dừa, superfat ${sfEl.value}%`;
    }
    return "";
  }

  function appendBubble(logEl, text, who) {
    if (!logEl) return null;
    const d = document.createElement("div");
    d.className = "bubble " + who;
    d.textContent = text;
    logEl.appendChild(d);
    logEl.scrollTop = logEl.scrollHeight;
    return d;
  }

  async function askBot(stepId, msg, targetLogs) {
    const cleanMsg = (msg || "").trim();
    if (!cleanMsg) return;

    const waits = targetLogs.map(logEl => {
      appendBubble(logEl, cleanMsg, "me");
      return appendBubble(logEl, "Đang soạn tin...", "bot");
    });

    try {
      const r = await fetch("/api/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          message: cleanMsg,
          step_id: stepId,
          user_context: getUserContext()
        })
      });
      const data = await r.json();
      const replyText = data.reply || data.error || "Mình chưa nhận được phản hồi, bạn thử lại nhé.";
      waits.forEach((w, idx) => {
        if (w) {
          w.textContent = replyText;
          targetLogs[idx].scrollTop = targetLogs[idx].scrollHeight;
        }
      });
    } catch {
      waits.forEach((w, idx) => {
        if (w) {
          w.textContent = "Không kết nối được, bạn thử lại nhé 🌿";
          targetLogs[idx].scrollTop = targetLogs[idx].scrollHeight;
        }
      });
    }
  }

  // 1. Widget chatbot nổi góc dưới phải
  const box = document.getElementById("chat-box");
  const floatLog = document.getElementById("chat-log");
  const floatInput = document.getElementById("chat-text");
  const stepBotCard = document.getElementById("step-bot");
  const inlineLog = document.getElementById("inline-chat-log");
  const inlineInput = document.getElementById("inline-chat-text");

  const stepId = parseInt(
    (stepBotCard && stepBotCard.dataset.stepId) ||
    (box && box.dataset.currentStep) ||
    "0",
    10
  ) || 0;

  const allLogs = [floatLog, inlineLog].filter(Boolean);

  if (box && floatLog && floatInput) {
    const toggleBtn = document.getElementById("chat-toggle");
    if (toggleBtn) {
      toggleBtn.onclick = () => {
        box.hidden = !box.hidden;
        if (!box.hidden) floatInput.focus();
      };
    }

    const closeBtn = document.getElementById("chat-close");
    if (closeBtn) closeBtn.onclick = () => { box.hidden = true; };

    const sendFloat = () => {
      const msg = floatInput.value.trim();
      if (!msg) return;
      floatInput.value = "";
      askBot(stepId, msg, allLogs);
    };

    const floatSendBtn = document.getElementById("chat-send");
    if (floatSendBtn) floatSendBtn.onclick = sendFloat;
    floatInput.addEventListener("keydown", e => { if (e.key === "Enter") sendFloat(); });
  }

  // 2. Khung chatbot nhúng trực tiếp trong từng bước EDP
  if (stepBotCard && inlineLog && inlineInput) {
    const sendInline = () => {
      const msg = inlineInput.value.trim();
      if (!msg) return;
      inlineInput.value = "";
      askBot(stepId, msg, allLogs);
    };

    const inlineSendBtn = document.getElementById("inline-chat-send");
    if (inlineSendBtn) inlineSendBtn.onclick = sendInline;
    inlineInput.addEventListener("keydown", e => {
      if (e.key === "Enter") {
        e.preventDefault();
        sendInline();
      }
    });
  }

  // 3. Các nút câu hỏi gợi ý (cả trong trang bước và trong khung chat nổi)
  document.querySelectorAll(".quick-chip").forEach(chip => {
    chip.addEventListener("click", () => {
      const prompt = chip.dataset.prompt || chip.textContent;
      askBot(stepId, prompt, allLogs);
      if (inlineLog && chip.classList.contains("inline-chip")) {
        inlineLog.scrollIntoView({ behavior: "smooth", block: "nearest" });
      }
    });
  });

  document.querySelectorAll("[data-open-chat]").forEach(btn => {
    btn.addEventListener("click", () => {
      if (stepBotCard) {
        stepBotCard.scrollIntoView({ behavior: "smooth", block: "center" });
        if (inlineInput) inlineInput.focus();
      } else if (box) {
        box.hidden = false;
        if (floatInput) floatInput.focus();
      }
    });
  });
})();