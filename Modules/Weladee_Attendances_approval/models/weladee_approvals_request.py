# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_approvals_request(models.Model):
    _inherit = 'fw.approvals.request'

    note = fields.Text(string="Note", copy=False, readonly=True)
    weladee_id = fields.Char(string="Weladee ID", copy=False, readonly=True)
    weladee_url = fields.Char(string="Weladee Url", default="", copy=False, readonly=True)
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css_hide_edit_btn')

    @api.model
    def create(self, vals):
        if 'res-mode' in vals:
            del vals['res-mode']
        return super(weladee_approvals_request, self).create(vals)
    
    def write(self, vals):
        if self.weladee_id and 'res-mode' not in vals and 'res-id' not in vals:
            raise UserError(_('This approval request can only be edited on Weladee.'))
        if 'res-mode' in vals:
            del vals['res-mode']
        if 'res-id' in vals:
            del vals['res-id']
        return super(weladee_approvals_request, self).write(vals)
    
    def open_weladee_approvals_request(self):
        if self.weladee_url:
            return {
                'name': _('Approval Request'),
                'type': 'ir.actions.act_url',
                'url': self.weladee_url,
                'target': 'new'
            }
        else:
            raise UserError(_("This approval request don't have a weladee id."))
    
    @api.depends('weladee_id')
    def _compute_css_hide_edit_btn(self):
        for record in self:
            if self.weladee_id:
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit_btn_css = False
