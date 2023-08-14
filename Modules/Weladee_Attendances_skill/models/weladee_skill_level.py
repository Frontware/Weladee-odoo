# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_skill_level(models.Model):
    _inherit = 'hr.skill.level'

    name = fields.Char(required=True, translate=True)
    weladee_id = fields.Char(string="Weladee ID",copy=False, readonly=True)
    
    def write(self, vals):
        if not self.env.context.get('updateLang'):
           for each in self:
               cansave = True
               if each.weladee_id: cansave = 'weladee_id' in vals

               if not cansave:
                  raise UserError('You cannot change this record from weladee') 

        return super(weladee_skill_level, self).write(vals)
