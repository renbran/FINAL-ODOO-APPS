/** @odoo-module **/

/**
 * Portal Workflow Components - Simplified Safe Version
 * Provides basic frontend portal functionality without MutationObserver
 */

// Simple, safe initialization without DOM dependencies
(function () {
  "use strict";

  console.log("OSUS Portal Workflow: Module loaded");

  // Basic functionality that doesn't depend on specific DOM elements
  function initPortalFeatures() {
    // Only run if we're in a portal context
    if (typeof odoo === "undefined") {
      console.log("OSUS Portal: Not in Odoo context, skipping initialization");
      return;
    }

    console.log("OSUS Portal: Basic features initialized");
  }

  // Safe initialization
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPortalFeatures);
  } else {
    initPortalFeatures();
  }
})();
