# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_approvals_type_approver(models.Model):
    _inherit = 'fw.approvals.type.approver'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
