# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

CONST_SETTING_SYNC_OT = 'weladee-sync-approval'
CONST_SETTING_OT_PERIOD = 'weladee-ot_period'
CONST_SETTING_OT_PERIOD_UNIT = 'weladee-ot_period_unit'

class weladee_settings_ot(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_ot(self):
        return self._get_params_value(CONST_SETTING_SYNC_OT) == 'Y'

    @api.model
    def get_ot_period_unit(self):
        return self._get_params_value(CONST_SETTING_OT_PERIOD_UNIT, number=True, default=1)

    @api.model
    def get_ot_period(self):
        return self._get_params_value(CONST_SETTING_OT_PERIOD, number=False, default='w')


    ot_period_unit = fields.Integer('Period unit',default=get_ot_period_unit)
    ot_period = fields.Selection([('w','week(s) ago'),
                                   ('m','month(s) ago'),
                                   ('y','year(s) ago'),
                                   ('all','All')],string='Since',default=get_ot_period)

    sync_ot = fields.Boolean('Sync OT', default=get_sync_ot)
    

    @api.model
    def get_settings(self):
        r = super(weladee_settings_ot, self).get_settings()
        r.sync_ot = self.get_sync_ot()

        r.ot_period_unit = self.get_ot_period_unit()
        r.ot_period = self.get_ot_period()

        return r

    def saveBtn(self):
        ret = super(weladee_settings_ot, self).saveBtn()

        config_pool = self.env['ir.config_parameter']
        if self.sync_ot:
            self._save_setting(config_pool, CONST_SETTING_OT_PERIOD_UNIT, self.ot_period_unit)
            self._save_setting(config_pool, CONST_SETTING_OT_PERIOD, self.ot_period)

        self._save_setting(config_pool, CONST_SETTING_SYNC_OT, "Y" if self.sync_ot else "")
        return ret
