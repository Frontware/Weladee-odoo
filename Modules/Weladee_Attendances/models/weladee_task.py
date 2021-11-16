# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api

class weladee_task(models.Model):
    _inherit = 'project.task'

    weladee_id = fields.Char(string="Weladee ID",copy=False)

    @api.model
    def create(self, vals):
        name_th = vals.get('name-th', '') 
        del vals['name-th']
        ret = super(weladee_task, self).create(vals)
        irobj = self.env['ir.translation']

        irobj._set_ids('project.task,name','model','en_US', [ret.id], vals.get('name', ''))
        irobj._set_ids('project.task,name','model','th_TH', [ret.id], name_th)

        return ret    