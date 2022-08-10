# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.Weladee_Attendances.library.weladee_translation import add_value_translation

class weladee_expense_type(models.Model):
    _name = 'weladee_expense_type'
    _inherit = ['image.mixin']

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    name = fields.Char('Name',translated=True)
    code = fields.Char('Code')
    active = fields.Boolean('Active',default=True)
    image_1920 = fields.Image('Icon')

    @api.model
    def create(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_expense_type, self).create(vals)

        if ret.id and (('name-th' in vals) or ('name' in vals)):
           irobj = self.env['ir.translation']
           add_value_translation(ret, irobj, 'weladee_expense_type','name',vals.get('name', ''), name_th)

        return ret

    def write(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_expense_type, self).write(vals)

        if ret and (('name-th' in vals) or ('name' in vals)):
           irobj = self.env['ir.translation']
           for each in self:
               add_value_translation(each, irobj, 'weladee_expense_type','name',vals.get('name', ''), name_th)
               break

        return ret    