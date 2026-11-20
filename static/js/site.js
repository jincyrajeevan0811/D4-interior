/* D4 Interiors: site behaviour. No dependencies. Every feature works without JS. */
(function () {
  "use strict";

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  /* ---------- Header: shadow on scroll, mobile menu ---------- */
  var header = $("[data-header]");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }
  var toggle = $("[data-nav-toggle]");
  var nav = $("#site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
      document.body.style.overflow = open ? "hidden" : "";
    };
    toggle.addEventListener("click", function () { setOpen(toggle.getAttribute("aria-expanded") !== "true"); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setOpen(false); });
    window.addEventListener("resize", function () { if (window.innerWidth > 960) setOpen(false); });
  }

  /* ---------- Toasts fade away ---------- */
  $$("[data-toast]").forEach(function (t) {
    setTimeout(function () { t.classList.add("is-leaving"); setTimeout(function () { t.remove(); }, 450); }, 5000);
  });

  /* ---------- Hero: the plot-to-keys build sequence ---------- */
  var build = $("[data-build]");
  if (build) {
    var labels = $$("[data-stage-label]");
    var replay = $("[data-build-replay]");
    var timers = [];
    var STAGE_MS = [0, 1300, 2300, 3700, 4700];

    var mark = function (stage) {
      labels.forEach(function (li, i) {
        li.classList.toggle("is-done", i < stage);
        li.classList.toggle("is-current", i === stage - 1 && stage < 5);
      });
    };
    var finish = function () {
      build.classList.remove("is-animating");
      build.classList.add("is-lit");
      mark(5);
      labels[4] && labels[4].classList.add("is-done");
      if (replay) replay.hidden = false;
    };
    var play = function () {
      timers.forEach(clearTimeout);
      timers = [];
      build.classList.remove("s1", "s2", "s3", "s4", "s5", "is-lit");
      build.classList.add("is-animating");
      if (replay) replay.hidden = true;
      mark(0);
      // Force a reflow so animations restart on replay.
      void build.getBoundingClientRect();
      STAGE_MS.forEach(function (ms, i) {
        timers.push(setTimeout(function () {
          build.classList.add("s" + (i + 1));
          mark(i + 1);
          if (i === 3) build.classList.add("is-lit");
        }, ms + 300));
      });
      timers.push(setTimeout(finish, STAGE_MS[4] + 2200));
    };

    if (reduceMotion) {
      finish();
    } else if ("IntersectionObserver" in window) {
      var started = false;
      new IntersectionObserver(function (entries, obs) {
        if (entries[0].isIntersecting && !started) { started = true; play(); obs.disconnect(); }
      }, { threshold: 0.35 }).observe(build);
    } else {
      finish();
    }
    if (replay) replay.addEventListener("click", play);
  }

  /* ---------- Process timeline fills as you scroll ---------- */
  var track = $("[data-process]");
  if (track) {
    var fill = $("[data-process-fill]", track);
    var steps = $$("[data-process-step]", track);
    var ticking = false;
    var update = function () {
      ticking = false;
      var r = track.getBoundingClientRect();
      var anchor = window.innerHeight * 0.6;
      var p = Math.min(1, Math.max(0, (anchor - r.top) / r.height));
      if (fill) fill.style.setProperty("--p", p.toFixed(3));
      steps.forEach(function (s) {
        s.classList.toggle("is-reached", s.getBoundingClientRect().top + 22 < anchor);
      });
    };
    if (reduceMotion) {
      if (fill) fill.style.setProperty("--p", 1);
      steps.forEach(function (s) { s.classList.add("is-reached"); });
    } else {
      window.addEventListener("scroll", function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
      update();
    }
  }

  /* ---------- Count-up for the stats strip (once) ---------- */
  var counters = $$("[data-count]");
  if (counters.length && !reduceMotion && "IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        io.unobserve(e.target);
        var el = e.target, end = parseInt(el.dataset.count, 10), t0 = null;
        var stepFn = function (ts) {
          if (!t0) t0 = ts;
          var k = Math.min(1, (ts - t0) / 1200);
          el.textContent = Math.round(end * (1 - Math.pow(1 - k, 3)));
          if (k < 1) requestAnimationFrame(stepFn);
        };
        requestAnimationFrame(stepFn);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { io.observe(c); });
  }

  /* ---------- Portfolio filter ---------- */
  var filter = $("[data-filter]");
  var grid = $("[data-filter-grid]");
  if (filter && grid) {
    var empty = $("[data-filter-empty]");
    var apply = function (value) {
      var shown = 0;
      $$(".pcard", grid).forEach(function (card) {
        var match = !value || card.dataset.category === value;
        var wasHidden = card.hidden;
        card.hidden = !match;
        if (match) {
          shown++;
          if (wasHidden || !reduceMotion) {
            card.classList.remove("is-entering");
            void card.offsetWidth;
            card.style.animationDelay = Math.min(shown - 1, 8) * 45 + "ms";
            card.classList.add("is-entering");
          }
        }
      });
      if (empty) empty.hidden = shown > 0;
      $$("[data-filter-value]", filter).forEach(function (b) {
        if (b.dataset.filterValue === value) b.setAttribute("aria-current", "true");
        else b.removeAttribute("aria-current");
      });
    };
    filter.addEventListener("click", function (e) {
      var btn = e.target.closest("[data-filter-value]");
      if (!btn) return;
      e.preventDefault();
      var value = btn.dataset.filterValue;
      var url = new URL(window.location.href);
      if (value) url.searchParams.set("category", value); else url.searchParams.delete("category");
      history.replaceState(null, "", url);
      if (document.startViewTransition && !reduceMotion) {
        document.startViewTransition(function () { apply(value); });
      } else {
        apply(value);
      }
    });
  }

  /* ---------- Before / after slider ---------- */
  $$("[data-ba]").forEach(function (ba) {
    var range = $("[data-ba-range]", ba);
    var set = function () { ba.style.setProperty("--pos", range.value + "%"); };
    range.addEventListener("input", set);
    set();
  });

  /* ---------- Gallery lightbox ---------- */
  var gallery = $("[data-gallery]");
  var lb = $("[data-lightbox]");
  if (gallery && lb && typeof lb.showModal === "function") {
    var items = $$(".gallery__item", gallery);
    var img = $("[data-lb-img]", lb), cap = $("[data-lb-cap]", lb), idx = 0;
    var show = function (i) {
      idx = (i + items.length) % items.length;
      img.src = items[idx].dataset.full;
      img.alt = items[idx].dataset.caption || "";
      cap.textContent = items[idx].dataset.caption || "";
    };
    items.forEach(function (it, i) { it.addEventListener("click", function () { show(i); lb.showModal(); }); });
    $("[data-lb-prev]", lb).addEventListener("click", function () { show(idx - 1); });
    $("[data-lb-next]", lb).addEventListener("click", function () { show(idx + 1); });
    lb.addEventListener("keydown", function (e) {
      if (e.key === "ArrowLeft") show(idx - 1);
      if (e.key === "ArrowRight") show(idx + 1);
    });
    lb.addEventListener("click", function (e) { if (e.target === lb) lb.close(); });
    if (items.length < 2) $$(".lightbox__nav", lb).forEach(function (b) { b.hidden = true; });
  }

  /* ---------- Multi-step quote form ---------- */
  var form = $("[data-steps]");
  if (form) {
    var stepEls = $$("[data-step]", form);
    var tabs = $$("[data-step-tab]", form);
    var prev = $("[data-step-prev]", form);
    var next = $("[data-step-next]", form);
    var submit = $("[data-step-submit]", form);
    var current = 0;
    form.classList.add("js-steps");

    var go = function (i, back) {
      current = i;
      stepEls.forEach(function (s, n) {
        s.classList.toggle("is-active", n === i);
        s.classList.toggle("from-back", n === i && !!back);
      });
      tabs.forEach(function (t, n) {
        if (n === i) t.setAttribute("aria-current", "step"); else t.removeAttribute("aria-current");
        t.classList.toggle("is-done", n < i);
      });
      prev.hidden = i === 0;
      next.hidden = i === stepEls.length - 1;
      submit.hidden = i !== stepEls.length - 1;
      var top = form.getBoundingClientRect().top + window.scrollY - 100;
      if (window.scrollY > top) window.scrollTo({ top: top, behavior: reduceMotion ? "auto" : "smooth" });
    };

    var validStep = function (i) {
      var ok = true;
      $$("input, select, textarea", stepEls[i]).forEach(function (el) {
        if (el.type === "hidden" || el.name === "website") return;
        var wrap = el.closest(".field");
        var msg = wrap && wrap.querySelector(".js-error");
        var bad = false;
        if (el.type === "radio") {
          if (el.required) bad = !form.querySelector('input[name="' + el.name + '"]:checked');
        } else {
          bad = !el.checkValidity();
        }
        if (wrap) wrap.classList.toggle("field--error", bad);
        if (bad && wrap && !msg) {
          msg = document.createElement("p");
          msg.className = "field__error js-error";
          wrap.appendChild(msg);
        }
        if (msg) msg.textContent = bad ? (el.type === "radio" ? "Choose one option." : (el.validationMessage || "Fill in this field.")) : "";
        if (bad && ok) { ok = false; el.focus({ preventScroll: false }); }
      });
      return ok;
    };

    next.addEventListener("click", function () { if (validStep(current)) go(current + 1); });
    prev.addEventListener("click", function () { go(current - 1, true); });
    tabs.forEach(function (t, n) {
      t.style.cursor = "pointer";
      t.addEventListener("click", function () { if (n < current || validStep(current)) { if (n <= current + 1) go(n, n < current); } });
    });
    form.addEventListener("submit", function (e) {
      for (var i = 0; i < stepEls.length; i++) {
        if (!validStep(i)) { e.preventDefault(); go(i); return; }
      }
      submit.disabled = true;
      submit.textContent = "Sending…";
    });

    // Open on the first step that has a server-side error.
    var start = 0;
    for (var s = 0; s < stepEls.length; s++) {
      if (stepEls[s].querySelector(".field--error")) { start = s; break; }
    }
    go(start);
  }

  /* ---------- File drop zone ---------- */
  $$("[data-dropzone]").forEach(function (dz) {
    var input = $("input[type=file]", dz);
    var text = $("[data-dropzone-text]", dz);
    var original = text.innerHTML;
    var refresh = function () {
      var f = input.files && input.files[0];
      dz.classList.toggle("has-file", !!f);
      if (f) text.textContent = f.name + " (" + (f.size / 1048576).toFixed(1) + " MB). Click to change.";
      else text.innerHTML = original;
    };
    ["dragenter", "dragover"].forEach(function (ev) { dz.addEventListener(ev, function () { dz.classList.add("is-over"); }); });
    ["dragleave", "drop"].forEach(function (ev) { dz.addEventListener(ev, function () { dz.classList.remove("is-over"); }); });
    input.addEventListener("change", refresh);
  });

  /* ---------- Cost estimator ---------- */
  var est = $("[data-estimator]");
  if (est) {
    var ratesEl = document.getElementById("estimator-rates");
    var RATES = ratesEl ? JSON.parse(ratesEl.textContent) : {};
    var eform = $("[data-estimator-form]", est);
    var range = $("[data-area-range]", est);
    var num = $("[data-area-num]", est);
    var hint = $("[data-area-hint]", est);
    var floorsField = $("[data-floors-field]", est);
    var outRange = $("[data-out-range]", est);
    var outArea = $("[data-out-area]", est);
    var outRate = $("[data-out-rate]", est);
    var outLow = $("[data-out-low]", est);
    var outHigh = $("[data-out-high]", est);

    var params = new URLSearchParams(window.location.search);
    if (params.get("service")) {
      var pre = eform.querySelector('input[name="service"][value="' + params.get("service") + '"]');
      if (pre) pre.checked = true;
    }

    var indian = function (n) { return Math.round(n).toLocaleString("en-IN"); };
    var money = function (n) {
      if (n >= 1e7) return "₹" + (n / 1e7).toFixed(2).replace(/\.?0+$/, "") + " crore";
      if (n >= 1e5) return "₹" + (n / 1e5).toFixed(1).replace(/\.0$/, "") + " lakh";
      return "₹" + indian(n);
    };
    var areaHint = function (a, service) {
      if (service === "renovation" || service === "interior") {
        if (a < 800) return "About the size of a 1 bedroom flat.";
        if (a < 1500) return "About a 2 bedroom home.";
        if (a < 2600) return "About a 3 to 4 bedroom home.";
        return "A large home, office floor or commercial space.";
      }
      if (a < 1000) return "A compact single-storey home.";
      if (a < 1800) return "Roughly a 2 to 3 bedroom home.";
      if (a < 3200) return "Roughly a 3 to 4 bedroom home.";
      if (a < 8000) return "A large villa, clinic or small commercial building.";
      return "A hospital, office block or larger commercial building.";
    };

    var last = "";
    var calc = function () {
      var service = (eform.querySelector('input[name="service"]:checked') || {}).value;
      var tier = (eform.querySelector('input[name="tier"]:checked') || {}).value;
      var area = Math.max(0, parseInt(num.value, 10) || 0);
      floorsField.hidden = service !== "construction";
      hint.textContent = areaHint(area, service);
      outArea.textContent = indian(area) + " sq ft";

      var svc = RATES[service] || {};
      $$("[data-tier-note]", est).forEach(function (n) {
        var t = svc[n.dataset.tierNote];
        n.textContent = t ? t.note : "";
      });

      var r = svc[tier];
      if (!r || !area) {
        outRange.textContent = area ? "Rates not set yet" : "Enter an area";
        outRate.textContent = "";
        outLow.value = outHigh.value = "";
        return;
      }
      var low = r.min * area, high = r.max * area;
      var text = money(low) + " to " + money(high);
      if (text !== last) {
        outRange.textContent = text;
        if (!reduceMotion) { outRange.classList.remove("is-updating"); void outRange.offsetWidth; outRange.classList.add("is-updating"); }
        last = text;
      }
      outRate.textContent = "Based on ₹" + indian(r.min) + " to ₹" + indian(r.max) + " per sq ft.";
      outLow.value = Math.round(low);
      outHigh.value = Math.round(high);
    };

    range.addEventListener("input", function () { num.value = range.value; calc(); });
    num.addEventListener("input", function () {
      var v = parseInt(num.value, 10) || 0;
      range.value = Math.min(Math.max(v, +range.min), +range.max);
      calc();
    });
    eform.addEventListener("change", calc);
    calc();
  }

  /* ---------- Quiet reveal for a few below-the-fold blocks ---------- */
  if (!reduceMotion && "IntersectionObserver" in window) {
    var revealables = $$(".work-grid, .svc-block, .principles, .voices__track, .rate-table");
    var rio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("is-visible"); rio.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealables.forEach(function (el) {
      if (el.getBoundingClientRect().top > window.innerHeight) { el.classList.add("reveal"); rio.observe(el); }
    });
  }
})();
