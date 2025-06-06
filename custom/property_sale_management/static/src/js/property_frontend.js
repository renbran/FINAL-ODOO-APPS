odoo.define('property_sale_management.frontend', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    publicWidget.registry.PropertyDashboard = publicWidget.Widget.extend({
        selector: '.property_dashboard',
        
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                if (self.$el.find('#propertySalesChart').length) {
                    self._initChart();
                }
                
                // Initialize property search functionality
                self.$el.find('.property-search-form').on('submit', function (ev) {
                    ev.preventDefault();
                    self._onSearchProperty();
                });
            });
        },
        
        _initChart: function () {
            // This is a placeholder - in a real implementation, you would use a charting library
            // like Chart.js or load data via AJAX and render it
            console.log('Chart would be initialized here');
            
            // Example of loading data
            ajax.jsonRpc('/property/api/properties', 'call', {})
                .then(function (data) {
                    console.log('Property data loaded:', data);
                    // Process the data and render the chart
                })
                .catch(function (error) {
                    console.error('Error loading property data:', error);
                });
        },
        
        _onSearchProperty: function () {
            var $form = this.$el.find('.property-search-form');
            var searchData = {
                name: $form.find('[name="name"]').val(),
                city: $form.find('[name="city"]').val(),
                status: $form.find('[name="status"]').val(),
                min_price: $form.find('[name="min_price"]').val(),
                max_price: $form.find('[name="max_price"]').val(),
            };
            
            ajax.jsonRpc('/property/api/search', 'call', searchData)
                .then(function (result) {
                    // Update the UI with search results
                    var $results = $('.property-search-results');
                    $results.empty();
                    
                    if (result.count === 0) {
                        $results.append('<div class="alert alert-info">No properties found matching your criteria.</div>');
                        return;
                    }
                    
                    // Render the results
                    $.each(result.properties, function (i, property) {
                        var $card = $('<div class="col-md-4 mb-4">')
                            .append($('<div class="card">')
                                .append($('<div class="card-body">')
                                    .append($('<h5 class="card-title">').text(property.name))
                                    .append($('<p class="card-text">').text(property.street + ', ' + property.city))
                                    .append($('<p class="card-text">').html('<strong>Price: </strong>$' + property.sale_price.toFixed(2)))
                                    .append($('<p class="card-text">').html('<strong>Status: </strong>' + property.status))
                                    .append($('<a class="btn btn-primary">').attr('href', '/property/property/' + property.id).text('View Details'))
                                )
                            );
                        $results.append($card);
                    });
                })
                .catch(function (error) {
                    console.error('Error searching properties:', error);
                });
        }
    });
    
    return {
        PropertyDashboard: publicWidget.registry.PropertyDashboard
    };
});