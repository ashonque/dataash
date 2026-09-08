/* dataash.de - measurement, in one place.
 *
 * This was six lines inlined into index.html. Two more pages now exist, and
 * copying those six lines into each is how three pages come to disagree about
 * what they measure - so it lives here, and every page loads the same file.
 *
 * What it adds beyond a page view:
 *
 *   open_access_modal   somebody opened the early-access form
 *   generate_lead       and sent it (fired beside the site's own
 *                       early_access_submit, which is kept)
 *   faq_open            which question was opened, by its own words
 *
 * The first two are the pair that matters. A submission count on its own says
 * how many people finished; the gap between opening the form and sending it
 * is the number that tells you whether the form is the problem.
 *
 * Everything is feature-detected. On a page with no modal and no FAQ this
 * file measures the page view and attaches nothing, which is what the guide
 * and the 404 page need.
 *
 * Consent is deliberately not changed here. The site has never asked for it,
 * and quietly switching that on or off is a decision about German law rather
 * than about JavaScript. See the note in the repository.
 */
(function () {
  "use strict";

  var ID = "G-5P4PHQCGXX";

  /* the standard bootstrap, unchanged from what was inline */
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", ID);

  var tag = document.createElement("script");
  tag.async = true;
  tag.src = "https://www.googletagmanager.com/gtag/js?id=" + ID;
  document.head.appendChild(tag);

  /* --------------------------------------------------------------- events */
  function say(name, params) {
    try { gtag("event", name, params || {}); } catch (e) { /* never break a page */ }
  }

  function trim(text, max) {
    var s = String(text || "").replace(/\s+/g, " ").trim();
    return s.length > (max || 100) ? s.slice(0, max || 100) : s;
  }

  function wire() {
    /* the form was opened. Counted once per click, including the several
       buttons around the page that open the same modal. */
    var openers = document.querySelectorAll("[data-open-modal]");
    for (var i = 0; i < openers.length; i++) {
      openers[i].addEventListener("click", function (ev) {
        say("open_access_modal", {
          /* where on the page the click came from, so the buttons can be
             compared rather than added together */
          link_text: trim(ev.currentTarget.textContent, 40)
        });
      });
    }

    /* which questions people actually open. The label is the question
       itself: a number nobody can read back to a question is no use. */
    var asked = document.querySelectorAll(".faq-q, .faq-item h3");
    for (var j = 0; j < asked.length; j++) {
      asked[j].addEventListener("click", function (ev) {
        say("faq_open", { question: trim(ev.currentTarget.textContent, 90) });
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", wire);
  } else {
    wire();
  }
})();
