/** @odoo-module **/

/**
 * Emergency Odoo.define Global Fix
 * Include this script FIRST if you encounter "odoo.define is not a function" errors
 *
 * This creates a global compatibility layer for legacy Odoo modules
 */

console.log("🚑 Emergency Odoo.define Global Fix Loading...");

// Ensure window.odoo exists
if (typeof window !== "undefined") {
  window.odoo = window.odoo || {};

  // Create a robust odoo.define compatibility shim
  if (typeof window.odoo.define !== "function") {
    window.odoo.define = function (name, dependencies, callback) {
      console.warn(`🚨 Emergency Fix: Legacy odoo.define() call for "${name}"`);

      // Handle different call signatures
      if (typeof dependencies === "function") {
        // odoo.define(name, function() {})
        callback = dependencies;
        dependencies = [];
      }

      // Create a safe execution context
      const requireShim = function (moduleName) {
        console.warn(
          `🚨 Emergency Fix: require('${moduleName}') called - returning empty object`
        );
        return {};
      };

      // Execute callback safely with error handling
      try {
        if (typeof callback === "function") {
          const result = callback(requireShim);
          console.log(
            `✅ Emergency Fix: Successfully executed legacy module "${name}"`
          );
          return result;
        }
      } catch (error) {
        console.error(
          `❌ Emergency Fix: Error in legacy module "${name}":`,
          error
        );
        // Don't throw - just log and continue
      }

      return {};
    };

    console.log("✅ Emergency odoo.define() shim activated");
  }

  // Also create a basic loader shim if needed
  window.odoo.loader = window.odoo.loader || {
    bus: {
      addEventListener: function (event, callback) {
        console.log(
          `🚨 Emergency Fix: loader.bus.addEventListener('${event}') shimmed`
        );
      },
    },
  };
}

// Global error handler specifically for odoo.define errors
window.addEventListener("error", function (event) {
  if (
    event.message &&
    event.message.includes("odoo.define is not a function")
  ) {
    console.error("🚨 Emergency Fix: Caught odoo.define error:", event.message);
    event.preventDefault();
    return true;
  }
});

console.log("🚑 Emergency Odoo.define Global Fix Ready!");
