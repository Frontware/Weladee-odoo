# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

CONST_SETTING_SYNC_APPROVAL = 'weladee-sync-approval'

class weladee_settings_approval(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_approval(self):
        return self._get_params_value(CONST_SETTING_SYNC_APPROVAL) == 'Y'

    sync_approval = fields.Boolean('Sync Approval', default=get_sync_approval)
    

    @api.model
    def get_settings(self):
        r = super(weladee_settings_approval, self).get_settings()
        r.sync_approval = self.get_sync_approval()
               
        return r

    def saveBtn(self):
        ret = super(weladee_settings_approval, self).saveBtn()

        config_pool = self.env['ir.config_parameter']
        self._save_setting(config_pool, CONST_SETTING_SYNC_APPROVAL, "Y" if self.sync_approval else "")
        return ret
