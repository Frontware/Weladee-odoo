# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv,api
from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.Weladee_Attendances.library.weladee_translation import add_value_translation

class weladee_gate(models.Model):
    _name = 'weladee_gate'

    name = fields.Char('Name',translate=True)
    weladee_id = fields.Char(string="Weladee ID",copy=False, default="", readonly=True, required=True)
    weladee_url = fields.Char(string="Weladee Url", copy=False, default="", readonly=True, required=True)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css')
    
    def open_weladee_gate(self):
        if self.weladee_url:
            return {
                'name': _('Weladee gate'),
                'type': 'ir.actions.act_url',
                'url': self.weladee_url,
                'target': 'new'
            }
        else:
            raise UserError(_("This gate doesn't have a weladee id."))
    
    @api.depends('weladee_id')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_id:
                record.is_weladee = True
            else:
                record.is_weladee = False

    @api.depends('weladee_id')
    def _compute_css(self):
        for record in self:
            if self.weladee_id:
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit_btn_css = False

    @api.model
    def create(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_gate, self).create(vals)

        if ret.id and (('name-th' in vals) or ('name' in vals)):
           irobj = self.env['ir.translation']
           add_value_translation(ret, irobj, 'weladee_gate','name',vals.get('name', ''), name_th)

        return ret

    def write(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_gate, self).write(vals)

        if ret and (('name-th' in vals) or ('name' in vals)):
           irobj = self.env['ir.translation']
           for each in self:
               add_value_translation(each, irobj, 'weladee_gate','name',vals.get('name', ''), name_th)
               break

        return ret    