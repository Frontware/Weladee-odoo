# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class weladee_mail_act_type(models.Model):
    _inherit = 'mail.activity.type'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    weladee_code = fields.Char(string='Weladee Code',copy=False)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    hide_edit_btn_css = fields.Html(string='css', sanitize=False, compute='_compute_from_weladee')

    @api.model
    def create(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_mail_act_type, self).create(vals)

        # Check if record could be created
        if ret and name_th:
           ret.with_context(lang='th_TH').write({'name': name_th})

        return ret
        
    def unlink(self):
        self.env['weladee_attendance.synchronous'].check_weladee_id(self, {})

        return super(weladee_mail_act_type, self).unlink()

    def write(self, vals):
        name_th = vals.get('name-th', '')
        if 'name-th' in vals: del vals['name-th']
        ret = super(weladee_mail_act_type, self).write(vals)

        if ret and name_th:
           for each in self: 
               each.with_context(lang='th_TH').write({'name': name_th})

        return ret

    def open_weladee_type(self):
        if self.weladee_id:
            return {
                'name': _('WorkType'),
                'type': 'ir.actions.act_url',
                'url': 'https://www.weladee.com/worktype/%s' % self.weladee_id,
                'target': 'new'
            }
        else:
            raise UserError(_("This type doesn't have a weladee id."))

    @api.depends('weladee_id')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_id:
                record.is_weladee = True
                record.hide_edit_btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
            else:
                record.is_weladee = False
                record.hide_edit_btn_css = False
