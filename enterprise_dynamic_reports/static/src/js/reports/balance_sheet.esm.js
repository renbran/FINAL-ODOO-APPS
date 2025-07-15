/** @odoo-module **/

import { Component, onWillStart, useState, useRef, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

const actionRegistry = registry.category("actions");

export class EnterpriseBalanceSheetReport extends Component {
    static template = "enterprise_dynamic_reports.BalanceSheetTemplate";

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.dialog = useService("dialog");

        this.state = useState({
            isLoading: true,
            reportData: null,
            reportOptions: {
                date_from: null,
                date_to: null,
                comparison_mode: 'none',
                show_hierarchy: true,
                show_zero_balance: false,
                drill_down_level: 'account_type',
            },
            filters: {
                companies: [],
                journals: [],
                date_filters: {},
            },
            expandedSections: new Set(['assets', 'liabilities', 'equity']),
            selectedAccounts: new Set(),
            showFilters: false,
            error: null,
            exporting: false,
        });

        this.reportRef = useRef("balanceSheetReport");
        this.filterPanelRef = useRef("filterPanel");

        onWillStart(async () => {
            await this.loadFilters();
            await this.generateReport();
        });

        onMounted(() => {
            this.setupEventListeners();
        });
    }

    async loadFilters() {
        try {
            const filters = await this.orm.call(
                "enterprise.balance.sheet.report",
                "get_report_filters",
                []
            );
            this.state.filters = filters;
        } catch (error) {
            console.error("Error loading filters:", error);
        }
    }

    async generateReport() {
        try {
            this.state.isLoading = true;
            this.state.error = null;

            // Create a new report record with current options
            const reportId = await this.orm.call(
                "enterprise.balance.sheet.report",
                "create",
                [this.state.reportOptions]
            );

            // Generate the report
            const result = await this.orm.call(
                "enterprise.balance.sheet.report",
                "action_generate_report",
                [reportId]
            );

            if (result.context && result.context.report_data) {
                this.state.reportData = result.context.report_data;
                this.state.reportOptions = result.context.report_options || this.state.reportOptions;
                
                // Initialize expanded sections
                this.initializeExpandedSections();
            } else {
                throw new Error("Invalid report data received");
            }

        } catch (error) {
            console.error("Error generating report:", error);
            this.state.error = _t("Failed to generate balance sheet report. Please check your parameters and try again.");
            this.notification.add(_t("Error generating report"), {
                type: "danger",
            });
        } finally {
            this.state.isLoading = false;
        }
    }

    initializeExpandedSections() {
        // Auto-expand sections with data
        if (this.state.reportData) {
            const sections = ['assets', 'liabilities', 'equity'];
            sections.forEach(section => {
                if (this.state.reportData.current_period[section]) {
                    this.state.expandedSections.add(section);
                }
            });
        }
    }

    setupEventListeners() {
        // Add keyboard shortcuts
        document.addEventListener('keydown', this.handleKeyDown.bind(this));
    }

    handleKeyDown(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (event.key) {
                case 'r':
                    event.preventDefault();
                    this.onRefreshReport();
                    break;
                case 'e':
                    event.preventDefault();
                    this.onExportPDF();
                    break;
                case 'f':
                    event.preventDefault();
                    this.onToggleFilters();
                    break;
            }
        }
    }

    // Event handlers
    async onDateFilterChange(filterKey) {
        const dateFilter = this.state.filters.date_filters[filterKey];
        if (dateFilter) {
            this.state.reportOptions.date_from = dateFilter.from;
            this.state.reportOptions.date_to = dateFilter.to;
            await this.generateReport();
        }
    }

    async onCustomDateChange() {
        await this.generateReport();
    }

    async onComparisonModeChange(mode) {
        this.state.reportOptions.comparison_mode = mode;
        await this.generateReport();
    }

    onToggleSection(sectionKey) {
        if (this.state.expandedSections.has(sectionKey)) {
            this.state.expandedSections.delete(sectionKey);
        } else {
            this.state.expandedSections.add(sectionKey);
        }
    }

    onToggleAccount(accountId) {
        if (this.state.selectedAccounts.has(accountId)) {
            this.state.selectedAccounts.delete(accountId);
        } else {
            this.state.selectedAccounts.add(accountId);
        }
    }

    onToggleFilters() {
        this.state.showFilters = !this.state.showFilters;
    }

    async onRefreshReport() {
        await this.generateReport();
        this.notification.add(_t("Report refreshed"), {
            type: "success",
        });
    }

    async onDrillDown(accountId, accountCode) {
        try {
            // Open detailed account view
            const action = await this.orm.call(
                "enterprise.balance.sheet.report",
                "action_drill_down_account",
                [accountId, this.state.reportOptions]
            );

            if (action) {
                this.env.services.action.doAction(action);
            }
        } catch (error) {
            console.error("Error drilling down:", error);
            this.notification.add(_t("Error opening account details"), {
                type: "danger",
            });
        }
    }

    // Export functions
    async onExportPDF() {
        await this.exportReport('pdf');
    }

    async onExportExcel() {
        await this.exportReport('xlsx');
    }

    async exportReport(format) {
        try {
            this.state.exporting = true;

            const exportData = {
                report_data: this.state.reportData,
                report_options: this.state.reportOptions,
                format: format,
            };

            const result = await this.orm.call(
                "enterprise.balance.sheet.report",
                `action_export_${format}`,
                [exportData]
            );

            if (result.url) {
                // Download the file
                const link = document.createElement('a');
                link.href = result.url;
                link.download = `balance_sheet_${new Date().toISOString().split('T')[0]}.${format}`;
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }

            this.notification.add(_t(`Balance Sheet exported to ${format.toUpperCase()}`), {
                type: "success",
            });

        } catch (error) {
            console.error(`Error exporting to ${format}:`, error);
            this.notification.add(_t(`Error exporting to ${format.toUpperCase()}`), {
                type: "danger",
            });
        } finally {
            this.state.exporting = false;
        }
    }

    // Helper methods
    isSectionExpanded(sectionKey) {
        return this.state.expandedSections.has(sectionKey);
    }

    isAccountSelected(accountId) {
        return this.state.selectedAccounts.has(accountId);
    }

    formatCurrency(amount) {
        if (!amount && amount !== 0) return '-';
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
        }).format(amount);
    }

    formatPercentage(value) {
        if (!value && value !== 0) return '-';
        return `${value.toFixed(1)}%`;
    }

    getVarianceClass(current, comparison) {
        if (!comparison) return '';
        return current > comparison ? 'positive' : 'negative';
    }

    getSectionIcon(sectionKey) {
        const icons = {
            assets: 'fa-coins',
            liabilities: 'fa-credit-card',
            equity: 'fa-chart-pie',
        };
        return icons[sectionKey] || 'fa-folder';
    }

    getRatioInterpretation(ratioKey, value) {
        const interpretations = {
            current_ratio: {
                good: value >= 1.5,
                warning: value >= 1.0 && value < 1.5,
                poor: value < 1.0,
                description: value >= 1.5 ? 'Excellent liquidity' : 
                           value >= 1.0 ? 'Good liquidity' : 'Poor liquidity'
            },
            debt_to_equity: {
                good: value <= 0.5,
                warning: value > 0.5 && value <= 1.0,
                poor: value > 1.0,
                description: value <= 0.5 ? 'Conservative leverage' :
                           value <= 1.0 ? 'Moderate leverage' : 'High leverage'
            },
            debt_to_assets: {
                good: value <= 0.3,
                warning: value > 0.3 && value <= 0.6,
                poor: value > 0.6,
                description: value <= 0.3 ? 'Low debt burden' :
                           value <= 0.6 ? 'Moderate debt burden' : 'High debt burden'
            },
            equity_ratio: {
                good: value >= 0.5,
                warning: value >= 0.3 && value < 0.5,
                poor: value < 0.3,
                description: value >= 0.5 ? 'Strong equity position' :
                           value >= 0.3 ? 'Adequate equity' : 'Weak equity position'
            }
        };

        return interpretations[ratioKey] || { description: 'No interpretation available' };
    }

    getRatioClass(ratioKey, value) {
        const interpretation = this.getRatioInterpretation(ratioKey, value);
        if (interpretation.good) return 'o_enterprise_ratio_good';
        if (interpretation.warning) return 'o_enterprise_ratio_warning';
        if (interpretation.poor) return 'o_enterprise_ratio_poor';
        return '';
    }

    // Print functionality
    onPrint() {
        window.print();
    }

    // Cleanup
    willUnmount() {
        document.removeEventListener('keydown', this.handleKeyDown.bind(this));
    }
}

// Register the component
actionRegistry.add("enterprise_balance_sheet_report", EnterpriseBalanceSheetReport);
