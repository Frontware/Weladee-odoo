# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

CONST_SETTING_SYNC_SKILL = 'weladee-sync-skill'

class weladee_settings_skill(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_skill(self):
        return self._get_params_value(CONST_SETTING_SYNC_SKILL) == 'Y'


    sync_skill = fields.Boolean('Sync Skill', default=get_sync_skill)
    

    @api.model
    def get_settings(self):
        r = super(weladee_settings_skill, self).get_settings()
        r.sync_skill = self.get_sync_skill()
               
        return r

    def saveBtn(self):
        ret = super(weladee_settings_skill, self).saveBtn()

        config_pool = self.env['ir.config_parameter']
        self._save_setting(config_pool, CONST_SETTING_SYNC_SKILL, "Y" if self.sync_skill else "")
        return ret
