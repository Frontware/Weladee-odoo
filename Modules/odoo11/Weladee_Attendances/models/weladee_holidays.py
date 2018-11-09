# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
from lxml import etree

from odoo import osv,api
from odoo import models, fields
from odoo import exceptions
from odoo.tools.translate import _

from odoo.addons.Weladee_Attendances.library.weladee_translation import allocate_holiday_tag

class weladee_holidays(models.Model):
    _inherit = 'hr.holidays'

    weladee_code = fields.Char('Weladee Code')
    weladee_sick = fields.Boolean('Sick')

    @api.multi
    def action_allocated(self):
        for each in self:
            each.write({'state':'validate'})

    @api.multi
    def name_get(self):
        res = super(weladee_holidays, self).name_get()
        # fixed allocate by tag name
        fixed_res = {}
        for leave in self:
            if leave.type != 'remove':
                fixed_res[leave.id] = _("Allocation of %s : %.2f day(s) To %s") % \
                (leave.holiday_status_id.name, 
                leave.number_of_days_temp,
                leave.employee_id.name if leave.employee_id else allocate_holiday_tag() % leave.category_id.name)
        
        newres = []
        for leave in res:
            if leave[0] in fixed_res:
                newres.append((leave[0],fixed_res[leave[0]]))
            else:
                newres.append(leave)

        return newres