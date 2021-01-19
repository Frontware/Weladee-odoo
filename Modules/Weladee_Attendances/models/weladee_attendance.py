# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _

class weladee_attendance(models.Model):
    _inherit = 'hr.attendance'

    _sql_constraints = [
        ('unique_empin_timestamp', 'unique (employee_id, check_in)', 'Employee checkin record must not duplicate'),
        ('unique_empout_timestamp', 'unique (employee_id, check_out)', 'Employee checkout record must not duplicate'),
    ]