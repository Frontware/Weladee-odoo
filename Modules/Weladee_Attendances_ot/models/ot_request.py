# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_ot_request(models.Model):
    _inherit = 'fwot_ot_requests'
    
    weladee_id = fields.Char(string="Weladee ID", copy=False, readonly=True)
    weladee_url = fields.Char(string="Weladee Url", default="", copy=False, readonly=True)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css_hide_edit_btn')
    
    def open_weladee_ot_request(self):
        if self.weladee_url:
            return {
                'name': _('OT Request'),
                'type': 'ir.actions.act_url',
                'url': self.weladee_url,
                'target': 'new'
            }
        else:
            raise UserError(_("This ot request doesn't have a weladee id."))
    
    @api.depends('weladee_id')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_id:
                record.is_weladee = True
            else:
                record.is_weladee = False

    @api.depends('weladee_id')
    def _compute_css_hide_edit_btn(self):
        for record in self:
            if self.weladee_id:
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit_btn_css = False

    def unlink(self):
        self.env['weladee_attendance.synchronous'].check_weladee_id(self, {})

        return super(weladee_ot_request, self).unlink()    