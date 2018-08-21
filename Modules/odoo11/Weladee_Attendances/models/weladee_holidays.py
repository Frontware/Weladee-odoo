# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv,api
from odoo import models, fields
from odoo import exceptions
'''
import base64
import requests
import time
import webbrowser

from datetime import datetime,date, timedelta

from .grpcproto import odoo_pb2
from .grpcproto import odoo_pb2_grpc
from .grpcproto import weladee_pb2
from . import weladee_grpc
from . import weladee_employee
from .sync.weladee_base import stub, myrequest
'''

class weladee_holidays(models.Model):
    _inherit = 'hr.holidays'

    weladee_code = fields.Char('Weladee Code')
    weladee_sick = fields.Boolean('Sick')

    @api.multi
    def action_allocated(self):
        for each in self:
            each.write({'state':'validate'})
