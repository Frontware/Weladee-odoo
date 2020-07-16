# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
from lxml import etree

from odoo import osv,api
from odoo import models, fields
from odoo import exceptions
from odoo.tools.translate import _

class weladee_expenses(models.Model):
    _inherit = 'hr.expense'

    weladee_type = fields.Many2one('weladee_expense_type','Expense Type')