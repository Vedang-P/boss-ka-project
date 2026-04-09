/* ==========================================================================
   app.js — Linear-inspired academic dashboard
   Vanilla ES2020, no frameworks, no build step.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", () => {
  /* =========================================================================
     1 — THEME MANAGEMENT
     ======================================================================= */

  const THEME_KEY = "sa_theme";

  function getStoredTheme() {
    try {
      return localStorage.getItem(THEME_KEY) || "light";
    } catch (_error) {
      return "light";
    }
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem(THEME_KEY, theme);
    } catch (_error) {
      // Ignore storage failures so the UI still works in restricted browsers.
    }

    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      const icon = btn.querySelector("[data-theme-icon]");
      const label = btn.querySelector("[data-theme-label]");
      if (theme === "dark") {
        if (icon) icon.textContent = "●";
        if (label) label.textContent = "Light mode";
        if (!icon && !label) btn.textContent = "● Light mode";
      } else {
        if (icon) icon.textContent = "◐";
        if (label) label.textContent = "Dark mode";
        if (!icon && !label) btn.textContent = "◐ Dark mode";
      }
      btn.setAttribute(
        "aria-label",
        theme === "dark" ? "Switch to light mode" : "Switch to dark mode",
      );
    });
  }

  const savedTheme = getStoredTheme();
  applyTheme(savedTheme);

  document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const current =
        document.documentElement.getAttribute("data-theme") || "light";
      applyTheme(current === "dark" ? "light" : "dark");
    });
  });

  /* =========================================================================
     2 — SCROLL REVEAL
     ======================================================================= */

  const revealEls = document.querySelectorAll(".reveal");

  const prefersReduced = window.matchMedia(
    "(prefers-reduced-motion: reduce)",
  ).matches;

  if (prefersReduced || !("IntersectionObserver" in window)) {
    revealEls.forEach((el) => el.classList.add("is-visible"));
  } else {
    const revealObserver = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        });
      },
      { threshold: 0.06 },
    );

    revealEls.forEach((el) => revealObserver.observe(el));
  }

  /* =========================================================================
     3 — FLASH TOAST AUTO-DISMISS
     ======================================================================= */

  function dismissFlash(flash) {
    flash.classList.add("is-hiding");
    setTimeout(() => {
      flash.remove();
    }, 200);
  }

  document.querySelectorAll(".flash").forEach((flash) => {
    const closeBtn = flash.querySelector(".flash-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => dismissFlash(flash));
    }

    setTimeout(() => {
      if (flash.isConnected) {
        dismissFlash(flash);
      }
    }, 4000);
  });

  /* =========================================================================
     4 — STAT COUNTER ANIMATION
     ======================================================================= */

  document.querySelectorAll(".stat-value[data-target]").forEach((el) => {
    const target = parseInt(el.dataset.target, 10);
    const suffix = el.dataset.suffix || "";
    const duration = 800;
    let startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;
      const t = Math.min(elapsed / duration, 1);
      const progress = 1 - Math.pow(1 - t, 3); // ease-out cubic
      const current = progress * target;
      el.textContent = Math.round(current) + suffix;
      if (t < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = target + suffix;
      }
    }

    requestAnimationFrame(step);
  });

  /* =========================================================================
     5 — HEATMAP CELL TOOLTIPS
     ======================================================================= */

  document.querySelectorAll(".heatmap-cell[data-tip]").forEach((cell) => {
    const tip = document.createElement("span");
    tip.className = "heatmap-tooltip";
    tip.textContent = cell.dataset.tip;
    cell.appendChild(tip);
  });

  /* =========================================================================
     6 — TASK EXPLORER FILTERING
     ======================================================================= */

  const explorer = document.querySelector("[data-task-explorer]");

  let applyFilters = () => {}; // hoisted so §7 can reference it

  if (explorer) {
    let activeFilter = "all";

    const searchInput = explorer.querySelector("#task-search");
    const chips = explorer.querySelectorAll("[data-task-filter]");
    const rows = explorer.querySelectorAll("[data-task-item]");
    const countDisplay = explorer.querySelector("[data-task-count]");
    const emptyHint = explorer.querySelector("[data-task-empty]");

    function isVisibleForFilter(row, filter) {
      const priority = parseFloat(row.dataset.priority || "0");
      const days = parseInt(row.dataset.days || "9999", 10);
      const type = row.dataset.type || "";
      const completed = row.dataset.completed === "true";

      switch (filter) {
        case "high":
          return priority >= 70;
        case "due":
          return days <= 2 && !completed;
        case "exam":
          return ["exam", "quiz"].includes(type);
        case "manual":
          return type === "manual";
        case "open":
          return !completed;
        default:
          return true;
      }
    }

    applyFilters = function () {
      const query = (searchInput ? searchInput.value : "").trim().toLowerCase();
      let count = 0;

      rows.forEach((row) => {
        const title = (row.dataset.title || "").toLowerCase();
        const course = (row.dataset.course || "").toLowerCase();

        const matchesSearch =
          !query || title.includes(query) || course.includes(query);
        const matchesFilter = isVisibleForFilter(row, activeFilter);
        const visible = matchesSearch && matchesFilter;

        row.classList.toggle("hidden", !visible);
        if (visible) count++;
      });

      if (countDisplay) countDisplay.textContent = String(count);
      if (emptyHint) emptyHint.classList.toggle("hidden", count > 0);
    };

    chips.forEach((chip) => {
      chip.addEventListener("click", () => {
        activeFilter = chip.dataset.taskFilter || "all";
        chips.forEach((c) => c.classList.remove("is-active"));
        chip.classList.add("is-active");
        applyFilters();
      });
    });

    if (searchInput) {
      searchInput.addEventListener("input", applyFilters);
    }

    applyFilters();
  }

  /* =========================================================================
     7 — AJAX TASK COMPLETION TOGGLE
     ======================================================================= */

  function getCsrfToken() {
    const cookie = document.cookie
      .split(";")
      .map((c) => c.trim())
      .find((c) => c.startsWith("csrftoken="));
    return cookie ? cookie.slice("csrftoken=".length) : "";
  }

  function dotClassFromPriority(priority) {
    if (priority >= 70) return "dot-urgent";
    if (priority >= 40) return "dot-high";
    if (priority >= 20) return "dot-medium";
    return "dot-low";
  }

  document.querySelectorAll(".task-toggle-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();

      const pk = btn.dataset.taskPk;
      const csrf = getCsrfToken();

      fetch(`/academics/task/${pk}/toggle/`, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "X-CSRFToken": csrf,
          "Content-Type": "application/x-www-form-urlencoded",
        },
      })
        .then((r) => r.json())
        .then((data) => {
          if (!data.ok) return;

          const row = btn.closest("[data-task-item]");

          if (row) {
            row.classList.toggle("is-done", data.is_completed);
            row.dataset.completed = data.is_completed ? "true" : "false";

            // Update issue dot
            const dot = row.querySelector(".issue-dot");
            if (dot) {
              if (data.is_completed) {
                dot.classList.remove(
                  "dot-urgent",
                  "dot-high",
                  "dot-medium",
                  "dot-low",
                );
                dot.classList.add("dot-low");
              } else {
                const priority = parseFloat(row.dataset.priority || "0");
                dot.classList.remove(
                  "dot-urgent",
                  "dot-high",
                  "dot-medium",
                  "dot-low",
                );
                dot.classList.add(dotClassFromPriority(priority));
              }
            }
          }

          btn.textContent = data.is_completed ? "Reopen" : "Done";
          btn.dataset.completed = data.is_completed ? "true" : "false";

          applyFilters();
        })
        .catch(() => {});
    });
  });

  /* =========================================================================
     8 — SIDEBAR ACTIVE LINK HIGHLIGHT
     ======================================================================= */

  const pathname = window.location.pathname;

  document.querySelectorAll(".sidebar-item[href]").forEach((item) => {
    const href = item.getAttribute("href");
    let isActive = false;

    if (pathname === "/" && href === "/") {
      isActive = true;
    } else if (href !== "/" && pathname.startsWith(href)) {
      isActive = true;
    }

    item.classList.toggle("is-active", isActive);
  });

  /* =========================================================================
     9 — LIVE URGENCY PREVIEW ON MANUAL TASK FORM
     ======================================================================= */

  const urgencyPreview = document.querySelector("[data-urgency-preview]");

  if (urgencyPreview) {
    const weightInput = document.querySelector('[name="weight_percent"]');
    const difficultyInput = document.querySelector('[name="difficulty"]');
    const typeSelect = document.querySelector('select[name="task_type"]');
    const hoursInput = document.querySelector('[name="estimated_hours"]');
    const dueInput = document.querySelector('[name="due_at"]');
    const barFill = document.querySelector(".urgency-bar-fill");

    const diffMap = { easy: 5, medium: 10, hard: 15 };

    function computeUrgency() {
      // Due component (0–45)
      let dueComponent = 0;
      if (dueInput && dueInput.value) {
        const daysUntil = (new Date(dueInput.value) - new Date()) / 86400000;
        dueComponent =
          daysUntil <= 0 ? 45 : Math.max(0, 45 - Math.min(daysUntil, 14) * 3);
      }

      // Weight component (0–30)
      const weightComponent = Math.min(
        parseFloat(weightInput ? weightInput.value : "0") || 0,
        30,
      );

      // Difficulty component (5 / 10 / 15)
      const diffVal = difficultyInput ? difficultyInput.value : "";
      const difficultyComponent =
        diffMap[diffVal] !== undefined ? diffMap[diffVal] : 10;

      // Time component (0–10)
      const timeComponent = Math.min(
        (parseFloat(hoursInput ? hoursInput.value : "0") || 0) * 2,
        10,
      );

      return Math.round(
        dueComponent + weightComponent + difficultyComponent + timeComponent,
      );
    }

    function updateUrgencyPreview() {
      const score = computeUrgency();

      urgencyPreview.textContent = String(score);

      urgencyPreview.classList.remove(
        "urgency-high",
        "urgency-med",
        "urgency-low",
      );
      if (score >= 70) {
        urgencyPreview.classList.add("urgency-high");
      } else if (score >= 40) {
        urgencyPreview.classList.add("urgency-med");
      } else {
        urgencyPreview.classList.add("urgency-low");
      }

      if (barFill) {
        barFill.style.width = Math.min(score, 100) + "%";
      }
    }

    [weightInput, difficultyInput, typeSelect, hoursInput, dueInput]
      .filter(Boolean)
      .forEach((input) => {
        input.addEventListener("change", updateUrgencyPreview);
        input.addEventListener("input", updateUrgencyPreview);
      });

    // Run once on load to reflect any pre-filled values
    updateUrgencyPreview();
  }
}); /* end DOMContentLoaded */
