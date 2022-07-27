# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_skill_type(models.Model):
    _inherit = 'hr.skill.type'

    name = fields.Char(required=True, translate=True)
    weladee_id = fields.Char(string="Weladee ID",copy=False, readonly=True)
    weladee_url = fields.Char(string="Weladee Url", default="", copy=False, readonly=True)
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css')

    @api.model
    def create(self, vals):
        if 'res-mode' in vals:
            del vals['res-mode']
        return super(weladee_skill_type, self).create(vals)

    def write(self, vals):
        if self.weladee_id and 'res-mode' not in vals and 'res-id' not in vals:
            raise UserError(_('This skill type can only be edited on Weladee.'))
        if 'res-mode' in vals:
            del vals['res-mode']
        if 'res-id' in vals:
            del vals['res-id']
        return super(weladee_skill_type, self).write(vals)
    
    def open_weladee_skill_type(self):
        if self.weladee_url:
            return {
                'name': _('Skill Type'),
                'type': 'ir.actions.act_url',
                'url': self.weladee_url,
                'target': 'new'
            }
        else:
            raise UserError(_("This skill type don't have a weladee id."))
    
    @api.depends('weladee_id')
    def _compute_css(self):
        for record in self:
            if self.weladee_id:
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit_btn_css = False
