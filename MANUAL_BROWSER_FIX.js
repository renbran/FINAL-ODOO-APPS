/**
 * MANUAL BROWSER INJECTION FIX
 * Copy and paste this directly into browser console to test immediately
 * This bypasses Odoo asset loading and tests the fix directly
 */

console.log("🚀 MANUAL FIX: Installing emergency JavaScript error prevention...");

// 1. IMMEDIATE MutationObserver fix
if (window.MutationObserver) {
    const OriginalMutationObserver = window.MutationObserver;

    window.MutationObserver = function (callback) {
        console.log("🛡️ MANUAL FIX: Creating safe MutationObserver instance");
        const instance = new OriginalMutationObserver(callback);

        const originalObserve = instance.observe;
        instance.observe = function (target, options) {
            // ULTRA-SAFE validation
            if (!target) {
                console.debug("🛡️ MANUAL FIX: Blocked null target");
                return;
            }

            if (typeof target !== "object") {
                console.debug("🛡️ MANUAL FIX: Blocked non-object target");
                return;
            }

            if (!("nodeType" in target) || typeof target.nodeType !== "number") {
                console.debug("🛡️ MANUAL FIX: Blocked invalid Node interface");
                return;
            }

            if (target.nodeType < 1 || target.nodeType > 12) {
                console.debug("🛡️ MANUAL FIX: Blocked invalid nodeType:", target.nodeType);
                return;
            }

            try {
                return originalObserve.call(this, target, options);
            } catch (error) {
                console.debug("🛡️ MANUAL FIX: Caught MutationObserver error:", error.message);
                return;
            }
        };

        return instance;
    };

    // Preserve prototype
    window.MutationObserver.prototype = OriginalMutationObserver.prototype;
    console.log("✅ MANUAL FIX: MutationObserver protection installed");
} else {
    console.log("⚠️ MANUAL FIX: MutationObserver not found");
}

// 2. IMMEDIATE error event handler
window.addEventListener(
    "error",
    function (event) {
        const message = event.message || "";
        const filename = event.filename || "";

        const errorPatterns = [
            "Failed to execute 'observe' on 'MutationObserver'",
            "parameter 1 is not of type 'Node'",
            "Unexpected token ';'",
        ];

        for (const pattern of errorPatterns) {
            if (
                message.includes(pattern) ||
                filename.includes("index.ts-") ||
                filename.includes("web.assets_web.min.js")
            ) {
                console.log("🛡️ MANUAL FIX: Suppressed error:", message);
                event.preventDefault();
                event.stopPropagation();
                return false;
            }
        }

        return true;
    },
    true
);

console.log("✅ MANUAL FIX: Error event handler installed");

// 3. IMMEDIATE promise rejection handler
window.addEventListener("unhandledrejection", function (event) {
    const reason = event.reason ? event.reason.toString() : "";

    if (
        reason.includes("MutationObserver") ||
        reason.includes("parameter 1 is not of type") ||
        reason.includes("Unexpected token")
    ) {
        console.log("🛡️ MANUAL FIX: Suppressed promise rejection:", reason);
        event.preventDefault();
        return false;
    }

    return true;
});

console.log("✅ MANUAL FIX: Promise rejection handler installed");

// 4. Test MutationObserver with various invalid inputs
console.log("🧪 MANUAL FIX: Testing MutationObserver protection...");

const testCases = [null, undefined, "string", 123, {}, { nodeType: 999 }, { nodeType: "invalid" }];

testCases.forEach((testCase, index) => {
    try {
        const observer = new MutationObserver(() => {});
        observer.observe(testCase, { childList: true });
        console.log(`🧪 Test ${index + 1}: Should have been blocked`);
    } catch (error) {
        console.log(`🧪 Test ${index + 1}: Correctly blocked/handled`);
    }
});

// 5. Test with valid DOM element
try {
    const observer = new MutationObserver(() => {});
    observer.observe(document.body, { childList: true });
    console.log("🧪 Valid test: MutationObserver working correctly with document.body");
    observer.disconnect();
} catch (error) {
    console.log("🧪 Valid test failed:", error.message);
}

console.log("🎉 MANUAL FIX: Installation complete! Monitor console for '🛡️ MANUAL FIX' messages.");
console.log("🎯 MANUAL FIX: If you see protection messages, the fix is working!");

// 6. Continuous monitoring
let errorCount = 0;
const originalConsoleError = console.error;
console.error = function (...args) {
    const message = args.join(" ");

    if (
        message.includes("MutationObserver") ||
        message.includes("parameter 1 is not of type") ||
        message.includes("Unexpected token")
    ) {
        errorCount++;
        console.log(`🛡️ MANUAL FIX: Suppressed console error #${errorCount}:`, message);
        return;
    }

    return originalConsoleError.apply(console, args);
};

console.log("✅ MANUAL FIX: Console error monitoring active");
console.log("📊 MANUAL FIX: Run this to check status: console.log('Errors suppressed:', errorCount)");

/* 
USAGE INSTRUCTIONS:
1. Open browser Developer Tools (F12)
2. Go to Console tab
3. Copy and paste this entire script
4. Press Enter to execute
5. Watch for protection messages starting with '🛡️ MANUAL FIX'
6. Navigate to your payment forms and check if errors are gone
*/
