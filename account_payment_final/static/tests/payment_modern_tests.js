/** @odoo-module **/

import { registry } from "@web/core/registry";
import { makeTestEnv } from "@web/../tests/helpers/mock_env";
import { makeFakeLocalizationService } from "@web/../tests/helpers/mock_services";
import { 
    PaymentApprovalWidgetModern 
} from "@account_payment_final/js/components/payment_approval_widget_modern";
import { 
    formatCurrency, 
    formatDate, 
    validatePaymentData,
    generateQRData,
    parseQRData,
    getStatusConfig
} from "@account_payment_final/js/utils/payment_utils";

const { Component, mount } = owl;
const { QUnit } = window;

QUnit.module("Account Payment Final - Modern Components", function (hooks) {
    let env;
    let target;

    hooks.beforeEach(async function () {
        target = document.createElement("div");
        document.body.appendChild(target);
        
        env = await makeTestEnv({
            services: {
                localization: makeFakeLocalizationService(),
            },
        });
    });

    hooks.afterEach(function () {
        if (target) {
            target.remove();
        }
    });

    QUnit.module("Payment Approval Widget Modern");

    QUnit.test("component renders correctly", async function (assert) {
        const mockRecord = {
            data: {
                id: 1,
                name: "BILL/2024/001",
                approval_state: "draft",
            },
            resId: 1,
        };

        const props = {
            record: mockRecord,
            readonly: false,
            update: () => {},
        };

        const component = await mount(PaymentApprovalWidgetModern, target, {
            env,
            props,
        });

        assert.ok(component, "Component should be mounted");
        assert.containsOnce(target, ".o_payment_approval_widget_modern", 
            "Should contain the widget container");
        
        component.destroy();
    });

    QUnit.test("readonly mode disables actions", async function (assert) {
        const mockRecord = {
            data: { id: 1, approval_state: "draft" },
            resId: 1,
        };

        const props = {
            record: mockRecord,
            readonly: true,
            update: () => {},
        };

        const component = await mount(PaymentApprovalWidgetModern, target, {
            env,
            props,
        });

        assert.notOk(component.state.showActions, 
            "Actions should be disabled in readonly mode");
        
        component.destroy();
    });
});

QUnit.module("Account Payment Final - Utility Functions", function () {

    QUnit.module("Currency Formatting");

    QUnit.test("formatCurrency handles various inputs", function (assert) {
        assert.equal(formatCurrency(1234.56, "USD"), "$1,234.56", 
            "Should format USD correctly");
        
        assert.equal(formatCurrency(1234.56, "EUR"), "€1,234.56", 
            "Should format EUR correctly");
        
        assert.equal(formatCurrency(null), "", 
            "Should handle null values");
        
        assert.equal(formatCurrency(undefined), "", 
            "Should handle undefined values");
    });

    QUnit.module("Date Formatting");

    QUnit.test("formatDate handles various formats", function (assert) {
        const testDate = new Date("2024-01-15");
        
        assert.ok(formatDate(testDate), "Should format date object");
        assert.ok(formatDate("2024-01-15"), "Should format date string");
        assert.equal(formatDate(""), "", "Should handle empty string");
        assert.equal(formatDate(null), "", "Should handle null");
    });

    QUnit.module("Payment Data Validation");

    QUnit.test("validatePaymentData checks required fields", function (assert) {
        const validPayment = {
            partner_id: [1, "Partner Name"],
            amount: 100.00,
            payment_method_id: [1, "Method"],
            journal_id: [1, "Journal"],
        };

        const result = validatePaymentData(validPayment);
        assert.ok(result.isValid, "Valid payment should pass validation");
        assert.equal(result.errors.length, 0, "Should have no errors");

        const invalidPayment = {
            partner_id: null,
            amount: 0,
            payment_method_id: null,
            journal_id: null,
        };

        const invalidResult = validatePaymentData(invalidPayment);
        assert.notOk(invalidResult.isValid, "Invalid payment should fail validation");
        assert.ok(invalidResult.errors.length > 0, "Should have errors");
    });

    QUnit.module("QR Code Utilities");

    QUnit.test("generateQRData and parseQRData work together", function (assert) {
        const mockPayment = {
            id: 123,
            name: "BILL/2024/001",
            amount: 100.00,
            partner_id: [1, "Test Partner"],
            date: "2024-01-15",
            verification_code: "ABC123",
        };

        const qrData = generateQRData(mockPayment);
        assert.ok(qrData, "Should generate QR data");

        const parsedData = parseQRData(qrData);
        assert.ok(parsedData, "Should parse QR data");
        assert.equal(parsedData.id, mockPayment.id, "Should preserve payment ID");
        assert.equal(parsedData.name, mockPayment.name, "Should preserve payment name");
    });

    QUnit.test("parseQRData handles invalid input", function (assert) {
        assert.equal(parseQRData("invalid"), null, "Should handle invalid input");
        assert.equal(parseQRData(""), null, "Should handle empty string");
        assert.equal(parseQRData(null), null, "Should handle null");
    });

    QUnit.module("Status Configuration");

    QUnit.test("getStatusConfig returns correct configuration", function (assert) {
        const draftConfig = getStatusConfig("draft");
        assert.equal(draftConfig.label, "Draft", "Should return correct draft label");
        assert.equal(draftConfig.color, "secondary", "Should return correct draft color");

        const approvedConfig = getStatusConfig("approved");
        assert.equal(approvedConfig.label, "Approved", "Should return correct approved label");
        assert.equal(approvedConfig.color, "success", "Should return correct approved color");

        const unknownConfig = getStatusConfig("unknown");
        assert.equal(unknownConfig.label, "Draft", "Should fallback to draft for unknown status");
    });
});

QUnit.module("Account Payment Final - Error Prevention", function () {

    QUnit.test("CloudPepper error prevention is loaded", function (assert) {
        assert.ok(window.CloudPepperErrorPrevention, 
            "Error prevention system should be available globally");
        
        assert.ok(window.CloudPepperErrorPrevention.manager, 
            "Error prevention manager should be available");
        
        assert.ok(typeof window.CloudPepperErrorPrevention.addPattern === "function", 
            "addPattern function should be available");
    });

    QUnit.test("DOM utilities work correctly", function (assert) {
        const testDiv = document.createElement("div");
        testDiv.id = "test-element";
        testDiv.className = "test-class";
        document.body.appendChild(testDiv);

        const { DOMUtils } = window.CloudPepperErrorPrevention;
        
        const found = DOMUtils.querySelector("#test-element");
        assert.ok(found, "Should find element by ID");

        const foundAll = DOMUtils.querySelectorAll(".test-class");
        assert.ok(foundAll.length > 0, "Should find elements by class");

        const listenerAdded = DOMUtils.addEventListener(testDiv, "click", () => {});
        assert.ok(listenerAdded, "Should successfully add event listener");

        document.body.removeChild(testDiv);
    });
});

QUnit.module("Account Payment Final - Integration Tests", function () {

    QUnit.test("services integration", function (assert) {
        const services = registry.category("services");
        
        // Check if payment workflow service is registered
        const paymentWorkflowService = services.get("paymentWorkflow", null);
        assert.ok(paymentWorkflowService, "Payment workflow service should be registered");
    });

    QUnit.test("component registration", function (assert) {
        const fields = registry.category("fields");
        
        // Check if modern widget is registered
        const modernWidget = fields.get("payment_approval_widget_modern", null);
        assert.ok(modernWidget, "Modern payment approval widget should be registered");
    });
});

// Performance Tests
QUnit.module("Account Payment Final - Performance", function () {

    QUnit.test("utility functions performance", function (assert) {
        const start = performance.now();
        
        // Test multiple currency formats
        for (let i = 0; i < 1000; i++) {
            formatCurrency(Math.random() * 10000, "USD");
        }
        
        const currencyTime = performance.now() - start;
        assert.ok(currencyTime < 100, `Currency formatting should be fast (${currencyTime}ms)`);

        const dateStart = performance.now();
        
        // Test date formatting
        for (let i = 0; i < 1000; i++) {
            formatDate(new Date());
        }
        
        const dateTime = performance.now() - dateStart;
        assert.ok(dateTime < 100, `Date formatting should be fast (${dateTime}ms)`);
    });

    QUnit.test("QR code generation performance", function (assert) {
        const mockPayment = {
            id: 123,
            name: "BILL/2024/001",
            amount: 100.00,
            partner_id: [1, "Test Partner"],
            date: "2024-01-15",
            verification_code: "ABC123",
        };

        const start = performance.now();
        
        for (let i = 0; i < 1000; i++) {
            const qrData = generateQRData(mockPayment);
            parseQRData(qrData);
        }
        
        const qrTime = performance.now() - start;
        assert.ok(qrTime < 50, `QR operations should be fast (${qrTime}ms)`);
    });
});
