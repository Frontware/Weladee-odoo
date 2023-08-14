# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import time

from odoo import models, fields, api, _
from datetime import datetime,date, timedelta

class weladee_position_job(models.Model):
    _inherit = 'hr.job'

    job_ads_ids = fields.One2many('weladee_job_ads','position_id',string='Job ads')
