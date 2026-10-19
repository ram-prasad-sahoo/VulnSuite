/* VulnSuite — Main JS (minimal) */
"use strict";

// Auto-dismiss flash messages after 5 seconds
document.addEventListener("DOMContentLoaded", () => {
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach((el) => {
    setTimeout(() => {
      el.style.transition = "opacity 0.5s, transform 0.5s";
      el.style.opacity    = "0";
      el.style.transform  = "translateY(-8px)";
      setTimeout(() => el.remove(), 500);
    }, 5000);
  });

  // Syntax highlight in .response-box elements (simple JSON prettify)
  document.querySelectorAll(".response-box[data-json]").forEach((el) => {
    try {
      const parsed = JSON.parse(el.textContent);
      el.textContent = JSON.stringify(parsed, null, 2);
    } catch (e) { /* leave as-is */ }
  });

  // Confirm destructive actions
  document.querySelectorAll("[data-confirm]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      if (!confirm(btn.dataset.confirm)) e.preventDefault();
    });
  });
});
