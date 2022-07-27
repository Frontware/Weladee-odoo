# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api

class weladee_expense(models.Model):
    _inherit = 'hr.expense'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    project_id = fields.Many2one('project.project',string='Project')
    user_id = fields.Many2one('res.users')
    journal_id = fields.Many2one('account.journal')
    bill_partner_id = fields.Many2one('res.partner')

    request_amount = fields.Float(string='Amount request',digits=(10,2))
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css')

    @api.depends('weladee_id')
    def _compute_css(self):
        for record in self:
            if self.weladee_id:
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit_btn_css = False