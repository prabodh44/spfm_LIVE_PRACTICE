document.addEventListener("DOMContentLoaded", function () {
  /* ---------- Header scroll state (subtle elevation once scrolled) ---------- */
  var header = document.querySelector(".site-header");
  if (header) {
    var updateHeader = function () {
      if (window.scrollY > 8) header.classList.add("is-scrolled");
      else header.classList.remove("is-scrolled");
    };
    updateHeader();
    window.addEventListener("scroll", updateHeader, { passive: true });
  }

  /* ---------- Scroll-reveal for elements with .reveal ---------- */
  var revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length) {
    revealEls.forEach(function (el, i) {
      el.style.setProperty("--d", Math.min(i % 6, 5) * 70);
    });

    if ("IntersectionObserver" in window) {
      var revealObserver = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              revealObserver.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
      );
      revealEls.forEach(function (el) { revealObserver.observe(el); });

      /* Safety net: if something never intersects (e.g. static render/
         very short page), reveal everything shortly after load anyway. */
      setTimeout(function () {
        revealEls.forEach(function (el) { el.classList.add("is-visible"); });
      }, 1200);
    } else {
      revealEls.forEach(function (el) { el.classList.add("is-visible"); });
    }
  }

  /* ---------- Animated counters (.stat-count[data-target]) ---------- */
  var counters = document.querySelectorAll(".stat-count");
  function animateCounter(el) {
    var target = el.getAttribute("data-target") || "";
    var numeric = parseInt(target.replace(/[^0-9]/g, ""), 10);
    var suffix = target.replace(/[0-9]/g, "");
    if (isNaN(numeric)) { el.textContent = target; return; }
    var start = 0;
    var duration = 1100;
    var startTime = null;
    function step(ts) {
      if (!startTime) startTime = ts;
      var progress = Math.min((ts - startTime) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * numeric) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if (counters.length && "IntersectionObserver" in window) {
    var counterObserver = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            animateCounter(entry.target);
            counterObserver.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.5 }
    );
    counters.forEach(function (el) { counterObserver.observe(el); });
  } else {
    counters.forEach(function (el) { el.textContent = el.getAttribute("data-target"); });
  }

  /* ---------- Job card gentle tilt toward cursor (desktop only) ---------- */
  var heroVisual = document.querySelector(".hero-visual");
  var jobCard = document.querySelector(".job-card");
  if (heroVisual && jobCard && window.matchMedia("(pointer: fine)").matches) {
    heroVisual.addEventListener("mousemove", function (e) {
      var rect = heroVisual.getBoundingClientRect();
      var x = (e.clientX - rect.left) / rect.width - 0.5;
      var y = (e.clientY - rect.top) / rect.height - 0.5;
      jobCard.style.transform =
        "rotate(1.5deg) rotateY(" + (x * 10) + "deg) rotateX(" + (y * -10) + "deg)";
    });
    heroVisual.addEventListener("mouseleave", function () {
      jobCard.style.transform = "rotate(1.5deg)";
    });
  }

  /* ---------- Mobile nav toggle ---------- */
  var navToggle = document.getElementById("navToggle");
  var mainNav = document.getElementById("main-nav");
  if (navToggle && mainNav) {
    navToggle.addEventListener("click", function () {
      var isOpen = mainNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
  }

  /* ---------- Quote modal ---------- */
  var modal = document.getElementById("quoteModal");
  var openers = document.querySelectorAll(".js-open-quote");
  var closers = document.querySelectorAll(".js-close-quote");

  function openModal() {
    if (!modal) return;
    modal.classList.add("is-open");
    modal.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }
  function closeModal() {
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  openers.forEach(function (btn) {
    btn.addEventListener("click", openModal);
  });
  closers.forEach(function (btn) {
    btn.addEventListener("click", closeModal);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeModal();
  });

  /* ---------- Gallery filters + lightbox (Our Work page) ---------- */
  var filterChips = document.querySelectorAll(".filter-chip");
  var tiles = document.querySelectorAll(".gallery-tile");

  filterChips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      filterChips.forEach(function (c) { c.classList.remove("is-active"); });
      chip.classList.add("is-active");
      var filter = chip.getAttribute("data-filter");
      tiles.forEach(function (tile) {
        var show = filter === "all" || tile.getAttribute("data-category") === filter;
        tile.style.display = show ? "" : "none";
      });
    });
  });

  var lightbox = document.getElementById("lightbox");
  if (lightbox) {
    var lightboxImgWrap = lightbox.querySelector(".lightbox-body");
    var lightboxCaption = lightbox.querySelector(".lightbox-caption-text");
    var lightboxClose = lightbox.querySelector(".lightbox-close");

    tiles.forEach(function (tile) {
      tile.addEventListener("click", function () {
        var title = tile.getAttribute("data-title") || "";
        var imgSrc = tile.getAttribute("data-image");
        lightboxImgWrap.innerHTML = imgSrc
          ? '<img src="' + imgSrc + '" alt="' + title + '">'
          : '<span class="placeholder-label">Photo coming soon — ' + title + "</span>";
        lightboxCaption.textContent = title;
        lightbox.classList.add("is-open");
      });
    });

    lightboxClose.addEventListener("click", function () {
      lightbox.classList.remove("is-open");
    });
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) lightbox.classList.remove("is-open");
    });
  }
});
