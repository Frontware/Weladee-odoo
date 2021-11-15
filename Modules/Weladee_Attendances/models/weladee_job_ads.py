# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import time

from odoo import osv
from odoo import models, fields, api, _
from datetime import datetime,date, timedelta
from odoo import exceptions

from .grpcproto import odoo_pb2
from . import weladee_settings
from .sync.weladee_base import stub, myrequest, sync_clean_up, sync_message_log

class weladee_job_ads(models.Model):
    _name = 'weladee_job_ads'

    name = fields.Char(string='Name')
    position_id = fields.Many2one('hr.job',string='Position')
    publish_date = fields.Date('Publish date')
    expire_date = fields.Date('Expire date')
    location = fields.Text('Location')
    description = fields.Text('Description')
    weladee_id = fields.Char(string="Weladee ID",copy=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', "Name can't duplicate !"),
    ]

