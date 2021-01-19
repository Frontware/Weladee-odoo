# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv,api
from odoo import models, fields
from odoo import exceptions

class weladee_expense_type(models.Model):
    _name = 'weladee_expense_type'

    weladee_code = fields.Char('Weladee Code')
    name_english = fields.Char('Name english')
    name_thai = fields.Char('Name english')
    note = fields.Text('Note')

    _sql_constraints = [
      ('weladee_code_uniq', 'unique(weladee_code)', "Weladee Expense type Code can't duplicate !"),
    ]
