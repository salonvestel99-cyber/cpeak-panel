/* C-Peak . Hero Typewriter V1
   Inline script calismazsa devreye girer (CSP/timing fallback).
   Idempotent: ayni h1'e iki kere yazmaz.
*/
(function () {
  "use strict";
  if (window.__cpkTypewriterV1) return;
  window.__cpkTypewriterV1 = true;

  function start() {
    var h1 = document.querySelector(".hero-typewriter");
    if (!h1) return false;
    var hedef = h1.getAttribute("data-metin");
    if (!hedef) return false;

    var span = h1.querySelector(".tw-text");
    if (!span) {
      span = document.createElement("span");
      span.className = "tw-text";
      h1.insertBefore(span, h1.firstChild);
    }

    /* Inline zaten yazmaya basladiysa dokunma */
    if (span.textContent && span.textContent.length > 1) return true;

    span.textContent = "";
    var i = 0;
    var HIZ = 45;

    function step() {
      if (i < hedef.length) {
        span.textContent = hedef.substring(0, i + 1);
        i++;
        setTimeout(step, HIZ);
      }
    }
    step();
    return true;
  }

  /* DOM hazir olunca calistir */
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  /* Emniyet: inline script gec calisirsa 800ms sonra tekrar dene */
  setTimeout(start, 800);
})();
