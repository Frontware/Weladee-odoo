# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api
from odoo import exceptions

import datetime
import time

class weladee_company_holidays(models.Model):
    _name="weladee_attendance.company.holidays"
    _description="Weladee company holidays"
    
    company_holiday_description = fields.Char(string='Description', required=True, track_visibility='always')
    company_holiday_date = fields.Date(string='Date', required=True, default=fields.Date.today, track_visibility='always')
    company_holiday_active = fields.Boolean("Active", default=False, track_visibility='always')
    company_holiday_notes = fields.Text('Notes', track_visibility='always')

    @api.onchange('company_holiday_date')
    def _onchange_company_holiday_date(self):
         holiday = self.search([('company_holiday_date','=',self.company_holiday_date)])
         if holiday:
            raise exceptions.UserError('%s is already a company holiday.' % self.company_holiday_date)