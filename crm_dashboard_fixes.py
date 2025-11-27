# -*- coding: utf-8 -*-
# CRM Dashboard Accuracy Fixes for scholarixv2
# Date: November 27, 2025
# Fixes: Hardcoded stage IDs, incorrect revenue calculations, date field inconsistencies

"""
CRITICAL FIXES TO APPLY TO: /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/crm_dashboard/models/crm_lead.py

This file contains corrected methods to replace the buggy ones in the crm_dashboard module.
"""

# ===========================
# FIX 1: Helper Methods for Stage Lookup
# ===========================
# ADD THESE METHODS at the top of the CRMLead class (after _inherit)

    @api.model
    def _get_won_stage_ids(self):
        """
        Get IDs of Won stages dynamically instead of hardcoded stage_id=4
        Returns list of stage IDs where probability=100 or is_won=True
        """
        won_stages = self.env['crm.stage'].search([
            '|',
            ('is_won', '=', True),
            ('probability', '=', 100)
        ])
        return tuple(won_stages.ids) if won_stages else (0,)
    
    @api.model
    def _get_lost_stage_ids(self):
        """Get IDs of Lost stages where probability=0"""
        lost_stages = self.env['crm.stage'].search([
            ('probability', '=', 0),
            ('fold', '=', True)
        ])
        return tuple(lost_stages.ids) if lost_stages else (0,)


# ===========================
# FIX 2: Corrected get_the_annual_target Method
# ===========================
# REPLACE lines 101-158 with this:

    @api.model
    def get_the_annual_target(self, kwargs):
        """Annual Target: Year To Date Graph - FIXED"""
        session_user_id = self.env.uid
        won_stage_ids = self._get_won_stage_ids()
        
        self._cr.execute('''SELECT res_users.id, res_users.sales, res_users.sale_team_id, 
                                (SELECT crm_team.invoiced_target FROM crm_team 
                                WHERE crm_team.id = res_users.sale_team_id) as invoiced_target 
                                FROM res_users WHERE res_users.sales IS NOT NULL 
                                AND res_users.id=%s AND res_users.sale_team_id IS NOT NULL;''', (session_user_id,))
        data2 = self._cr.dictfetchall()
        sales = [rec['sales'] for rec in data2]
        inv_target = [
            rec['invoiced_target'] if rec['invoiced_target'] is not None else 0
            for rec in data2]
        team_id = data2[-1]['sale_team_id'] if data2 else 0
        target_annual = sum(sales) + sum(inv_target)
        
        if self.env.user.has_group('sales_team.group_sale_manager'):
            self._cr.execute('''SELECT res_users.id,res_users.sales,
            res_users.sale_team_id, (SELECT crm_team.invoiced_target FROM 
            crm_team WHERE crm_team.id = res_users.sale_team_id) FROM res_users 
            WHERE res_users.id = %s AND res_users.sales is not null;''',
                             (session_user_id,))
            data3 = self._cr.dictfetchall()
            sales = [rec['sales'] if rec['sales'] else 0 for rec in data3]
            inv_target = [rec['invoiced_target'] if rec.get('invoiced_target') else 0 for rec in data3]
            ytd_target = sum(sales) + sum(inv_target)
            
            # FIX: Use dynamic stage IDs instead of hardcoded 4
            self._cr.execute('''select sum(expected_revenue) from crm_lead 
            where stage_id IN %s and team_id=%s AND Extract(Year FROM date_closed)=
            Extract(Year FROM DATE(NOW()))''', (won_stage_ids, team_id))
            achieved_won_data = self._cr.dictfetchall()
            achieved_won = [item['sum'] if item['sum'] else 0 for item in achieved_won_data]
        else:
            self._cr.execute(
                '''SELECT res_users.id,res_users.sales FROM res_users WHERE 
                res_users.id = %s AND res_users.sales is not null;''',
                (session_user_id,))
            data4 = self._cr.dictfetchall()
            sales = [rec['sales'] if rec['sales'] else 0 for rec in data4]
            ytd_target = sum(sales)
            
            # FIX: Use dynamic stage IDs
            self._cr.execute('''select sum(expected_revenue) from crm_lead 
            where stage_id IN %s and user_id=%s AND 
            Extract(Year FROM date_closed)=Extract(Year FROM DATE(NOW()))''',
                             (won_stage_ids, session_user_id))
            achieved_won_data = self._cr.dictfetchall()
            achieved_won = [item['sum'] if item['sum'] else 0 for item in achieved_won_data]
        
        won = achieved_won[0] if achieved_won else 0
        value = [target_annual, ytd_target, won]
        name = ["Annual Target", "YtD target", "Won"]
        final = [value, name]
        return final


# ===========================
# FIX 3: Corrected revenue_count_pie Method
# ===========================
# REPLACE lines 218-247 with this:

    @api.model
    def revenue_count_pie(self, kwargs):
        """Total expected revenue and count Pie - FIXED"""
        session_user_id = self.env.uid
        won_stage_ids = self._get_won_stage_ids()
        lost_stage_ids = self._get_lost_stage_ids()

        def fetch_total_revenue(query, params):
            self._cr.execute(query, params)
            total_rev_data = self._cr.dictfetchall()
            total_rev = total_rev_data[0]['revenue'] if total_rev_data and \
                                                        total_rev_data[0]['revenue'] else 0
            return total_rev

        # FIX: Expected revenue should exclude won/lost opportunities
        queries = [
            ("SELECT sum(expected_revenue) as revenue FROM crm_lead WHERE user_id=%s AND type='opportunity' AND active=true AND probability NOT IN (0, 100)", (session_user_id,)),
            ("SELECT sum(expected_revenue) as revenue FROM crm_lead WHERE user_id=%s AND type='opportunity' AND stage_id IN %s", (session_user_id, won_stage_ids)),
            ("SELECT sum(expected_revenue) as revenue FROM crm_lead WHERE user_id=%s AND type='opportunity' AND stage_id IN %s", (session_user_id, lost_stage_ids))
        ]
        
        total_expected_revenue = fetch_total_revenue(queries[0][0], queries[0][1])
        total_won_rev = fetch_total_revenue(queries[1][0], queries[1][1])
        total_lost_rev = fetch_total_revenue(queries[2][0], queries[2][1])
        
        revenue_pie_count = [total_expected_revenue, total_won_rev, total_lost_rev]
        revenue_pie_title = ['Expected (Open)', 'Won', 'Lost']
        revenue_data = [revenue_pie_count, revenue_pie_title]
        return revenue_data


# ===========================
# FIX 4: Corrected get_monthly_goal Method  
# ===========================
# REPLACE lines 275-303 with this:

    @api.model
    def get_monthly_goal(self, kwargs):
        """Monthly Goal Gauge - FIXED"""
        uid = self.env.uid
        today = fields.date.today()
        current_month = today.month
        current_year = today.year
        won_stage_ids = self._get_won_stage_ids()
        
        # Get opportunities expected to close this month (excluding won/lost)
        leads = self.env['crm.lead'].search([
            ('date_deadline', '!=', False),
            ('user_id', '=', uid),
            ('type', '=', 'opportunity'),
            ('active', '=', True),
            ('probability', 'not in', (0, 100))  # FIX: Exclude won/lost
        ])
        
        # Get opportunities actually won this month
        leads_won = self.env['crm.lead'].search([
            ('date_closed', '!=', False),
            ('stage_id', 'in', won_stage_ids),  # FIX: Use dynamic stage lookup
            ('user_id', '=', uid),
            ('type', '=', 'opportunity')
        ])
        
        currency_symbol = self.env.company.currency_id.symbol
        
        # FIX: Use date_closed for achievement (actual closes)
        achievement = sum(won.expected_revenue for won in leads_won.filtered(
            lambda a: a.date_closed.month == current_month and
                      a.date_closed.year == current_year))
        
        # FIX: Use date_deadline for target (expected closes)
        total = sum(rec.expected_revenue for rec in leads.filtered(
            lambda t: t.date_deadline.month == current_month and
                      t.date_deadline.year == current_year))
        
        percent = (achievement / total) if total > 0 else 0  # FIX: Simplified calculation
        goals = [achievement, total, currency_symbol, percent]
        return {'goals': goals}


# ===========================
# FIX 5: Corrected lead_details_user Method (Average Time Bug)
# ===========================
# REPLACE the average time calculation section (around lines 692-710) with:

        # FIX: Correct average conversion time calculation
        avg_seconds = 0
        if crm_lead_value > 0:
            self._cr.execute('''SELECT id, date_conversion, create_date
            FROM crm_lead WHERE date_conversion IS NOT NULL;''')
            data = self._cr.dictfetchall()
            for rec in data:
                date_close = rec['date_conversion']
                date_create = rec['create_date']
                delta = date_close - date_create
                avg_seconds += delta.total_seconds()  # FIX: Use total_seconds() not .seconds
            
            avg_time = round(avg_seconds / crm_lead_value / 86400, 1)  # Convert to days
        else:
            avg_time = 0


# ===========================
# FIX 6: Corrected Ratio Calculation with Better NULL Handling
# ===========================
# REPLACE the ratio calculation section (around lines 660-685) with:

        # FIX: Improved ratio calculation with proper NULL handling
        self._cr.execute('''SELECT active, count(active) FROM crm_lead
        WHERE type='opportunity' AND (
            (active = true AND probability = 100 AND user_id=%s 
             AND Extract(MONTH FROM date_closed) = Extract(MONTH FROM DATE(NOW())) 
             AND Extract(Year FROM date_closed) = Extract(Year FROM DATE(NOW())))
            OR
            (active = false AND probability = 0 AND user_id=%s 
             AND Extract(MONTH FROM date_deadline) = Extract(MONTH FROM DATE(NOW())) 
             AND Extract(Year FROM date_deadline) = Extract(Year FROM DATE(NOW())))
        )
        GROUP BY active
        ''', (session_user_id, session_user_id))
        
        record_opportunity = dict(self._cr.fetchall())
        
        # FIX: More robust NULL handling
        total_opportunity_won = record_opportunity.get(True, 0) or 0
        total_opportunity_lost = record_opportunity.get(False, 0) or 0
        
        if total_opportunity_lost > 0:
            opportunity_ratio_value = round(total_opportunity_won / total_opportunity_lost, 2)
        else:
            opportunity_ratio_value = 0.0 if total_opportunity_won == 0 else float('inf')


# ===========================
# DEPLOYMENT INSTRUCTIONS
# ===========================
"""
To apply these fixes to scholarixv2:

1. Backup current module:
   cd /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/crm_dashboard/models
   cp crm_lead.py crm_lead.py.backup.$(date +%Y%m%d_%H%M%S)

2. Apply fixes manually OR copy corrected methods from this file

3. Update module:
   cd /var/odoo/scholarixv2
   sudo -u odoo venv/bin/python3 src/odoo-bin -c odoo.conf -d scholarixv2 --no-http --stop-after-init -u crm_dashboard

4. Restart Odoo service:
   systemctl restart odoo-scholarixv2

5. Clear browser cache and test dashboard

6. If issues occur, rollback:
   cd /var/odoo/scholarixv2/extra-addons/cybroaddons.git-68f85fe88986a/crm_dashboard/models
   cp crm_lead.py.backup.YYYYMMDD_HHMMSS crm_lead.py
   (repeat steps 3-4)
"""
