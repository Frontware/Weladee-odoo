# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_skill(models.Model):
    _inherit = 'hr.skill'

    name = fields.Char(required=True, translate=True)
    weladee_id = fields.Char(string="Weladee ID",copy=False, readonly=True)
