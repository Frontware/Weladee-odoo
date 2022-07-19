# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_approvals_approver(models.Model):
    _inherit = 'fw.approvals.approver'

    weladee_id = fields.Char(string="Weladee ID",copy=False)

    @api.model
    def create(self, vals):
        if 'res-mode' in vals:
            del vals['res-mode']
        return super(weladee_approvals_approver, self).create(vals)
    
    def write(self, vals):
        if 'res-mode' in vals:
            del vals['res-mode']
        if 'res-id' in vals:
            del vals['res-id']
        return super(weladee_approvals_approver, self).write(vals)
