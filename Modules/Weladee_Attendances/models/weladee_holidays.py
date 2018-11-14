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

    weladee_code = fields.Char('Weladee Code')
    weladee_sick = fields.Boolean('Sick')

    @api.multi
    def action_allocated(self):
        for each in self:
            each.write({'state':'validate'})