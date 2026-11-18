// Chỗ dành cho hiệu ứng giao diện sau này
document.querySelectorAll("#howto .howto-tabs button").forEach(btn => {
  btn.addEventListener("click", () => {
    const n = btn.dataset.step;
    document.querySelectorAll("#howto .howto-tabs button").forEach(b => {
      const on = b === btn;
      b.classList.toggle("active", on);
      b.setAttribute("aria-selected", on);
    });
    document.querySelectorAll("#howto .step-panel").forEach(p => {
      p.hidden = p.dataset.panel !== n;
    });
  });
});
// Hiện dần khi cuộn tới
(function () {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (!("IntersectionObserver" in window) || reduce) return;

  const sel = [
    ".hero > div", ".section h1", ".section h2", ".section > p", ".story p",
    ".story blockquote", ".story-end", ".card", ".howto", ".steps li",
    ".icons", ".leaf li"
  ].join(",");

  document.documentElement.classList.add("js-reveal");

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (e.isIntersecting) {
        e.target.classList.add("in");
        io.unobserve(e.target);
      }
    });
  }, { threshold: 0.12, rootMargin: "0px 0px -8% 0px" });

  document.querySelectorAll(sel).forEach((el) => {
    // Các mục cùng danh sách hiện lần lượt, cách nhau 0,12 giây
    if (el.tagName === "LI" || el.classList.contains("card")) {
      const i = Math.min([...el.parentNode.children].indexOf(el), 5);
      el.style.transitionDelay = i * 0.12 + "s";
    }
    el.classList.add("reveal");
    io.observe(el);
  });
})();

// Đăng xuất
(function () {
  const btn = document.getElementById("logout-btn");
  if (!btn) return;
  btn.addEventListener("click", async () => {
    btn.disabled = true;
    try {
      const res = await fetch("/api/auth/logout", { method: "POST" });
      const data = await res.json();
      location.href = data.redirect || "/";
    } catch (e) {
      btn.disabled = false;
    }
  });
})();