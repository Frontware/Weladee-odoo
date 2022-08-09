# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class weladee_expense_type(models.Model):
    _name = 'weladee_expense_type'
    _inherit = ['image.mixin']

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    name = fields.Char('Name',translated=True)
    code = fields.Char('Code')
    active = fields.Boolean('Active',default=True)
    image_1920 = fields.Image('Icon')

    @api.model
    def create(self, vals):
        name_th = vals.get('name-th', '')
        des_th = vals.get('description-th', '')
        if 'name-th' in vals: del vals['name-th']
        if 'description-th' in vals: del vals['description-th']
        ret = super(weladee_project, self).create(vals)
        irobj = self.env['ir.translation']

        # Check if record could be created
        if ret.id:
            irobj._set_ids('project.project,name','model','en_US', [ret.id], vals.get('name', ''))
            irobj._set_ids('project.project,name','model','th_TH', [ret.id], name_th)

            irobj._set_ids('project.project,description','model','en_US', [ret.id], vals.get('description', ''))
            irobj._set_ids('project.project,description','model','th_TH', [ret.id], des_th)

        return ret

    def write(self, vals):
        name_th = vals.get('name-th', '')
        des_th = vals.get('description-th', '')
        if 'name-th' in vals: del vals['name-th']
        if 'description-th' in vals: del vals['description-th']
        ret = super(weladee_project, self).write(vals)
        irobj = self.env['ir.translation']

        # Check if record exists
        for each in self:
            irobj._set_ids('project.project,name','model','en_US', [each.id], vals.get('name', ''))
            irobj._set_ids('project.project,name','model','th_TH', [each.id], name_th)

            irobj._set_ids('project.project,description','model','en_US', [each.id], vals.get('description', ''))
            irobj._set_ids('project.project,description','model','th_TH', [each.id], des_th)

        return ret    