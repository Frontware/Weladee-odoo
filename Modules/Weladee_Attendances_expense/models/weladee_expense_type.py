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
    _description = 'weladee_expense_type'
    _inherit = ['image.mixin']

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    name = fields.Char('Name',translate=True)
    code = fields.Char('Code')
    active = fields.Boolean('Active',default=True)
    image_1920 = fields.Image('Icon')

    @api.model
    def create(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_expense_type, self).create(vals)

        if ret.id and (('name-th' in vals) or ('name' in vals)):
           add_value_translation(ret, 'name', vals.get('name', ''), name_th)

        return ret

    def unlink(self):
        self.env['weladee_attendance.synchronous'].check_weladee_id(self, {})

        return super(weladee_expense_type, self).unlink()

    def write(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_expense_type, self).write(vals)

        if self.env.context.get('updateLang'): return ret

        for each in self:
            cansave = True
            if each.weladee_id: cansave = 'weladee_id' in vals

            if not cansave:
               raise UserError(_('You cannot change this record from weladee') )

        if ret and (('name-th' in vals) or ('name' in vals)):
           for each in self:
               add_value_translation(each, 'name', vals.get('name', ''), name_th)

        return ret    
    
    def open_weladee_type(self):
        if self.weladee_id:
            return {
                'name': _('Weladee Expense type'),
                'type': 'ir.actions.act_url',
                'url': 'https://www.weladee.com/expense/type/%s' % self.weladee_id,
                'target': 'new'
            }
        else:
            raise UserError(_("This expense type doesn't have a weladee id."))
       
