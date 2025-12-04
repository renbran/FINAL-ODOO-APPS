/** @odoo-module **/

/**
 * SGC Tech AI Theme - Enterprise-Style Navbar Toggle
 *
 * Patches the Odoo NavBar component to add sidebar toggle functionality.
 * This enables users to show/hide the Enterprise-style sidebar menu.
 */

import { patch } from "@web/core/utils/patch";
import { NavBar } from "@web/webclient/navbar/navbar";

patch(NavBar.prototype, {
  setup() {
    super.setup(...arguments);

    // Initialize sidebar visibility from localStorage
    this.sidebarVisible =
      localStorage.getItem("sgc_sidebar_visible") !== "false";

    // Apply initial body class
    this.updateSidebarClass();
  },

  /**
   * Toggle sidebar visibility and persist state
   */
  toggleSidebar() {
    this.sidebarVisible = !this.sidebarVisible;
    localStorage.setItem("sgc_sidebar_visible", this.sidebarVisible);
    this.updateSidebarClass();

    console.log(
      "[SGC NavBar] Sidebar toggled:",
      this.sidebarVisible ? "Visible" : "Hidden"
    );
  },

  /**
   * Update body classes based on sidebar visibility
   */
  updateSidebarClass() {
    const body = document.body;

    if (this.sidebarVisible) {
      body.classList.remove("sgc_sidebar_type_invisible");
      body.classList.add("sgc_sidebar_type_large");
    } else {
      body.classList.remove("sgc_sidebar_type_large");
      body.classList.add("sgc_sidebar_type_invisible");
    }
  },
});
