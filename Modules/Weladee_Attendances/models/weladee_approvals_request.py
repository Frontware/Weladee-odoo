# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_approvals_request(models.Model):
    _inherit = 'fw.approvals.request'

    note = fields.Text(string="Note", copy=False, readonly=True)
    weladee_id = fields.Char(string="Weladee ID", copy=False, readonly=True)
    weladee_url = fields.Char(string="Weladee Url", default="", copy=False, readonly=True)

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
