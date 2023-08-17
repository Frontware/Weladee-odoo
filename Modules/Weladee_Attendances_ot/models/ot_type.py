# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.Weladee_Attendances.library.weladee_translation import add_value_translation

class weladee_ot_type(models.Model):
    _inherit = 'fwot_ot_type'

    weladee_id = fields.Char(string="Weladee ID",copy=False, default="", readonly=True, required=True)
    weladee_url = fields.Char(string="Weladee Url", copy=False, default="", readonly=True, required=True)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css')
    
    def open_weladee_ot_type(self):
        if self.weladee_url:
            return {
                'name': _('OT Type'),
                'type': 'ir.actions.act_url',
                'url': self.weladee_url,
                'target': 'new'
            }
        else:
            raise UserError(_("This OT type doesn't have a weladee id."))
    
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
        ret = super(weladee_ot_type, self).create(vals)

        if ret.id and (('name-th' in vals) or ('name' in vals)):
           irobj = self.env['ir.translation']
           add_value_translation(ret, irobj, 'fwot_ot_type','name',vals.get('name', ''), name_th)

        return ret

    def write(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_ot_type, self).write(vals)

        for each in self:
            cansave = True
            if each.weladee_id: cansave = 'weladee_id' in vals

            if not cansave:
               raise UserError('You cannot change this record from weladee') 

        if self.env.context.get('updateLang'): return ret
        if ret and (('name-th' in vals) or ('name' in vals)):
           irobj = self.env['ir.translation']
           for each in self:
               add_value_translation(each, irobj, 'fwot_ot_type','name',vals.get('name', ''), name_th)

        return ret    