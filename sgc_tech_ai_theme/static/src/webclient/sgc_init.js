/** @odoo-module **/

/**
 * SGC Tech AI Theme - Initialization Script
 *
 * This script runs early to set default sidebar visibility state.
 * It ensures the Enterprise-style sidebar is visible by default on first load.
 */

(function () {
  "use strict";

  // Set default sidebar visibility if not set
  if (localStorage.getItem("sgc_sidebar_visible") === null) {
    localStorage.setItem("sgc_sidebar_visible", "true");
  }

  // Apply initial body class based on stored preference
  const sidebarVisible =
    localStorage.getItem("sgc_sidebar_visible") !== "false";

  if (sidebarVisible) {
    document.body.classList.add("sgc_sidebar_type_large");
    document.body.classList.remove("sgc_sidebar_type_invisible");
  } else {
    document.body.classList.add("sgc_sidebar_type_invisible");
    document.body.classList.remove("sgc_sidebar_type_large");
  }

  console.log(
    "[SGC Init] Sidebar initialized:",
    sidebarVisible ? "Visible" : "Hidden"
  );
})();
