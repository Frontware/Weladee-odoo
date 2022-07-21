# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get

CONST_SETTING_APIKEY = 'weladee-api_key'
CONST_SETTING_SYNC_EMAIL = 'weladee-sync-email'
CONST_SETTING_APIDB = 'weladee-api_db'
CONST_SETTING_API_DEBUG = 'weladee-api_debug'

CONST_SETTING_SYNC_EMPLOYEE = 'weladee-sync-employee'
CONST_SETTING_SYNC_POSITION = 'weladee-sync-position'
CONST_SETTING_SYNC_DEPARTMENT = 'weladee-sync-department'

class wiz_setting():
    def __init__(self):
        self.authorization = False
        self.api_db = False
        self.sync_employee = True
        self.sync_position = True
        self.sync_department = True

class weladee_settings(models.TransientModel):
    _name="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    def _get_params_value(self, key, number=False, default=False):
        r = self.env['ir.config_parameter'].get_param(key)
        if number:
           try:
                return int(float(r)) or default
           except:
                if default: return default
        else:
           return r or default
    
    @api.model
    def get_settings(self):
        r = wiz_setting()
        r.authorization = [("authorization", self.get_api_key())]
        r.api_db = self._get_params_value(CONST_SETTING_APIDB)
        if r.api_db != self.env.cr.dbname:
           r.authorization = False
           r.api_db = False

        return r

    '''
    purpose : get default holiday_status_id
    remarks :
    2017-09-26 CKA created
    2018-06-07 KPO save data
    '''

    @api.model
    def get_api_key(self):
       return self._get_params_value(CONST_SETTING_APIKEY)

    @api.model
    def get_synchronous_email(self):
        return self._get_params_value(CONST_SETTING_SYNC_EMAIL)

    @api.model
    def get_synchronous_debug(self):
        return self._get_params_value(CONST_SETTING_API_DEBUG) == 'Y'   

    api_key = fields.Char(string="API Key", required=True,default=get_api_key )
    email = fields.Text('Email', required=True, default=get_synchronous_email )
    api_database = fields.Char('API Database',default=lambda s: s.env.cr.dbname)
    api_debug = fields.Boolean('Show debug info',default=get_synchronous_debug)

    sync_employee = fields.Boolean('Sync Employee', readonly=True, default=True)
    sync_position = fields.Boolean('Sync Position', readonly=True, default=True)
    sync_department = fields.Boolean('Sync Department', readonly=True, default=True)

    def _save_setting(self, pool, key, value):
        line_ids = pool.search([('key','=',key)])
        if len(line_ids) == 0:
           line_ids.create({'key':key, 'value': value}) 
        else:
          line_ids.write({'value': value})   

    def saveBtn(self):
        '''
        write back to parameter
        '''
        config_pool = self.env['ir.config_parameter']
        self._save_setting(config_pool, CONST_SETTING_APIDB, self.api_database)
        self._save_setting(config_pool, CONST_SETTING_APIKEY, self.api_key)

        # notification
        self._save_setting(config_pool, CONST_SETTING_SYNC_EMAIL, self.email)
        _api_debug = ""
        if self.api_debug: _api_debug = "Y"
        self._save_setting(config_pool, CONST_SETTING_API_DEBUG, _api_debug)

        self._save_setting(config_pool, CONST_SETTING_SYNC_EMPLOYEE, "Y" if self.sync_employee else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_POSITION, "Y" if self.sync_position else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_DEPARTMENT, "Y" if self.sync_department else "")
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
