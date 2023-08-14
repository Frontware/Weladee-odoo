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

    def unlink(self):
        self.env['weladee_attendance.synchronous'].check_weladee_id(self, {})
        return super(weladee_approvals_type, self).unlink()

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

    def write(self, vals):
        if not self.env.context.get('updateLang'):
           for each in self:
               cansave = True
               if each.weladee_id: cansave = 'weladee_id' in vals

               if not cansave:
                  raise UserError('You cannot change this record from weladee') 

        return super(weladee_approvals_type, self).write(vals)
