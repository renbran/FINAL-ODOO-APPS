/**
 (function() {
    'use strict';

    // CloudPepper compatibility check
    if (typeof $ === 'undefined') {
        console.log('PaymentWorkflowRealtime: jQuery not available, skipping initialization');
        return;
    }

    // Global Payment Workflow Real-time Handler (CloudPepper Safe Version)
    window.PaymentWorkflowRealtime = {
        
        // Version and compatibility info
        version: '1.1.0',
        cloudPepperSafe: true,
        lastUserActivity: 0,ment Workflow Real-time Updates
 * CloudPepper Compatible - NON-MODULE VERSION
 * Provides real-time status updates and UI enhancements for payment approval workflow
 */

(function () {
    "use strict";

    // Global Payment Workflow Real-time Handler
    window.PaymentWorkflowRealtime = {
        
        /**
         * Initialize real-time workflow monitoring (CloudPepper Safe)
         */
        init: function() {
            this.setupWorkflowObservers();
            this.setupFieldWatchers();
            this.enhanceButtons();
            this.setupAutoRefresh();
            this.setupUserActivityTracking();
            this.lastUserActivity = Date.now();
        },

        /**
         * Setup user activity tracking for safe refreshes
         */
        setupUserActivityTracking: function() {
            var self = this;
            
            // Track various user interactions
            $(document).on('click change keypress', function() {
                self.trackUserActivity();
            });
            
            // Track form interactions specifically
            $(document).on('change', 'input, select, textarea', function() {
                self.trackUserActivity();
            });
        },

        /**
         * Setup observers for workflow state changes (CloudPepper Safe)
         */
        setupWorkflowObservers: function() {
            try {
                // Watch for approval_state field changes
                $(document).on('change', 'select[name="approval_state"]', function() {
                    try {
                        PaymentWorkflowRealtime.onApprovalStateChange($(this));
                    } catch (error) {
                        console.log('Approval state change error:', error);
                    }
                });

                // Watch for reviewer/approver/authorizer changes
                $(document).on('change', 'select[name="reviewer_id"], select[name="approver_id"], select[name="authorizer_id"]', function() {
                    try {
                        PaymentWorkflowRealtime.onWorkflowUserChange($(this));
                    } catch (error) {
                        console.log('Workflow user change error:', error);
                    }
                });

                // Watch for state synchronization
                $(document).on('change', 'select[name="state"]', function() {
                    try {
                        PaymentWorkflowRealtime.onStateChange($(this));
                    } catch (error) {
                        console.log('State change error:', error);
                    }
                });
            } catch (error) {
                console.log('Setup workflow observers error:', error);
            }
        },

        /**
         * Setup field watchers for real-time validation (CloudPepper Safe)
         */
        setupFieldWatchers: function() {
            try {
                // Amount validation
                $(document).on('change', 'input[name="amount"]', function() {
                    try {
                        PaymentWorkflowRealtime.validateAmount($(this));
                    } catch (error) {
                        console.log('Amount validation error:', error);
                    }
                });

                // Partner validation
                $(document).on('change', 'select[name="partner_id"]', function() {
                    try {
                        PaymentWorkflowRealtime.onPartnerChange($(this));
                    } catch (error) {
                        console.log('Partner change error:', error);
                    }
                });
            } catch (error) {
                console.log('Setup field watchers error:', error);
            }
        },

        /**
         * Handle approval state changes
         */
        onApprovalStateChange: function($field) {
            var newState = $field.val();
            var currentTime = new Date().toISOString();
            
            // Update workflow progress indicator
            this.updateWorkflowProgress(newState);
            
            // Show appropriate notifications
            this.showStateChangeNotification(newState);
            
            // Update button visibility
            this.updateButtonVisibility(newState);
            
            // Sync with standard state field if needed
            this.syncStandardState(newState);
        },

        /**
         * Handle workflow user assignments
         */
        onWorkflowUserChange: function($field) {
            var fieldName = $field.attr('name');
            var userId = $field.val();
            var currentTime = new Date().toISOString();
            
            // Auto-populate corresponding date fields
            if (fieldName === 'reviewer_id' && userId) {
                $('input[name="reviewer_date"]').val(currentTime);
            } else if (fieldName === 'approver_id' && userId) {
                $('input[name="approver_date"]').val(currentTime);
            } else if (fieldName === 'authorizer_id' && userId) {
                $('input[name="authorizer_date"]').val(currentTime);
            }
            
            // Update workflow progress
            this.updateWorkflowProgress();
        },

        /**
         * Handle standard state changes
         */
        onStateChange: function($field) {
            var newState = $field.val();
            var $approvalField = $('select[name="approval_state"]');
            
            // Sync approval state with standard state
            if (newState === 'posted' && $approvalField.val() !== 'posted') {
                $approvalField.val('posted').trigger('change');
            } else if (newState === 'cancel' && $approvalField.val() !== 'cancelled') {
                $approvalField.val('cancelled').trigger('change');
            }
        },

        /**
         * Validate payment amount in real-time
         */
        validateAmount: function($field) {
            var amount = parseFloat($field.val()) || 0;
            var $warning = $('.amount-warning');
            
            // Remove existing warnings
            $warning.remove();
            
            if (amount <= 0) {
                this.showFieldWarning($field, 'Amount must be greater than zero');
            } else if (amount > 10000) {
                this.showFieldWarning($field, 'High amount payment - enhanced approval required', 'warning');
            }
        },

        /**
         * Handle partner changes
         */
        onPartnerChange: function($field) {
            var partnerId = $field.val();
            if (partnerId) {
                // Auto-populate partner bank if available
                this.autoPopulatePartnerBank(partnerId);
                
                // Set destination account for vendor payments
                this.setDestinationAccount(partnerId);
            }
        },

        /**
         * Update workflow progress indicator
         */
        updateWorkflowProgress: function(currentState) {
            var $progress = $('.workflow-progress');
            if ($progress.length === 0) return;
            
            currentState = currentState || $('select[name="approval_state"]').val();
            
            var stages = ['draft', 'under_review', 'for_approval', 'for_authorization', 'approved', 'posted'];
            var currentIndex = stages.indexOf(currentState);
            
            $progress.find('.progress-step').each(function(index) {
                var $step = $(this);
                if (index <= currentIndex) {
                    $step.removeClass('step-pending step-current').addClass('step-completed');
                } else if (index === currentIndex + 1) {
                    $step.removeClass('step-pending step-completed').addClass('step-current');
                } else {
                    $step.removeClass('step-completed step-current').addClass('step-pending');
                }
            });
        },

        /**
         * Show state change notifications
         */
        showStateChangeNotification: function(newState) {
            var messages = {
                'under_review': 'Payment submitted for review',
                'for_approval': 'Payment ready for approval',
                'for_authorization': 'Payment ready for authorization',
                'approved': 'Payment approved - ready to post',
                'posted': 'Payment posted successfully',
                'cancelled': 'Payment cancelled'
            };
            
            var message = messages[newState];
            if (message) {
                this.showNotification(message, 'success');
            }
        },

        /**
         * Update button visibility based on current state
         */
        updateButtonVisibility: function(currentState) {
            var $buttons = $('.workflow-buttons button');
            
            // Hide all workflow buttons first
            $buttons.hide();
            
            // Show appropriate buttons based on current state
            switch(currentState) {
                case 'draft':
                    $('button[name="action_submit_for_review"]').show();
                    break;
                case 'under_review':
                    $('button[name="action_review_payment"]').show();
                    $('button[name="action_reject_payment"]').show();
                    break;
                case 'for_approval':
                    $('button[name="action_approve_payment"]').show();
                    $('button[name="action_reject_payment"]').show();
                    break;
                case 'for_authorization':
                    $('button[name="action_authorize_payment"]').show();
                    $('button[name="action_reject_payment"]').show();
                    break;
                case 'approved':
                    $('button[name="action_post_payment"]').show();
                    break;
                case 'posted':
                    // No workflow buttons needed
                    break;
            }
        },

        /**
         * Sync standard Odoo state with approval state
         */
        syncStandardState: function(approvalState) {
            var $stateField = $('select[name="state"]');
            if ($stateField.length === 0) return;
            
            if (approvalState === 'posted' && $stateField.val() !== 'posted') {
                $stateField.val('posted');
            } else if (approvalState === 'cancelled' && $stateField.val() !== 'cancel') {
                $stateField.val('cancel');
            }
        },

        /**
         * Enhanced button functionality
         */
        enhanceButtons: function() {
            // Add click handlers for workflow buttons
            $(document).on('click', '.workflow-buttons button', function(e) {
                var $button = $(this);
                var action = $button.attr('name');
                
                // Show loading state
                $button.prop('disabled', true).append(' <i class="fa fa-spinner fa-spin"></i>');
                
                // Re-enable button after 3 seconds (fallback)
                setTimeout(function() {
                    $button.prop('disabled', false).find('.fa-spinner').remove();
                }, 3000);
            });
        },

        /**
         * Setup auto-refresh for real-time updates (CloudPepper Safe)
         */
        setupAutoRefresh: function() {
            // Use safer page-based refresh instead of RPC calls
            setInterval(function() {
                PaymentWorkflowRealtime.refreshWorkflowStatusSafe();
            }, 60000); // Increased to 60 seconds for stability
        },

        /**
         * Safe refresh method that doesn't use RPC calls
         */
        refreshWorkflowStatusSafe: function() {
            // Only refresh if we're on a payment form and user hasn't interacted recently
            if (!$('select[name="approval_state"]').length) return;
            
            var lastActivity = PaymentWorkflowRealtime.lastUserActivity || 0;
            var now = Date.now();
            
            // Don't refresh if user was active in last 30 seconds
            if (now - lastActivity < 30000) return;
            
            try {
                // Safe notification about potential updates
                var currentState = $('select[name="approval_state"]').val();
                if (currentState && currentState !== 'posted') {
                    PaymentWorkflowRealtime.showNotification(
                        'Workflow may have updates. Refresh page to see latest status.', 
                        'info', 
                        5000
                    );
                }
            } catch (error) {
                console.log('Safe refresh notification skipped:', error);
            }
        },

        /**
         * Deprecated: Direct RPC refresh - removed for CloudPepper compatibility
         */
        refreshWorkflowStatus: function() {
            // This method is deprecated and replaced with refreshWorkflowStatusSafe
            console.log('Direct RPC refresh disabled for CloudPepper compatibility');
            this.refreshWorkflowStatusSafe();
        },

        /**
         * Deprecated: Update fields from server response - removed for CloudPepper compatibility
         */
        updateFieldsFromServer: function(data) {
            // This method is deprecated to prevent RPC errors
            console.log('Direct field updates from server disabled for CloudPepper compatibility');
        },

        /**
         * Track user activity to prevent unnecessary refreshes
         */
        trackUserActivity: function() {
            this.lastUserActivity = Date.now();
        },

        /**
         * Get current record ID
         */
        getCurrentRecordId: function() {
            // Try to get record ID from URL or form
            var urlMatch = window.location.href.match(/id=(\d+)/);
            if (urlMatch) {
                return parseInt(urlMatch[1]);
            }
            
            // Try to get from form data
            var $form = $('.o_form_view');
            if ($form.length && $form.data('record-id')) {
                return $form.data('record-id');
            }
            
            return null;
        },

        /**
         * Show field-specific warnings
         */
        showFieldWarning: function($field, message, type) {
            type = type || 'error';
            var $warning = $('<div class="alert alert-' + (type === 'error' ? 'danger' : 'warning') + ' amount-warning">' + message + '</div>');
            $field.closest('.o_field_widget').after($warning);
            
            // Auto-remove warning after 5 seconds
            setTimeout(function() {
                $warning.fadeOut();
            }, 5000);
        },

        /**
         * Show notification messages (CloudPepper Safe)
         */
        showNotification: function(message, type, duration) {
            try {
                type = type || 'info';
                duration = duration || 4000;
                
                // Remove any existing notifications first
                $('.payment-notification').remove();
                
                // Create notification element with error handling
                var $notification = $(
                    '<div class="alert alert-' + type + ' payment-notification" style="position: fixed; top: 20px; right: 20px; z-index: 9999; max-width: 400px;">' +
                    '<button type="button" class="close" data-dismiss="alert" aria-label="Close">&times;</button>' +
                    '<span>' + message + '</span>' +
                    '</div>'
                );
                
                // Safely append to body
                if ($('body').length) {
                    $('body').append($notification);
                } else {
                    return; // Can't show notification if no body
                }
                
                // Setup close button
                $notification.find('.close').on('click', function() {
                    $notification.fadeOut(300, function() {
                        $(this).remove();
                    });
                });
                
                // Auto-remove after specified duration
                setTimeout(function() {
                    if ($notification.length) {
                        $notification.fadeOut(300, function() {
                            $(this).remove();
                        });
                    }
                }, duration);
                
            } catch (error) {
                // Fallback to console if notification fails
                console.log('Notification:', type, '-', message);
            }
        },

        /**
         * Auto-populate partner bank details
         */
        autoPopulatePartnerBank: function(partnerId) {
            // This would typically make an AJAX call to get partner bank details
            // For now, just trigger a recalculation
            $('select[name="partner_bank_id"]').trigger('change');
        },

        /**
         * Set destination account for payments
         */
        setDestinationAccount: function(partnerId) {
            // This would typically make an AJAX call to get the correct account
            // For now, just trigger a recalculation
            $('select[name="destination_account_id"]').trigger('change');
        }
    };

    // Initialize when document is ready (CloudPepper Safe)
    $(document).ready(function() {
        try {
            PaymentWorkflowRealtime.init();
        } catch (error) {
            console.log('PaymentWorkflowRealtime initialization error:', error);
        }
    });

    // Re-initialize when form is reloaded (with error handling)
    $(document).on('DOMNodeInserted', function(e) {
        try {
            if ($(e.target).find('select[name="approval_state"]').length > 0) {
                setTimeout(function() {
                    try {
                        PaymentWorkflowRealtime.init();
                    } catch (error) {
                        console.log('PaymentWorkflowRealtime re-initialization error:', error);
                    }
                }, 100);
            }
        } catch (error) {
            console.log('DOM insertion handler error:', error);
        }
    });

})();
