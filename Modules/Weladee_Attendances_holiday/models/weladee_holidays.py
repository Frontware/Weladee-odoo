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
    _inherit = 'hr.leave'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    weladee_code = fields.Char('Weladee Code')
    weladee_sick = fields.Boolean('Sick')
    day_part = fields.Selection([
            ('0', 'Fullday'),
            ('1', 'Morning'),
            ('2', 'Afternoon')],string='Day part')
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)

    def action_allocated(self):
        for each in self:
            each.write({'state':'validate'})

    @api.depends('weladee_code')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_code:
                record.weladee_code = True
            else:
                record.weladee_code = False

    def open_weladee(self):
        return {
                'name': _('TimeOff'),
                'type': 'ir.actions.act_url',
                'url': 'https://www.weladee.com/holiday/employee',
                'target': 'new'
        }