(function () {
  let saved = null;
  try { saved = localStorage.getItem("theme"); } catch (e) {}
  document.documentElement.setAttribute("data-theme", saved || "dark");

  window.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;
    const render = () => {
      btn.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "☀️" : "🌙";
    };
    render();
    btn.addEventListener("click", () => {
      const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) {}
      render();
      window.dispatchEvent(new Event("themechange"));
    });
  });
})();