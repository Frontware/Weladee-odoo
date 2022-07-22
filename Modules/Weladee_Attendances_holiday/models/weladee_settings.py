# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get

CONST_SETTING_HOLIDAY_NOTICE = 'weladee-holiday-notify'
CONST_SETTING_HOLIDAY_NOTICE_EMAIL = 'weladee-holiday-notify-email'
CONST_SETTING_HOLIDAY_TIMEZONE = 'weladee-holiday-timezone'
CONST_SETTING_HOLIDAY_STATUS_ID = 'weladee-holiday_status_id'
CONST_SETTING_HOLIDAY_PERIOD = 'weladee-holiday_period'
CONST_SETTING_HOLIDAY_PERIOD_UNIT = 'weladee-holiday_period_unit'
CONST_SETTING_SICK_STATUS_ID = 'weladee-sick_status_id'

CONST_SETTING_SYNC_HOLIDAY = 'weladee-sync-holiday'

class weladee_settings_holiday(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_holiday(self):
        return self._get_params_value(CONST_SETTING_SYNC_HOLIDAY) == 'Y'

    @api.model
    def get_holiday_notify_leave_req(self):
        return self._get_params_value(CONST_SETTING_HOLIDAY_NOTICE) == 'Y' 

    @api.model
    def get_holiday_notify_leave_req_email(self):
        return self._get_params_value(CONST_SETTING_HOLIDAY_NOTICE_EMAIL)
    
    @api.model
    def get_holiday_period_unit(self):
        return self._get_params_value(CONST_SETTING_HOLIDAY_PERIOD_UNIT, number=True, default=1)

    @api.model
    def get_holiday_period(self):
        return self._get_params_value(CONST_SETTING_HOLIDAY_PERIOD, number=False, default='w')

    @api.model
    def get_holiday_tz(self):
        return self._get_params_value(CONST_SETTING_HOLIDAY_TIMEZONE,default=self._context.get('tz'))

    @api.model
    def get_holiday_status(self):
        return self._get_params_value(CONST_SETTING_HOLIDAY_STATUS_ID, number=True)

    @api.model
    def get_holiday_sick_status(self):
        return self._get_params_value(CONST_SETTING_SICK_STATUS_ID, number=True)    

    holiday_status_id = fields.Many2one("hr.leave.type", String="Default Leave Type",default=get_holiday_status )
    sick_status_id = fields.Many2one("hr.leave.type", String="Sick leave Type",default=get_holiday_sick_status )
    holiday_notify_leave_req = fields.Boolean('Notify if there is not enough allocated leave request', default=get_holiday_notify_leave_req )
    holiday_notify_leave_req_email = fields.Text('Notified Email', default=get_holiday_notify_leave_req_email)

    tz = fields.Selection(_tz_get, string='Timezone', default=get_holiday_tz)
    holiday_period_unit = fields.Integer('Period unit', default=get_holiday_period_unit)
    holiday_period = fields.Selection([('w','week(s) ago'),
                                       ('m','month(s) ago'),
                                       ('y','year(s) ago'),
                                       ('all', 'All')], string='Since', default=get_holiday_period)
    
    sync_holiday = fields.Boolean('Sync Holiday', default=get_sync_holiday)
    

    @api.model
    def get_settings(self):
        r = super(weladee_settings_holiday, self).get_settings()
        r.sync_holiday = self.get_sync_holiday()
        
        r.holiday_status_id = self.get_holiday_status()
        r.sick_status_id = self.get_holiday_sick_status()
        r.tz = self.get_holiday_tz()
       
        return r

    def saveBtn(self):
        ret = super(weladee_settings_holiday, self).saveBtn()

        config_pool = self.env['ir.config_parameter']
        if self.sync_holiday:
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_TIMEZONE, self.tz)
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_STATUS_ID, self.holiday_status_id.id)
           self._save_setting(config_pool, CONST_SETTING_SICK_STATUS_ID, self.sick_status_id.id)
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_NOTICE, "Y" if self.holiday_notify_leave_req else "N")
           if self.holiday_notify_leave_req:
              self._save_setting(config_pool, CONST_SETTING_HOLIDAY_NOTICE_EMAIL, self.holiday_notify_leave_req_email)
           
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_PERIOD_UNIT, self.holiday_period_unit)
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_PERIOD, self.holiday_period)

        self._save_setting(config_pool, CONST_SETTING_SYNC_HOLIDAY, "Y" if self.sync_holiday else "")
        return ret
