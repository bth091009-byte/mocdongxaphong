// Đăng nhập / đăng ký bằng Firebase Authentication (Google + Email/Mật khẩu)
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.14.1/firebase-app.js";
import {
  getAuth, GoogleAuthProvider, signInWithPopup,
  signInWithEmailAndPassword, createUserWithEmailAndPassword,
  updateProfile, sendPasswordResetEmail, signOut,
} from "https://www.gstatic.com/firebasejs/10.14.1/firebase-auth.js";

const root = document.getElementById("auth");
const msg = document.getElementById("auth-msg");
const nextUrl = root.dataset.next || "";
const cfg = window.FIREBASE_CONFIG || {};

const ERRORS = {
  "auth/invalid-email": "Email chưa đúng định dạng.",
  "auth/user-not-found": "Email hoặc mật khẩu chưa đúng.",
  "auth/wrong-password": "Email hoặc mật khẩu chưa đúng.",
  "auth/invalid-credential": "Email hoặc mật khẩu chưa đúng.",
  "auth/email-already-in-use": "Email này đã có tài khoản. Hãy chuyển sang tab Đăng nhập.",
  "auth/weak-password": "Mật khẩu cần có ít nhất 6 ký tự.",
  "auth/too-many-requests": "Bạn thử quá nhiều lần. Hãy đợi vài phút rồi thử lại.",
  "auth/network-request-failed": "Mất kết nối mạng. Hãy kiểm tra internet và thử lại.",
  "auth/popup-blocked": "Trình duyệt đã chặn cửa sổ đăng nhập Google. Hãy cho phép cửa sổ bật lên rồi thử lại.",
  "auth/unauthorized-domain": "Tên miền này chưa được thêm vào Authorized domains trong Firebase.",
  "auth/operation-not-allowed": "Phương thức đăng nhập này chưa được bật trong Firebase.",
  "auth/user-disabled": "Tài khoản này đã bị vô hiệu hóa.",
};
const SILENT = new Set(["auth/popup-closed-by-user", "auth/cancelled-popup-request"]);

function show(text, type = "error") {
  msg.hidden = !text;
  msg.textContent = text || "";
  msg.className = "form-msg " + type;
}
function explain(err) {
  if (SILENT.has(err.code)) return "";
  return ERRORS[err.code] || err.message || "Có lỗi xảy ra. Vui lòng thử lại.";
}
function busy(on) {
  root.querySelectorAll("button").forEach((b) => (b.disabled = on));
}

if (!cfg.apiKey) {
  busy(true);
} else {
  const app = initializeApp(cfg);
  const auth = getAuth(app);
  auth.languageCode = "vi";
  // Trang này chỉ hiện khi server chưa có phiên đăng nhập -> dọn trạng thái Firebase cũ ở trình duyệt
  signOut(auth).catch(() => {});

  // Gửi ID token cho Flask để xác thực, lưu user vào Firestore và mở phiên
  async function finish(user, fullName = "") {
    const idToken = await user.getIdToken(true);
    const res = await fetch("/api/auth/session", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id_token: idToken, full_name: fullName, next: nextUrl }),
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      await signOut(auth).catch(() => {});
      throw new Error(data.error || "Không thể đăng nhập. Vui lòng thử lại.");
    }
    location.href = data.redirect || "/";
  }

  async function run(fn) {
    show("");
    busy(true);
    try {
      await fn();
    } catch (err) {
      show(explain(err));
      busy(false);
    }
  }

  document.getElementById("google-btn").addEventListener("click", () =>
    run(async () => {
      const cred = await signInWithPopup(auth, new GoogleAuthProvider());
      await finish(cred.user, cred.user.displayName || "");
    })
  );

  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");

  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const f = new FormData(loginForm);
    const email = f.get("email").trim(), pw = f.get("password");
    if (!email || !pw) return show("Hãy nhập email và mật khẩu.");
    run(async () => {
      const cred = await signInWithEmailAndPassword(auth, email, pw);
      await finish(cred.user, cred.user.displayName || "");
    });
  });

  registerForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const f = new FormData(registerForm);
    const name = f.get("full_name").trim(), email = f.get("email").trim();
    const pw = f.get("password"), pw2 = f.get("password2");
    if (!name || !email || !pw) return show("Hãy điền đầy đủ họ tên, email và mật khẩu.");
    if (pw.length < 6) return show(ERRORS["auth/weak-password"]);
    if (pw !== pw2) return show("Hai mật khẩu chưa giống nhau.");
    run(async () => {
      const cred = await createUserWithEmailAndPassword(auth, email, pw);
      await updateProfile(cred.user, { displayName: name });
      await finish(cred.user, name);
    });
  });

  document.getElementById("forgot-btn").addEventListener("click", () => {
    const email = loginForm.elements.email.value.trim();
    if (!email) return show("Nhập email của bạn ở trên, rồi bấm Quên mật khẩu.");
    run(async () => {
      await sendPasswordResetEmail(auth, email);
      show("Đã gửi email đặt lại mật khẩu. Hãy kiểm tra hộp thư (cả mục Spam).", "ok");
      busy(false);
    });
  });
}

// Chuyển tab Đăng nhập / Đăng ký
root.querySelectorAll(".auth-tabs button").forEach((btn) => {
  btn.addEventListener("click", () => {
    const reg = btn.dataset.tab === "register";
    root.querySelectorAll(".auth-tabs button").forEach((b) => {
      const on = b === btn;
      b.classList.toggle("active", on);
      b.setAttribute("aria-selected", on);
    });
    document.getElementById("login-form").hidden = reg;
    document.getElementById("register-form").hidden = !reg;
    show("");
  });
});
