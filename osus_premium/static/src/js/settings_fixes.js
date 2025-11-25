/** @odoo-module **/

// Settings page cleanup - remove rogue toggle buttons
// This runs immediately when the module loads

const removeRogueButtons = () => {
  const settingsForm = document.querySelector(".o_form_view.o_xxl_form_view");
  if (settingsForm) {
    // Find all buttons that might be problematic
    const buttons = settingsForm.querySelectorAll("button");
    buttons.forEach((button) => {
      const text = button.textContent.trim();
      const hasNoName = !button.getAttribute("name");
      const hasNoClass =
        !button.className ||
        button.className === "btn" ||
        button.className === "btn-secondary";

      // Remove if it's an empty button or says "Toggle Dropdown"
      if (
        (text === "" || text === "Toggle Dropdown") &&
        hasNoName &&
        hasNoClass
      ) {
        console.log("[OSUS] Removing rogue button:", button);
        button.style.display = "none";
        button.remove();
      }
    });
  }
};

// Run when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", () => {
    removeRogueButtons();
    setTimeout(removeRogueButtons, 500);
    setTimeout(removeRogueButtons, 1000);
  });
} else {
  // DOM already loaded
  removeRogueButtons();
  setTimeout(removeRogueButtons, 500);
  setTimeout(removeRogueButtons, 1000);
}

// Run on any DOM mutations
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.addedNodes.length) {
      removeRogueButtons();
    }
  });
});

// Start observing when ready
const startObserving = () => {
  const settingsContainer = document.querySelector(".o_content");
  if (settingsContainer) {
    observer.observe(settingsContainer, {
      childList: true,
      subtree: true,
    });
    console.log("[OSUS] Settings page observer started");
  } else {
    setTimeout(startObserving, 500);
  }
};

startObserving();

console.log("[OSUS] Settings fixes loaded - removing rogue toggle buttons");
