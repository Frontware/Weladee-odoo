# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api

class weladee_project(models.Model):
    _inherit = 'project.project'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    descrition = fields.Html(translate=True)
    url = fields.Char('URL')
    note = fields.Text('Note')

    @api.model
    def create(self, vals):
        name_th = vals.get('name-th', '') 
        des_th = vals.get('description-th', '')
        del vals['name-th']
        del vals['description-th']
        ret = super(weladee_project, self).create(vals)
        irobj = self.env['ir.translation']

        irobj._set_ids('project.project,name','model','en_US', [ret.id], vals.get('name', ''))
        irobj._set_ids('project.project,name','model','th_TH', [ret.id], name_th)

        irobj._set_ids('project.project,description','model','en_US', [ret.id], vals.get('description', ''))
        irobj._set_ids('project.project,description','model','th_TH', [ret.id], des_th)

        return ret