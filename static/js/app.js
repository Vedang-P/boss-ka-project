document.addEventListener("DOMContentLoaded", () => {
  const THEME_KEY = "study_theme";
  const root = document.documentElement;
  const themeToggle = document.querySelector("[data-theme-toggle]");
  const revealElements = document.querySelectorAll(".reveal");

  const setTheme = (theme) => {
    root.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
    if (!themeToggle) {
      return;
    }
    themeToggle.textContent = theme === "dark" ? "Light mode" : "Dark mode";
    themeToggle.setAttribute(
      "aria-pressed",
      theme === "dark" ? "true" : "false",
    );
  };

  if (themeToggle) {
    const current = root.getAttribute("data-theme") || "light";
    setTheme(current);
    themeToggle.addEventListener("click", () => {
      const next =
        root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      setTheme(next);
    });
  }

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    revealElements.forEach((element) => element.classList.add("is-visible"));
    return;
  }

  if (!("IntersectionObserver" in window)) {
    revealElements.forEach((element) => element.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.08 },
  );

  revealElements.forEach((element) => observer.observe(element));

  const explorer = document.querySelector("[data-task-explorer]");
  if (!explorer) {
    return;
  }

  const searchInput = explorer.querySelector("#task-search");
  const chips = explorer.querySelectorAll("[data-task-filter]");
  const rows = explorer.querySelectorAll("[data-task-item]");
  const visibleCount = explorer.querySelector("[data-task-count]");
  const emptyHint = explorer.querySelector("[data-task-empty]");
  let activeFilter = "all";

  const isVisibleForFilter = (row, filterName) => {
    const priority = parseFloat(row.dataset.priority || "0");
    const dueDays = parseInt(row.dataset.days || "999", 10);
    const taskType = row.dataset.type || "";
    const completed = row.dataset.completed === "true";

    if (filterName === "high") {
      return priority >= 70;
    }
    if (filterName === "due") {
      return dueDays <= 2 && !completed;
    }
    if (filterName === "exam") {
      return taskType === "exam" || taskType === "quiz";
    }
    if (filterName === "manual") {
      return taskType === "manual";
    }
    if (filterName === "open") {
      return !completed;
    }
    return true;
  };

  const applyFilters = () => {
    const query = (searchInput?.value || "").trim().toLowerCase();
    let count = 0;

    rows.forEach((row) => {
      const title = row.dataset.title || "";
      const course = row.dataset.course || "";
      const searchPass =
        !query || title.includes(query) || course.includes(query);
      const filterPass = isVisibleForFilter(row, activeFilter);
      const show = searchPass && filterPass;
      row.classList.toggle("hidden", !show);
      if (show) {
        count += 1;
      }
    });

    if (visibleCount) {
      visibleCount.textContent = String(count);
    }
    if (emptyHint) {
      emptyHint.classList.toggle("hidden", count > 0);
    }
  };

  chips.forEach((chip) => {
    chip.addEventListener("click", () => {
      activeFilter = chip.dataset.taskFilter || "all";
      chips.forEach((item) => item.classList.remove("is-active"));
      chip.classList.add("is-active");
      applyFilters();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", applyFilters);
  }

  applyFilters();

  // Task completion toggle
  document.querySelectorAll(".task-toggle-btn").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const pk = btn.dataset.taskPk;
      const csrfToken = document.cookie
        .split(";")
        .find((c) => c.trim().startsWith("csrftoken="));
      const csrf = csrfToken ? csrfToken.trim().split("=")[1] : "";
      fetch(`/academics/task/${pk}/toggle/`, {
        method: "POST",
        headers: {
          "X-CSRFToken": csrf,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        credentials: "same-origin",
      })
        .then((r) => r.json())
        .then((data) => {
          if (!data.ok) return;
          const row = btn.closest("[data-task-item]");
          if (row) {
            row.dataset.completed = data.is_completed ? "true" : "false";
            row.classList.toggle("is-complete", data.is_completed);
          }
          btn.textContent = data.is_completed ? "Reopen" : "Done";
          btn.dataset.completed = data.is_completed ? "true" : "false";
          // Update status pill
          const pill = row && row.querySelector(".status-pill");
          if (pill) {
            pill.textContent = data.is_completed ? "Completed" : "Open";
            pill.className = `status-pill ${data.is_completed ? "status-done" : "status-open"}`;
          }
          applyFilters();
        })
        .catch(() => {});
    });
  });
});
