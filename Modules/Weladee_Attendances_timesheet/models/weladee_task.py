# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.Weladee_Attendances.library.weladee_translation import add_value_translation

class weladee_task(models.Model):
    _inherit = 'project.task'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    weladee_url = fields.Char(string="Weladee Url", default="", copy=False, readonly=True)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css')
    other_assignee_ids = fields.Many2many('res.users', 'project_task_assignee','task_id','user_id',string='Other assignee')

    @api.model
    def create(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_task, self).create(vals)

        # Check if record could be created
        if ret.id and (('name-th' in vals) or ('name' in vals)):
           irobj = self.env['ir.translation']
           add_value_translation(ret, irobj, 'project.task','name',vals.get('name', ''), name_th)

        return ret

    def write(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_task, self).write(vals)

        if ret and (('name-th' in vals) or ('name' in vals)):
           irobj = self.env['ir.translation']
           for each in self:
               add_value_translation(each, irobj, 'project.task','name',vals.get('name', ''), name_th)
               break

        return ret

    def open_weladee_task(self):
        if self.weladee_url:
            return {
                'name': _('Task'),
                'type': 'ir.actions.act_url',
                'url': self.weladee_url,
                'target': 'new'
            }
        else:
            raise UserError(_("This task doesn't have a weladee id."))

    @api.depends('weladee_id')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_id:
                record.is_weladee = True
            else:
                record.is_weladee = False

    @api.depends('weladee_id')
    def _compute_css(self):
        for record in self:
            if self.weladee_id:
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit_btn_css = False
