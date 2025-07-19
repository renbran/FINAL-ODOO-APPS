odoo.define('custom_sales.Dashboard', function (require) {
    'use strict';

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var QWeb = core.qweb;
    var _t = core._t;
    var framework = require('web.framework');

    var CustomSalesDashboard = AbstractAction.extend({
        template: 'custom_sales.Dashboard',
        events: {
            'click .custom_sales_refresh_dashboard': '_onRefreshDashboard',
            'change .custom_sales_date_filter': '_onDateFilterChange',
            'click .export-dashboard': '_onExportDashboard',
            'click .toggle-auto-refresh': '_onToggleAutoRefresh',
            'click .kpi-card': '_onKPIClick',
            'click .chart-fullscreen': '_onChartFullscreen',
        },

        /**
         * @override
         */
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.dashboardId = action.context.dashboard_id || false;
            this.chartInstances = {};
            this.dashboardData = {};
            this.dateFrom = action.context.date_from || null;
            this.dateTo = action.context.date_to || null;
            this.autoRefreshInterval = null;
            this.isLoading = false;
        },

        /**
         * @override
         */
        willStart: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                return self._loadAssets().then(function () {
                    return self._fetchDashboardConfig();
                }).then(function () {
                    if (self.dashboardConfig) {
                        return self._fetchDashboardData();
                    }
                });
            });
        },

        /**
         * @override
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._setupTheme();
                if (!self.dashboardConfig) {
                    self._renderNoDashboard();
                } else {
                    self._renderDashboard();
                    self._setupAutoRefresh();
                }
                return Promise.resolve();
            });
        },

        /**
         * @override
         */
        destroy: function () {
            this._clearAutoRefresh();
            this._destroyCharts();
            this._super.apply(this, arguments);
        },

        /**
         * Load required assets (Chart.js, etc.)
         * @private
         */
        _loadAssets: function () {
            // Chart.js should be loaded via assets bundle
            return Promise.resolve();
        },

        /**
         * Fetch dashboard configuration
         * @private
         */
        _fetchDashboardConfig: function () {
            var self = this;
            return rpc.query({
                route: '/custom_sales/api/dashboard_data',
                params: {
                    dashboard_id: this.dashboardId,
                    date_from: this.dateFrom,
                    date_to: this.dateTo,
                },
            }).then(function (result) {
                if (result.error) {
                    self._showError(result.error);
                    return Promise.reject(result.error);
                }
                self.dashboardData = result.data;
                self.dashboardConfig = result.config;
                return Promise.resolve();
            }).catch(function (error) {
                self._showError(error.message || error);
                return Promise.reject(error);
            });
        },

        /**
         * Fetch dashboard data from the server
         * @private
         */
        _fetchDashboardData: function () {
            var self = this;
            if (this.isLoading) return Promise.resolve();
            
            this.isLoading = true;
            this._showLoading();

            return Promise.all([
                this._fetchKPIData(),
                this._fetchChartData(),
                this._fetchSummaryData()
            ]).then(function () {
                self.isLoading = false;
                self._hideLoading();
                return Promise.resolve();
            }).catch(function (error) {
                self.isLoading = false;
                self._hideLoading();
                self._showError(error.message || error);
                return Promise.reject(error);
            });
        },

        /**
         * Fetch KPI data from the server
         * @private
         */
        _fetchKPIData: function () {
            var self = this;
            return rpc.query({
                route: '/custom_sales/api/kpis',
                params: {
                    dashboard_id: this.dashboardId,
                    date_from: this.dateFrom,
                    date_to: this.dateTo,
                },
            }).then(function (result) {
                if (result.error) {
                    return Promise.reject(new Error(result.error));
                }
                self.dashboardData.kpis = result.kpis;
                return Promise.resolve();
            });
        },

        /**
         * Fetch chart data from the server
         * @private
         */
        _fetchChartData: function () {
            var self = this;
            return rpc.query({
                route: '/custom_sales/api/charts',
                params: {
                    dashboard_id: this.dashboardId,
                    date_from: this.dateFrom,
                    date_to: this.dateTo,
                },
            }).then(function (result) {
                if (result.error) {
                    return Promise.reject(new Error(result.error));
                }
                self.dashboardData.charts = result.charts;
                return Promise.resolve();
            });
        },

        /**
         * Fetch summary data
         * @private
         */
        _fetchSummaryData: function () {
            var self = this;
            return rpc.query({
                route: '/custom_sales/api/sales_overview',
                params: {
                    date_from: this.dateFrom,
                    date_to: this.dateTo,
                },
            }).then(function (result) {
                if (result.error) {
                    return Promise.reject(new Error(result.error));
                }
                self.dashboardData.summary = result.data;
                return Promise.resolve();
            });
        },

        /**
         * Setup branded theme
         * @private
         */
        _setupTheme: function () {
            this.$el.addClass('custom-sales-dashboard');
            if (this.dashboardConfig) {
                this.$el.css({
                    '--osus-burgundy': this.dashboardConfig.primary_color || '#8B0000',
                    '--osus-gold': this.dashboardConfig.secondary_color || '#FFD700',
                    '--osus-light-gold': this.dashboardConfig.accent_color || '#F5DEB3',
                });
            }
        },

        /**
         * Render the complete dashboard
         * @private
         */
        _renderDashboard: function () {
            var self = this;
            var $content = QWeb.render('custom_sales.DashboardMain', {
                widget: this,
                dashboard_config: this.dashboardConfig,
                dashboard_data: this.dashboardData,
                date_from: this.dateFrom,
                date_to: this.dateTo,
            });
            
            this.$el.html($content);
            
            // Render components with animation
            setTimeout(function () {
                self._renderKPIs();
                self._renderCharts();
                self._renderTables();
                self._setupDatePickers();
            }, 100);
        },

        /**
         * Render KPI widgets
         * @private
         */
        _renderKPIs: function () {
            var $kpiContainer = this.$('.kpi-container');
            if ($kpiContainer.length && this.dashboardData.kpis) {
                var $kpis = QWeb.render('custom_sales.KPIWidgets', {
                    kpis: this.dashboardData.kpis,
                });
                $kpiContainer.html($kpis);
                
                // Animate KPI cards
                this.$('.kpi-card').each(function (index) {
                    $(this).delay(index * 100).addClass('fade-in');
                });
            }
        },

        /**
         * Render dashboard charts
         * @private
         */
        _renderCharts: function () {
            var self = this;
            if (!this.dashboardData.charts) return;

            this.dashboardData.charts.forEach(function (chartConfig, index) {
                var chartId = 'chart_' + chartConfig.id;
                var $chartContainer = self.$('#' + chartId);
                
                if ($chartContainer.length) {
                    var canvas = $chartContainer.find('canvas')[0];
                    if (canvas) {
                        // Destroy existing chart
                        if (self.chartInstances[chartId]) {
                            self.chartInstances[chartId].destroy();
                        }
                        
                        // Create new chart with theme colors
                        var ctx = canvas.getContext('2d');
                        var options = self._getChartOptions(chartConfig);
                        
                        self.chartInstances[chartId] = new Chart(ctx, {
                            type: chartConfig.type,
                            data: self._applyThemeToChartData(chartConfig.data),
                            options: options,
                        });
                        
                        // Animate chart container
                        $chartContainer.delay(index * 200).addClass('slide-in-left');
                    }
                }
            });
        },

        /**
         * Render data tables
         * @private
         */
        _renderTables: function () {
            var $tablesContainer = this.$('.data-tables-container');
            if ($tablesContainer.length && this.dashboardData.summary) {
                var $tables = QWeb.render('custom_sales.DataTables', {
                    summary: this.dashboardData.summary,
                });
                $tablesContainer.html($tables);
                $tablesContainer.addClass('slide-in-right');
            }
        },

        /**
         * Setup date picker controls
         * @private
         */
        _setupDatePickers: function () {
            var self = this;
            this.$('.date-picker').each(function () {
                $(this).on('change', function () {
                    self._onDateFilterChange.call(self, { currentTarget: this });
                });
            });
        },

        /**
         * Setup auto-refresh functionality
         * @private
         */
        _setupAutoRefresh: function () {
            if (this.dashboardConfig && this.dashboardConfig.auto_refresh && 
                this.dashboardConfig.refresh_interval > 0) {
                this._startAutoRefresh(this.dashboardConfig.refresh_interval * 1000);
            }
        },

        /**
         * Start auto-refresh timer
         * @private
         */
        _startAutoRefresh: function (interval) {
            var self = this;
            this._clearAutoRefresh();
            this.autoRefreshInterval = setInterval(function () {
                self._refreshData();
            }, interval);
        },

        /**
         * Clear auto-refresh timer
         * @private
         */
        _clearAutoRefresh: function () {
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
                this.autoRefreshInterval = null;
            }
        },

        /**
         * Refresh dashboard data
         * @private
         */
        _refreshData: function () {
            var self = this;
            return this._fetchDashboardData().then(function () {
                self._renderKPIs();
                self._renderCharts();
                self._renderTables();
                self._showSuccessMessage(_t('Dashboard refreshed successfully'));
            });
        },

        /**
         * Apply theme colors to chart data
         * @private
         */
        _applyThemeToChartData: function (chartData) {
            var themeColors = [
                '#8B0000', '#FFD700', '#F5DEB3', '#DAA520', '#B8860B',
                '#CD853F', '#D2691E', '#A0522D', '#8B4513'
            ];
            
            if (chartData.datasets) {
                chartData.datasets.forEach(function (dataset, index) {
                    if (!dataset.backgroundColor) {
                        dataset.backgroundColor = themeColors[index % themeColors.length];
                    }
                    if (!dataset.borderColor) {
                        dataset.borderColor = themeColors[index % themeColors.length];
                    }
                });
            }
            
            return chartData;
        },

        /**
         * Get chart options with theme
         * @private
         */
        _getChartOptions: function (chartConfig) {
            var options = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: chartConfig.show_legend !== false,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            font: {
                                family: 'Roboto, sans-serif',
                                size: 12,
                            }
                        }
                    },
                    title: {
                        display: true,
                        text: chartConfig.name,
                        font: {
                            family: 'Roboto, sans-serif',
                            size: 16,
                            weight: 'bold',
                        },
                        color: '#8B0000',
                    }
                },
                scales: {}
            };

            // Add scales for appropriate chart types
            if (['bar', 'line'].includes(chartConfig.type)) {
                options.scales.y = {
                    beginAtZero: true,
                    grid: {
                        color: '#F5DEB3',
                    },
                    ticks: {
                        font: {
                            family: 'Roboto, sans-serif',
                        }
                    }
                };
                options.scales.x = {
                    grid: {
                        display: false,
                    },
                    ticks: {
                        font: {
                            family: 'Roboto, sans-serif',
                        }
                    }
                };
            }

            return options;
        },

        /**
         * Destroy all chart instances
         * @private
         */
        _destroyCharts: function () {
            Object.values(this.chartInstances).forEach(function (chart) {
                if (chart && typeof chart.destroy === 'function') {
                    chart.destroy();
                }
            });
            this.chartInstances = {};
        },

        /**
         * Render no dashboard state
         * @private
         */
        _renderNoDashboard: function () {
            this.$el.html(QWeb.render('custom_sales.NoDashboard'));
        },

        /**
         * Show loading overlay
         * @private
         */
        _showLoading: function () {
            if (!this.$('.loading-overlay').length) {
                this.$el.append('<div class="loading-overlay"><div class="loading-spinner"></div></div>');
            }
        },

        /**
         * Hide loading overlay
         * @private
         */
        _hideLoading: function () {
            this.$('.loading-overlay').remove();
        },

        /**
         * Show error message
         * @private
         */
        _showError: function (message) {
            this.displayNotification({
                title: _t('Dashboard Error'),
                message: message,
                type: 'danger',
            });
        },

        /**
         * Show success message
         * @private
         */
        _showSuccessMessage: function (message) {
            this.displayNotification({
                title: _t('Success'),
                message: message,
                type: 'success',
            });
        },

        // Event Handlers

        /**
         * Handle dashboard refresh button click
         * @private
         */
        _onRefreshDashboard: function (ev) {
            ev.preventDefault();
            this._refreshData();
        },

        /**
         * Handle date filter change
         * @private
         */
        _onDateFilterChange: function (ev) {
            var $input = $(ev.currentTarget);
            var filterType = $input.data('filter');
            var newValue = $input.val();

            if (filterType === 'date_from') {
                this.dateFrom = newValue;
            } else if (filterType === 'date_to') {
                this.dateTo = newValue;
            }

            this._refreshData();
        },

        /**
         * Handle export dashboard button click
         * @private
         */
        _onExportDashboard: function (ev) {
            ev.preventDefault();
            var format = $(ev.currentTarget).data('format') || 'pdf';
            
            var url = '/custom_sales/report/export';
            var params = new URLSearchParams({
                format: format,
                date_from: this.dateFrom || '',
                date_to: this.dateTo || '',
            });
            
            window.open(url + '?' + params.toString(), '_blank');
        },

        /**
         * Handle auto-refresh toggle
         * @private
         */
        _onToggleAutoRefresh: function (ev) {
            ev.preventDefault();
            var $btn = $(ev.currentTarget);
            
            if (this.autoRefreshInterval) {
                this._clearAutoRefresh();
                $btn.removeClass('active').text(_t('Enable Auto Refresh'));
            } else {
                this._startAutoRefresh((this.dashboardConfig.refresh_interval || 300) * 1000);
                $btn.addClass('active').text(_t('Disable Auto Refresh'));
            }
        },

        /**
         * Handle KPI card click
         * @private
         */
        _onKPIClick: function (ev) {
            var $card = $(ev.currentTarget);
            var kpiCode = $card.data('kpi-code');
            
            if (kpiCode) {
                // You could open a detailed view or drill-down here
                console.log('KPI clicked:', kpiCode);
            }
        },

        /**
         * Handle chart fullscreen toggle
         * @private
         */
        _onChartFullscreen: function (ev) {
            ev.preventDefault();
            var $chart = $(ev.currentTarget).closest('.chart-card');
            $chart.toggleClass('fullscreen');
            
            // Redraw chart after fullscreen toggle
            var chartId = $chart.find('canvas').attr('id');
            if (this.chartInstances[chartId]) {
                setTimeout(() => {
                    this.chartInstances[chartId].resize();
                }, 300);
            }
        },
    });

    core.action_registry.add('custom_sales.dashboard', CustomSalesDashboard);

    return CustomSalesDashboard;
});