# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api

class weladee_project(models.Model):
    _inherit = 'project.project'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    name_thai = fields.Char(string='Name(thai)')