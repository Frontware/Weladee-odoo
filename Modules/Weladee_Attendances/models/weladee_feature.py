# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class weladee_attendance_feature(models.Model):
    _name = "weladee_attendance_feature"
    _order = 'sequence'

    #fields
    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')
    description = fields.Text('Description')
    active = fields.Boolean('Active')

    to_odoo = fields.Boolean('Sync to odoo')
    to_weladee = fields.Boolean('Sync to weladee')
