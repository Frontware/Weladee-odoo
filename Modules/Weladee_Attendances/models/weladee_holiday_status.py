# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv,api
from odoo import models, fields
from odoo import exceptions

class weladee_holiday_status(models.Model):
    _inherit = 'hr.leave.type'

    weladee_code = fields.Char('Weladee Code')

    _sql_constraints = [
      ('weladee_code_uniq', 'unique(weladee_code)', "Weladee Holiday Type can't duplicate !"),
    ]
