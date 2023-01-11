# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class weladee_skill_level(models.Model):
    _inherit = 'hr.skill.level'

    name = fields.Char(required=True, translate=True)
    weladee_id = fields.Char(string="Weladee ID",copy=False, readonly=True)
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_css')

    def unlink(self):
        self.env['weladee_attendance.synchronous'].check_weladee_id(self, {})

        return super(weladee_skill_level, self).unlink()

    def open_weladee_level(self):
        if self.weladee_url:
            return {
                'name': _('Skill level'),
                'type': 'ir.actions.act_url',
                'url': 'https://www.weladee.com/skills/%s' % self.weladee_id,
                'target': 'new'
            }
        else:
            raise UserError(_("This skill type doesn't have a weladee id."))
    
    @api.depends('weladee_id')
    def _compute_css(self):
        for record in self:
            if self.weladee_id:
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.hide_edit_btn_css = False