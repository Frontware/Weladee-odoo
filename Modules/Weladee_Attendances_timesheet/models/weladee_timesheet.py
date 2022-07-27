# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class weladee_account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    work_type_id = fields.Many2one('mail.activity.type', string='Work type')
    weladee_cost = fields.Float(string="Weladee cost",digits=(12,2))

    def open_weladee_timesheet(self):
      '''
      open weladee timesheet url
      '''
      if self.weladee_id:
        return {
              'name': _("Weladee Timesheet"),
              'type': 'ir.actions.act_url',
              'target': 'new'
          }
      else:
        raise UserError(_("This employee doesn't have weladee url."))

    @api.depends('weladee_id')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_id:
                record.is_weladee = True
            else:
                record.is_weladee = False
