# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api

class weladee_mail_act_type(models.Model):
    _inherit = 'mail.activity.type'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    weladee_code = fields.Char(string='Weladee Code',copy=False)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    name_thai = fields.Char(string='Name(thai)')

    @api.depends('weladee_id')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_id:
                record.is_weladee = True
            else:
                record.is_weladee = False
