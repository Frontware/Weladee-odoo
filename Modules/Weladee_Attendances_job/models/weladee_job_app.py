# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import time

from odoo import osv
from odoo import models, fields, api, _
from datetime import datetime,date, timedelta
from odoo import exceptions

class weladee_job_app(models.Model):
    _inherit = 'hr.applicant'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    lastname = fields.Char('Last name')
    firstname = fields.Char('First name')
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')])
    lang_id = fields.Many2one('res.lang', string='Language')
    date_apply = fields.Datetime(string='Apply date')
    note = fields.Text(string='Note')