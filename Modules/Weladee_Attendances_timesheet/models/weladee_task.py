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
           add_value_translation(ret, 'name',vals.get('name', ''), name_th)

        return ret
        
    def unlink(self):
        self.env['weladee_attendance.synchronous'].check_weladee_id(self, {})

        return super(weladee_task, self).unlink()

    def write(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']

        if not self.env.context.get('updateLang'): 
           for each in self:
               cansave = True
               if each.weladee_id: cansave = 'weladee_id' in vals

               if not cansave and self.env.context.get('validate_weladee_id', True):
                  raise UserError(_('You cannot change this record from weladee') )

        ret = super(weladee_task, self).write(vals)

        if self.env.context.get('updateLang'): return ret
        if ret and (('name-th' in vals) or ('name' in vals)):
           for each in self:
               add_value_translation(each, 'name', vals.get('name', ''), name_th)

        return ret
    
    @api.model
    def _task_message_auto_subscribe_notify(self, users_per_task):
        if self.env.context.get('mail_auto_subscribe_no_notify'): return

        return super()._task_message_auto_subscribe_notify(users_per_task)

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
            if record.weladee_id:
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit_btn_css = False
