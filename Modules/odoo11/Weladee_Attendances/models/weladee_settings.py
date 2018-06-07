# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.addons.Weladee_Attendances.models.weladee_employee import get_api_key, CONST_SETTING_APIKEY, CONST_SETTING_HOLIDAY_STATUS_ID, CONST_SETTING_SYNC_EMAIL 

class weladee_settings(models.TransientModel):
    _name="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    '''
    purpose : get default holiday_status_id
    remarks :
    2017-09-26 CKA created
    2018-06-07 KPO save data
    '''
    def _get_holiday_status(self):
        tmp, holiday_status_id = get_api_key(self)

        return holiday_status_id

    def _get_api_key(self):
        api_key, tmp = get_api_key(self)
        
        return (api_key or [['','']])[0][1]

    def _get_email(self):
        ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_SYNC_EMAIL)])
        if ret:
           return ret.value 
        else:
           self.env['ir.config_parameter'].create({'key':CONST_SETTING_SYNC_EMAIL,'value':''}) 
           return ""


    holiday_status_id = fields.Many2one("hr.holidays.status", String="Leave Type",required=True,default=_get_holiday_status )
    api_key = fields.Char(string="API Key", required=True,default=_get_api_key )
    email = fields.Char('Email', required=True, default=_get_email )

    def saveBtn(self):
        '''
        write back to parameter
        '''
        line_ids = self.env['ir.config_parameter'].search([('key','like','weladee-%')])

        if len(line_ids) == 0:
           self.env['ir.config_parameter'].create({'key':CONST_SETTING_APIKEY,
                                                   'value': self.api_key}) 
           self.env['ir.config_parameter'].create({'key':CONST_SETTING_HOLIDAY_STATUS_ID,
                                                   'value': self.holiday_status_id.id}) 
           self.env['ir.config_parameter'].create({'key':CONST_SETTING_SYNC_EMAIL,
                                                   'value': self.email}) 
           return

        for each in line_ids:
            if each.key == CONST_SETTING_APIKEY:
               each.write({'value':self.api_key}) 
            elif each.key == CONST_SETTING_HOLIDAY_STATUS_ID:
               each.write({'value':self.holiday_status_id.id})                
            elif each.key == CONST_SETTING_SYNC_EMAIL:
               each.write({'value':self.email})                

weladee_settings()
