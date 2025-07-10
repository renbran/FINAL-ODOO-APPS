# -*- coding: utf-8 -*-
################################################################################
#
#    Kolpolok Ltd. (https://www.kolpolok.com)
#    Author: Kaushik Ahmed Apu, Aqil Mahmud, Zarin Tasnim(<https://www.kolpolok.com>)
#
################################################################################
from odoo import fields, models


class PropertyDashboard(models.Model):
    _name = 'property.dashboard'
    _description = 'Property Dashboard'
    
    def get_details(self):
        total_property = self.env['property.property'].search_count([])
        sold_property = self.env['property.property'].search_count([('status', '=', 'sold')])
        print("==============>", total_property)
        return {
            'total_property': total_property,
        }