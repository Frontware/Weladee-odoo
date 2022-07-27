# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_approvals_type(models.Model):
    _inherit = 'fw.approvals.type'
    _sql_constraints = [
        ('unique_approval_type_name', 'UNIQUE(name,weladee_id)', _('Approval type name must be unique.')),
    ]

    weladee_id = fields.Char(string="Weladee ID",copy=False, default="", readonly=True, required=True)
    weladee_url = fields.Char(string="Weladee Url", copy=False, default="", readonly=True, required=True)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css')

    @api.model
    def create(self, vals):
        if 'res-mode' in vals:
            del vals['res-mode']
        return super(weladee_approvals_type, self).create(vals)

    def write(self, vals):
        if self.weladee_id and 'res-mode' not in vals and 'res-id' not in vals:
            raise UserError(_('This approval type can only be edited on Weladee.'))
        if 'res-mode' in vals:
            del vals['res-mode']
        if 'res-id' in vals:
            del vals['res-id']
        return super(weladee_approvals_type, self).write(vals)
    
    def open_weladee_approvals_type(self):
        if self.weladee_url:
            return {
                'name': _('Approval Type'),
                'type': 'ir.actions.act_url',
                'url': self.weladee_url,
                'target': 'new'
            }
        else:
            raise UserError(_("This approval type doesn't have a weladee id."))
    
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
