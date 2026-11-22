/* MD Work — language, theme and small interactions */
(function () {
  "use strict";

  var LANGS = ["en", "it", "fr", "de", "ar", "hi"];
  var RTL = ["ar", "he", "fa", "ur"];
  var root = document.documentElement;

  function safeGet(key) {
    try { return localStorage.getItem(key); } catch (e) { return null; }
  }
  function safeSet(key, value) {
    try { localStorage.setItem(key, value); } catch (e) { /* private mode */ }
  }

  /* ---------- language ----------
     English is the page language. Another dictionary is fetched only when
     someone picks it, so the first load carries a single translation. */
  function loadDictionary(code, done) {
    if (window.I18N && window.I18N[code]) { done(); return; }
    var script = document.createElement("script");
    script.src = "assets/js/i18n/" + code + ".js";
    script.onload = done;
    script.onerror = done;
    document.head.appendChild(script);
  }

  function paint(code) {
    var dict = (window.I18N || {})[code];
    if (!dict) return false;
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
    return true;
  }

  function setLang(code) {
    if (LANGS.indexOf(code) < 0) code = "en";
    if (paint(code)) return;
    loadDictionary(code, function () { paint(code); });
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

    var savedLang = safeGet("mdwork.lang");
    setLang(savedLang && LANGS.indexOf(savedLang) >= 0 ? savedLang : "en");

    var langSelect = document.getElementById("lang");
    if (langSelect) {
      langSelect.addEventListener("change", function () { setLang(langSelect.value); });
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
      var syncBar = function () {
        bar.hidden = !(window.scrollY > 460) || footerVisible;
        ticking = false;
      };
      var ticking = false;
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (entries) {
          footerVisible = entries[0].isIntersecting;
          syncBar();
        }, { threshold: 0.01 }).observe(footer);
      }
      window.addEventListener("scroll", function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(syncBar);
      }, { passive: true });
      syncBar();
    }

    /* keep one FAQ answer open at a time */
    var qas = document.querySelectorAll(".qa");
    for (var i = 0; i < qas.length; i++) {
      (function (qa) {
        qa.addEventListener("toggle", function () {
          if (!qa.open) return;
          for (var j = 0; j < qas.length; j++) if (qas[j] !== qa) qas[j].open = false;
        });
      })(qas[i]);
    }

    /* web app install prompt, when the browser offers it */
    var deferredPrompt = null;
    window.addEventListener("beforeinstallprompt", function (event) {
      event.preventDefault();
      deferredPrompt = event;
    });
    var playLinks = document.querySelectorAll('a[href*="play.google.com"]');
    for (var k = 0; k < playLinks.length; k++) {
      playLinks[k].addEventListener("click", function () {
        if (deferredPrompt) {
          deferredPrompt.prompt();
          deferredPrompt = null;
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
