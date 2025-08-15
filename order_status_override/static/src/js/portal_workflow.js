/** @odoo-module **/

/**
 * Portal Workflow Components
 * Provides frontend portal functionality for order status
 */

document.addEventListener("DOMContentLoaded", function () {
  console.log("Portal workflow module loaded");

  // Safe DOM manipulation - check if elements exist
  const statusElements = document.querySelectorAll(".o_portal_status_badge");
  if (statusElements.length > 0) {
    console.log(`Found ${statusElements.length} status badges`);

    // Add interactive behavior
    statusElements.forEach((element) => {
      element.addEventListener("click", function () {
        const status = this.textContent.trim();
        console.log("Status clicked:", status);
      });
    });
  }

  // Safe mutation observer setup
  const targetNode = document.querySelector("#wrapwrap");
  if (targetNode && typeof MutationObserver !== "undefined") {
    const observer = new MutationObserver(function (mutations) {
      mutations.forEach(function (mutation) {
        if (mutation.type === "childList") {
          // Handle dynamic content updates
          const newStatusElements = mutation.target.querySelectorAll(
            ".o_portal_status_badge:not(.processed)"
          );
          newStatusElements.forEach((element) => {
            element.classList.add("processed");
            console.log("New status element processed");
          });
        }
      });
    });

    // Start observing with error handling
    try {
      observer.observe(targetNode, {
        childList: true,
        subtree: true,
      });
      console.log("Mutation observer initialized successfully");
    } catch (error) {
      console.warn("Mutation observer setup failed:", error);
    }
  } else {
    console.warn("Target node or MutationObserver not available");
  }
});
