/* ===== SafeSpace — Progressive Web App ===== */
(function () {
  "use strict";

  // ---- DOM refs ----
  const screenInput   = document.getElementById("screen-input");
  const screenLoading = document.getElementById("screen-loading");
  const screenResult  = document.getElementById("screen-result");
  const form          = document.getElementById("form-analyze");
  const textarea      = document.getElementById("input-text");
  const charCurrent   = document.getElementById("char-current");
  const btnSubmit     = document.getElementById("btn-submit");
  const btnBack       = document.getElementById("btn-back");
  const emergencyBanner  = document.getElementById("emergency-banner");
  const resultCategory   = document.getElementById("result-category");
  const resultSeriousness = document.getElementById("result-seriousness");
  const resultSummary    = document.getElementById("result-summary");
  const resultActions    = document.getElementById("result-actions");
  const supportSchool    = document.getElementById("support-school");
  const supportOfficial  = document.getElementById("support-official");
  const resultDisclaimers = document.getElementById("result-disclaimers");
  const resultMode       = document.getElementById("result-mode");

  // ---- Helpers ----
  function show(screen) {
    [screenInput, screenLoading, screenResult].forEach(function (s) {
      s.classList.remove("active");
    });
    screen.classList.add("active");
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function escapeHtml(text) {
    var div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }

  // ---- Character counter ----
  textarea.addEventListener("input", function () {
    charCurrent.textContent = textarea.value.length;
  });

  // ---- Form submit ----
  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    var text = textarea.value.trim();
    if (!text) return;

    btnSubmit.classList.add("loading");
    show(screenLoading);

    try {
      var res = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text }),
      });

      if (!res.ok) {
        var errData = await res.json().catch(function () { return {}; });
        throw new Error(errData.detail || "Something went wrong. Please try again.");
      }

      var data = await res.json();
      renderResult(data);
      show(screenResult);
    } catch (err) {
      alert(err.message || "Could not reach the server. Please check your connection.");
      show(screenInput);
    } finally {
      btnSubmit.classList.remove("loading");
    }
  });

  // ---- Back button ----
  btnBack.addEventListener("click", function () {
    show(screenInput);
    textarea.focus();
  });

  // ---- Render result ----
  function renderResult(data) {
    // Emergency banner
    if (data.emergency_banner) {
      emergencyBanner.hidden = false;
    } else {
      emergencyBanner.hidden = true;
    }

    // Category
    resultCategory.textContent = data.category || "General";

    // Seriousness
    var sev = (data.seriousness || "moderate").toLowerCase();
    resultSeriousness.textContent = sev;
    resultSeriousness.className = "seriousness-badge seriousness-" + sev;

    // Summary
    resultSummary.textContent = data.summary || "";

    // Actions
    resultActions.innerHTML = "";
    (data.actions || []).forEach(function (action) {
      var li = document.createElement("li");
      li.textContent = action;
      resultActions.appendChild(li);
    });

    // School support
    supportSchool.innerHTML = "";
    var school = data.support && data.support.school ? data.support.school : [];
    school.forEach(function (item) {
      var li = document.createElement("li");
      li.innerHTML = "🏫 " + escapeHtml(item);
      supportSchool.appendChild(li);
    });

    // Official resources
    supportOfficial.innerHTML = "";
    var official = data.support && data.support.official ? data.support.official : [];
    official.forEach(function (resource) {
      var li = document.createElement("li");
      var label = escapeHtml(resource.name || "");

      if (resource.contact) {
        li.innerHTML = "📞 " + label +
          '<a href="tel:' + escapeHtml(resource.contact) + '" class="contact-link">' +
          escapeHtml(resource.contact) + "</a>";
      } else if (resource.url) {
        li.innerHTML = "🔗 " + label +
          '<a href="' + escapeHtml(resource.url) + '" target="_blank" rel="noopener" class="contact-link">Open</a>';
      } else {
        li.innerHTML = "ℹ️ " + label;
      }

      supportOfficial.appendChild(li);
    });

    // Disclaimers
    resultDisclaimers.innerHTML = "";
    (data.disclaimers || []).forEach(function (d) {
      var li = document.createElement("li");
      li.textContent = d;
      resultDisclaimers.appendChild(li);
    });

    // Mode
    var modeLabels = {
      ai: "Powered by AI",
      fallback: "Offline guidance (AI unavailable)",
      urgent: "Safety response",
    };
    resultMode.textContent = modeLabels[data.mode] || data.mode;
  }

  // ---- PWA Install Prompt ----
  var deferredPrompt = null;
  var installBanner = document.getElementById("install-banner");
  var btnInstall = document.getElementById("btn-install");
  var btnDismiss = document.getElementById("btn-dismiss-install");

  window.addEventListener("beforeinstallprompt", function (e) {
    e.preventDefault();
    deferredPrompt = e;
    if (!localStorage.getItem("pwa-install-dismissed")) {
      installBanner.hidden = false;
    }
  });

  if (btnInstall) {
    btnInstall.addEventListener("click", async function () {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      var choice = await deferredPrompt.userChoice;
      if (choice.outcome === "accepted") {
        installBanner.hidden = true;
      }
      deferredPrompt = null;
    });
  }

  if (btnDismiss) {
    btnDismiss.addEventListener("click", function () {
      installBanner.hidden = true;
      localStorage.setItem("pwa-install-dismissed", "1");
    });
  }

  // ---- Register Service Worker ----
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", function () {
      navigator.serviceWorker.register("/static/sw.js").catch(function (err) {
        console.log("SW registration failed:", err);
      });
    });
  }
})();
