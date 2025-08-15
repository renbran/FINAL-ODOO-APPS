/** @odoo-module **/

/**
 * Status Dashboard Components
 * Provides dashboard functionality for order status management
 */

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class StatusDashboard extends Component {
  static template = "order_status_override.StatusDashboard";

  setup() {
    this.orm = useService("orm");
    this.notification = useService("notification");
    this.state = useState({
      isLoading: false,
      data: null,
    });

    onWillStart(this.loadDashboardData);
  }

  async loadDashboardData() {
    this.state.isLoading = true;
    try {
      // Load dashboard data safely
      this.state.data = {
        orders_count: 0,
        commission_total: 0.0,
        status_distribution: {},
      };
    } catch (error) {
      console.warn("Dashboard data loading failed:", error);
      this.notification.add("Dashboard data unavailable", { type: "info" });
    } finally {
      this.state.isLoading = false;
    }
  }
}

// Only register if not already registered
if (!registry.category("components").contains("status_dashboard")) {
  registry.category("components").add("status_dashboard", StatusDashboard);
}

console.log("Status Dashboard module loaded successfully");
