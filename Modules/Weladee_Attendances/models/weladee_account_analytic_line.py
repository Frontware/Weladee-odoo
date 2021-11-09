# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api

class weladee_account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    weladee_id = fields.Char(string="Weladee ID",copy=False)