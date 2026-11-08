/* MD Work — language, theme and small interactions */
(function () {
  "use strict";

  var I18N = window.I18N || {};
  var LANGS = Object.keys(I18N);
  var RTL = ["ar", "he", "fa", "ur"];
  var root = document.documentElement;

  function safeGet(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }
  function safeSet(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* private mode */ }
  }

  /* ---------- language ---------- */
  function detectLang() {
    var saved = safeGet("mdwork.lang");
    if (saved && I18N[saved]) return saved;
    var list = navigator.languages || [navigator.language || "en"];
    for (var i = 0; i < list.length; i++) {
      var code = String(list[i]).toLowerCase().split("-")[0];
      if (I18N[code]) return code;
    }
    return "en";
  }

  function applyLang(code) {
    if (!I18N[code]) return;
    var dict = I18N[code];
    root.lang = code;
    root.dir = RTL.indexOf(code) >= 0 ? "rtl" : "ltr";

    var nodes = document.querySelectorAll("[data-i18n]");
    for (var i = 0; i < nodes.length; i++) {
      var key = nodes[i].getAttribute("data-i18n");
      if (dict[key]) nodes[i].textContent = dict[key];
    }
    var select = document.getElementById("lang");
    if (select && select.value !== code) select.value = code;
    safeSet("mdwork.lang", code);
  }

  /* ---------- theme ---------- */
  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    var btn = document.getElementById("theme");
    if (btn) btn.setAttribute("aria-pressed", theme === "light" ? "true" : "false");
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", theme === "light" ? "#f5f7fb" : "#070b12");
    safeSet("mdwork.theme", theme);
  }

  function initTheme() {
    var saved = safeGet("mdwork.theme");
    if (saved === "light" || saved === "dark") { applyTheme(saved); return; }
    var prefersLight = window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches;
    applyTheme(prefersLight ? "light" : "dark");
  }

  /* ---------- init ---------- */
  function init() {
    initTheme();
    applyLang(detectLang());

    var langSelect = document.getElementById("lang");
    if (langSelect) {
      langSelect.addEventListener("change", function () { applyLang(langSelect.value); });
    }

    var themeBtn = document.getElementById("theme");
    if (themeBtn) {
      themeBtn.addEventListener("click", function () {
        applyTheme(root.getAttribute("data-theme") === "light" ? "dark" : "light");
      });
    }

    /* sticky download bar on small screens */
    var bar = document.getElementById("stickybar");
    var footer = document.querySelector(".footer");
    if (bar && footer) {
      var footerVisible = false;
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (entries) {
          footerVisible = entries[0].isIntersecting;
          syncBar();
        }, { threshold: 0.01 }).observe(footer);
      }
      var ticking = false;
      var syncBar = function () {
        bar.hidden = !(window.scrollY > 460) || footerVisible;
        ticking = false;
      };
      window.addEventListener("scroll", function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(syncBar);
      }, { passive: true });
      syncBar();
    }

    /* reveal on scroll */
    var revealTargets = document.querySelectorAll(".card, .step, .screens__item, .cta__copy, .strip__item");
    if ("IntersectionObserver" in window && revealTargets.length) {
      var revealObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            revealObserver.unobserve(entry.target);
          }
        });
      }, { rootMargin: "0px 0px -8% 0px", threshold: 0.12 });
      revealTargets.forEach(function (el) {
        el.classList.add("reveal");
        revealObserver.observe(el);
      });
    }

    /* keyboard: keep only one FAQ answer open */
    var qas = document.querySelectorAll(".qa");
    qas.forEach(function (qa) {
      qa.addEventListener("toggle", function () {
        if (!qa.open) return;
        qas.forEach(function (other) { if (other !== qa) other.open = false; });
      });
    });

    /* web app install prompt, when the browser offers it */
    var deferredPrompt = null;
    window.addEventListener("beforeinstallprompt", function (event) {
      event.preventDefault();
      deferredPrompt = event;
    });
    document.querySelectorAll('a[href*="play.google.com"]').forEach(function (link) {
      link.addEventListener("click", function () {
        if (deferredPrompt) {
          deferredPrompt.prompt();
          deferredPrompt = null;
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
