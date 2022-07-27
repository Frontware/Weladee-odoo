# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class weladee_project(models.Model):
    _inherit = 'project.project'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    weladee_url = fields.Char(string="Weladee Url", default="", copy=False, readonly=True)
    descrition = fields.Html(translate=True)
    url = fields.Char('URL')
    note = fields.Text('Note')
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css')

    @api.model
    def create(self, vals):
        name_th = vals.get('name-th', '') 
        des_th = vals.get('description-th', '')
        if 'name-th' in vals: del vals['name-th']
        if 'description-th' in vals: del vals['description-th']
        ret = super(weladee_project, self).create(vals)
        irobj = self.env['ir.translation']

        irobj._set_ids('project.project,name','model','en_US', [ret.id], vals.get('name', ''))
        irobj._set_ids('project.project,name','model','th_TH', [ret.id], name_th)

        irobj._set_ids('project.project,description','model','en_US', [ret.id], vals.get('description', ''))
        irobj._set_ids('project.project,description','model','th_TH', [ret.id], des_th)

        return ret

    def open_weladee_project(self):
        if self.weladee_url:
            return {
                'name': _('Project'),
                'type': 'ir.actions.act_url',
                'url': self.weladee_url,
                'target': 'new'
            }
        else:
            raise UserError(_("This project doesn't have a weladee id."))
    
    @api.depends('weladee_id')
    def _compute_css(self):
        for record in self:
            if self.weladee_id:
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit_btn_css = False
