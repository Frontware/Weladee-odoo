##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-Now Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api
from odoo import exceptions

import datetime
import time

class hr_holidays(models.TransientModel):
    _name="weladee_attendance.company.holidays"
    _description="Weladee company holidays"
    
    company_holiday_description = fields.Char(string='Description', required=True)
    company_holiday_date = fields.Date(string='Date', required=True, default=fields.Date.today)
    company_holiday_active = fields.Boolean("Active", default=False)
    company_holiday_notes = fields.Text('Notes')

    @api.onchange('company_holiday_date')
    def _onchange_company_holiday_date(self):
         holiday = self.search([('company_holiday_date','=',self.company_holiday_date)])
         if holiday:
            raise exceptions.UserError('This Date already company holiday.')

    @api.model
    def create(self, vals):
        print(vals["company_holiday_date"])
        holiday_line_obj = self.env['weladee_attendance.company.holidays']
        holiday_line_ids = holiday_line_obj.search( [ ('company_holiday_date','=', vals["company_holiday_date"] )] )

        if holiday_line_ids :
            raise exceptions.UserError('This Date already company holiday.')
        else:
            holiday = super(hr_holidays,self).create(vals)
            return holiday
   
                 
hr_holidays()