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

import datetime
import time

class hr_holidays(models.TransientModel):
    _name="weladee_attendance.company.holidays"
    _description="Weladee company holidays"
    
    company_holiday_description = fields.Char(string='Description', required=True)
    company_holiday_date_from = fields.Date(string='From', required=True)
    company_holiday_date_to = fields.Date(string='To', required=True)
    company_holiday_active = fields.Boolean("Active", default=False)
    company_holiday_notes = fields.Text('Notes')
   
                 
hr_holidays()