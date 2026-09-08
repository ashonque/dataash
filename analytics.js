/* dataash.de - measurement, and the consent it depends on. One file, loaded
 * by every page, because copying this into three pages is how three pages
 * come to disagree about what they count and what they ask.
 *
 * ---------------------------------------------------------------------------
 * CONSENT
 *
 * Analytics on a German domain sets cookies on somebody's machine, and under
 * the GDPR and the TTDSG that needs asking first. Google's mechanism for it
 * is Consent Mode, and the one rule that makes it work is ordering: the
 * default must be pushed into the dataLayer *before* gtag is configured. Set
 * afterwards, the tag has already read the old state and the default has no
 * effect - which looks identical to a working implementation from the outside.
 *
 * So the first thing this file does is deny, and the banner grants.
 *
 * Denied does not mean nothing. Under Consent Mode, Google still receives
 * cookieless pings and models the gap, so the numbers stay directionally
 * useful; what stops is the cookie and anything that could follow one person
 * between visits.
 *
 * `security_storage` is granted by default because it is not tracking - it is
 * what fraud prevention and load balancing use, and it has no marketing
 * dimension to consent to.
 *
 * The banner offers Accept and Decline as the same size, the same weight and
 * the same distance from the cursor. A decline that is harder to click than
 * an accept is not consent, and regulators have said so repeatedly. There is
 * no pre-ticked anything and no third "manage" step designed to be tiring.
 * ---------------------------------------------------------------------------
 */
(function () {
  "use strict";

  var ID = "G-5P4PHQCGXX";
  var KEY = "dataash.consent";     /* "granted" or "declined", or absent */

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;

  function stored() {
    try { return window.localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function remember(value) {
    try { window.localStorage.setItem(KEY, value); } catch (e) { /* private window */ }
  }

  /* ------------------------------------------------- 1. deny, before anything */
  gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied",
    functionality_storage: "denied",
    personalization_storage: "denied",
    security_storage: "granted",
    /* a moment for a returning visitor's stored answer to be applied before
       the first hit leaves, so their choice is not ignored once per visit */
    wait_for_update: 500
  });

  /* ------------------------------------------------- 2. a choice already made */
  var answered = stored();
  if (answered === "granted") {
    gtag("consent", "update", {
      analytics_storage: "granted",
      functionality_storage: "granted",
      personalization_storage: "granted"
    });
  }

  /* ------------------------------------------------- 3. now measure */
  gtag("js", new Date());
  gtag("config", ID);

  var tag = document.createElement("script");
  tag.async = true;
  tag.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
  document.head.appendChild(tag);

  /* ------------------------------------------------- events
   * open_access_modal and early_access_submit are the two ends of one
   * funnel. A submission count says how many people finished; the gap
   * between opening the form and sending it is what says whether the form
   * is the problem.
   */
  function say(name, params) {
    try { gtag("event", name, params || {}); } catch (e) { /* never break a page */ }
  }

  function trim(text, max) {
    var s = String(text || "").replace(/\s+/g, " ").trim();
    return s.length > (max || 100) ? s.slice(0, max || 100) : s;
  }

  function wire() {
    var openers = document.querySelectorAll("[data-open-modal]");
    for (var i = 0; i < openers.length; i++) {
      openers[i].addEventListener("click", function (ev) {
        say("open_access_modal", { link_text: trim(ev.currentTarget.textContent, 40) });
      });
    }
    /* which questions people open, in their own words: a number nobody can
       read back to a question is no use */
    var asked = document.querySelectorAll(".faq-q, .faq-item h3");
    for (var j = 0; j < asked.length; j++) {
      asked[j].addEventListener("click", function (ev) {
        say("faq_open", { question: trim(ev.currentTarget.textContent, 90) });
      });
    }
  }

  /* ------------------------------------------------- the banner */
  function styles() {
    if (document.getElementById("dashConsentStyles")) return;
    var s = document.createElement("style");
    s.id = "dashConsentStyles";
    s.textContent = [
      ".dash-consent{position:fixed;left:0;right:0;bottom:0;z-index:9999;",
      "  background:#FFFFFF;border-top:1px solid #E3DCCE;",
      "  box-shadow:0 -8px 30px rgba(12,27,54,.10);",
      "  font-family:Inter,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;",
      "  animation:dashUp .28s cubic-bezier(.16,1,.3,1)}",
      "@keyframes dashUp{from{transform:translateY(100%)}to{transform:translateY(0)}}",
      "@media (prefers-reduced-motion:reduce){.dash-consent{animation:none}}",
      ".dash-consent-in{max-width:1080px;margin:0 auto;padding:18px 24px;",
      "  display:flex;gap:22px;align-items:center;flex-wrap:wrap}",
      ".dash-consent-say{flex:1 1 380px;min-width:0;font-size:14px;line-height:1.6;",
      "  color:#5A6A86;margin:0}",
      ".dash-consent-say b{color:#0C1B36;font-weight:600}",
      ".dash-consent-btns{display:flex;gap:10px;flex:0 0 auto}",
      /* the same size, the same weight, the same distance: a decline that is
         harder to click than an accept is not a choice */
      ".dash-consent button{font-family:inherit;font-size:14px;font-weight:600;",
      "  padding:11px 22px;border-radius:9px;cursor:pointer;border:1px solid #1E3A6B;",
      "  min-width:132px}",
      ".dash-yes{background:#1E3A6B;color:#fff}",
      ".dash-yes:hover{background:#3E68AE;border-color:#3E68AE}",
      ".dash-no{background:#fff;color:#1E3A6B}",
      ".dash-no:hover{background:#EDF2FA}",
      ".dash-consent button:focus-visible{outline:3px solid #3E68AE;outline-offset:2px}",
      "@media (max-width:620px){.dash-consent-btns{width:100%}",
      "  .dash-consent button{flex:1 1 0;min-width:0}}"
    ].join("");
    document.head.appendChild(s);
  }

  function decide(answer) {
    remember(answer);
    if (answer === "granted") {
      gtag("consent", "update", {
        analytics_storage: "granted",
        functionality_storage: "granted",
        personalization_storage: "granted"
      });
      /* the first page view left under the denied default, so record the
         page again now that it can be attributed to a visit */
      say("page_view");
    }
    var bar = document.getElementById("dashConsent");
    if (bar && bar.parentNode) bar.parentNode.removeChild(bar);
  }

  function banner() {
    if (stored()) return;              /* already answered, on this browser */
    styles();
    var bar = document.createElement("div");
    bar.id = "dashConsent";
    bar.className = "dash-consent";
    bar.setAttribute("role", "region");
    bar.setAttribute("aria-label", "Cookies and measurement");
    bar.innerHTML =
      '<div class="dash-consent-in">' +
        '<p class="dash-consent-say"><b>May we count this visit?</b> ' +
        "We use Google Analytics to see which pages are read and where people " +
        "give up. It sets a cookie in your browser. Decline and nothing is " +
        "stored on your machine — the site works exactly the same either way." +
        "</p>" +
        '<div class="dash-consent-btns">' +
          '<button type="button" class="dash-no" id="dashNo">Decline</button>' +
          '<button type="button" class="dash-yes" id="dashYes">Accept</button>' +
        "</div>" +
      "</div>";
    document.body.appendChild(bar);
    document.getElementById("dashYes").addEventListener("click", function () {
      decide("granted");
    });
    document.getElementById("dashNo").addEventListener("click", function () {
      decide("declined");
    });
  }

  function start() {
    wire();
    banner();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  /* so a person can change their mind from the console, or from a link on a
     privacy page when one exists */
  window.DataAshConsent = {
    state: function () { return stored() || "not answered"; },
    grant: function () { decide("granted"); },
    withdraw: function () {
      remember("declined");
      gtag("consent", "update", {
        analytics_storage: "denied",
        functionality_storage: "denied",
        personalization_storage: "denied"
      });
    },
    ask: function () {
      try { window.localStorage.removeItem(KEY); } catch (e) { /* ignore */ }
      banner();
    }
  };
})();
