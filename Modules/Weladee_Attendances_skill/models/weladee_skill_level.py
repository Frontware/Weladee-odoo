# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_skill_level(models.Model):
    _inherit = 'hr.skill.level'

    name = fields.Char(required=True, translate=True)
    weladee_id = fields.Char(string="Weladee ID",copy=False, readonly=True)

    @api.model
    def create(self, vals):
        if 'res-mode' in vals:
            del vals['res-mode']
        return super(weladee_skill_level, self).create(vals)

    def write(self, vals):
        if 'res-mode' in vals:
            del vals['res-mode']
        if 'res-id' in vals:
            del vals['res-id']
        return super(weladee_skill_level, self).write(vals)
