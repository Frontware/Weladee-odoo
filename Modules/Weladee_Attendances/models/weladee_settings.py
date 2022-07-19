# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.addons.base.models.res_partner import _tz_get

CONST_SETTING_APIKEY = 'weladee-api_key'
CONST_SETTING_SYNC_EMAIL = 'weladee-sync-email'
CONST_SETTING_APIDB = 'weladee-api_db'
CONST_SETTING_API_DEBUG = 'weladee-api_debug'
CONST_SETTING_LOG_PERIOD = 'weladee-log_period'
CONST_SETTING_LOG_PERIOD_UNIT = 'weladee-log_period_unit'

CONST_SETTING_HOLIDAY_NOTICE = 'weladee-holiday-notify'
CONST_SETTING_HOLIDAY_NOTICE_EMAIL = 'weladee-holiday-notify-email'
CONST_SETTING_HOLIDAY_TIMEZONE = 'weladee-holiday-timezone'
CONST_SETTING_HOLIDAY_STATUS_ID = 'weladee-holiday_status_id'

CONST_SETTING_SICK_STATUS_ID = 'weladee-sick_status_id'

CONST_SETTING_EXPENSE_PRODUCT_ID = 'weladee-expense_product_id'

CONST_SETTING_TIMESHEET_ACCOUNT_ANALYTIC_ID = 'weladee-timesheet_account_analytic_id'
class wiz_setting():
    def __init__(self):
        self.authorization = False
        self.holiday_status_id = False
        self.api_db = False
        self.sick_status_id = False
        self.tz = False
        self.expense_product_id = False
        self.account_analytic_id = False

def get_api_key(self):
    '''
    get api key from settings
    return authorization, holiday_status_id, api_db

    '''
    line_ids = self.env['ir.config_parameter'].search([('key','like','weladee-%')])
    ret = wiz_setting()  
    for dataSet in line_ids:
        if dataSet.key == CONST_SETTING_APIKEY :
            ret.authorization = [("authorization", dataSet.value)]
        elif dataSet.key == CONST_SETTING_HOLIDAY_STATUS_ID:
            try:
                ret.holiday_status_id = int(float(dataSet.value))
            except:
                pass  
        elif dataSet.key == CONST_SETTING_SICK_STATUS_ID:
            try:
                ret.sick_status_id = int(float(dataSet.value))
            except:
                pass  
        elif dataSet.key == CONST_SETTING_APIDB:
            ret.api_db = dataSet.value   
            if ret.api_db != self.env.cr.dbname:
                ret.authorization = False
                ret.holiday_status_id = False
                ret.sick_status_id = False 
                ret.tz = False 
        elif dataSet.key == CONST_SETTING_HOLIDAY_TIMEZONE :
            ret.tz = dataSet.value
        elif dataSet.key == CONST_SETTING_EXPENSE_PRODUCT_ID:
            try:
                ret.expense_product_id = int(float(dataSet.value))
            except:
                pass
        elif dataSet.key == CONST_SETTING_TIMESHEET_ACCOUNT_ANALYTIC_ID:
            try:
                ret.account_analytic_id = int(dataSet.value)
            except:
                pass

    return ret

def get_synchronous_period(self):
    '''
    get synchronous log period
    '''
    rets = {'period':'w','unit':'1'}
    config_pool = self.env['ir.config_parameter']
    ret = config_pool.search([('key','=',CONST_SETTING_LOG_PERIOD)])
    if ret:
       rets['period'] = ret.value
    else:
        config_pool.create({'key':CONST_SETTING_LOG_PERIOD,'value':'w'}) 

    ret = config_pool.search([('key','=',CONST_SETTING_LOG_PERIOD_UNIT)])
    if ret:
       rets['unit'] = ret.value
    else:
        config_pool.create({'key':CONST_SETTING_LOG_PERIOD_UNIT,'value':'1'}) 

    return rets

def get_synchronous_email(self):
    '''
    get synchronous email setting    
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_SYNC_EMAIL)])
    if ret:
        return ret.value 
    else:
        self.env['ir.config_parameter'].create({'key':CONST_SETTING_SYNC_EMAIL,'value':''}) 
        return ""

def get_synchronous_debug(self):
    '''
    get synchronous debug setting    
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_API_DEBUG)])
    if ret:
        return ret.value == 'Y'     

def get_holiday_notify(self):
    '''
    get notify holiday setting    
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_HOLIDAY_NOTICE)])
    if ret:
        return ret.value == 'Y'        
    else:
        self.env['ir.config_parameter'].create({'key':CONST_SETTING_HOLIDAY_NOTICE,'value':''}) 
        return ""

def get_holiday_notify_email(self):
    '''
    get notify holiday email setting    
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_HOLIDAY_NOTICE_EMAIL)])
    if ret:
        return ret.value
    else:
        self.env['ir.config_parameter'].create({'key':CONST_SETTING_HOLIDAY_NOTICE_EMAIL,'value':''}) 
        return ""

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
        ret = get_api_key(self)

        return ret.holiday_status_id

    def _get_sick_status(self):
        ret = get_api_key(self)

        return ret.sick_status_id    

    def _get_api_key(self):
        ret = get_api_key(self)
        
        return (ret.authorization or [['','']])[0][1]

    def _get_email(self):
        return get_synchronous_email(self)

    def _get_debug(self):
        return get_synchronous_debug(self)    

    def _get_log_period_unit(self):
        ret = int(get_synchronous_period(self)['unit'])
        return ret

    def _get_log_period(self):
        ret = get_synchronous_period(self)['period']    
        return ret
    
    def _get_holiday_notify_leave_req(self):
        return get_holiday_notify(self)

    def _get_holiday_notify_leave_req_email(self):
        return get_holiday_notify_email(self)

    def _get_tz(self):
        ret = get_api_key(self)
        print(ret.tz)
        return ret.tz or self._context.get('tz')

    def _get_expense_product(self):
        ret = get_api_key(self)

        return ret.expense_product_id
    
    def _get_account_analytic(self):
        ret = get_api_key(self)

        return ret.account_analytic_id

    holiday_status_id = fields.Many2one("hr.leave.type", String="Default Leave Type",required=True,default=_get_holiday_status )
    sick_status_id = fields.Many2one("hr.leave.type", String="Sick leave Type",default=_get_sick_status )
    holiday_notify_leave_req = fields.Boolean('Notify if there is not enough allocated leave request', default=_get_holiday_notify_leave_req )
    holiday_notify_leave_req_email = fields.Text('Notified Email', default=_get_holiday_notify_leave_req_email)

    api_key = fields.Char(string="API Key", required=True,default=_get_api_key )
    email = fields.Text('Email', required=True, default=_get_email )
    api_database = fields.Char('API Database',default=lambda s: s.env.cr.dbname)
    api_debug = fields.Boolean('Show debug info',default=_get_debug)

    log_period_unit = fields.Integer('Period unit',default=_get_log_period_unit,required=True)
    log_period = fields.Selection([('w','week(s) ago'),
                                   ('m','month(s) ago'),
                                   ('y','year(s) ago'),
                                   ('all','All')],string='Since',default=_get_log_period,required=True)
    tz = fields.Selection(_tz_get, string='Timezone', default=_get_tz,required=True)    
    expense_product_id = fields.Many2one("product.product", String="Expense product",required=True,default=_get_expense_product )

    account_analytic_id = fields.Many2one('account.analytic.account', string="Account Analytic", required=True, default=_get_account_analytic)

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
        self._save_setting(config_pool, CONST_SETTING_APIKEY, self.api_key)
        self._save_setting(config_pool, CONST_SETTING_HOLIDAY_STATUS_ID, self.holiday_status_id.id)
        self._save_setting(config_pool, CONST_SETTING_SYNC_EMAIL, self.email)
        self._save_setting(config_pool, CONST_SETTING_APIDB, self.api_database)
        self._save_setting(config_pool, CONST_SETTING_SICK_STATUS_ID, self.sick_status_id.id)
        self._save_setting(config_pool, CONST_SETTING_HOLIDAY_TIMEZONE, self.tz)

        _api_debug = ""
        if self.api_debug: _api_debug = "Y"
        self._save_setting(config_pool, CONST_SETTING_API_DEBUG, _api_debug)
        self._save_setting(config_pool, CONST_SETTING_LOG_PERIOD_UNIT, self.log_period_unit)
        self._save_setting(config_pool, CONST_SETTING_LOG_PERIOD, self.log_period)

        self._save_setting(config_pool, CONST_SETTING_HOLIDAY_NOTICE, "Y" if self.holiday_notify_leave_req else "N")
        self._save_setting(config_pool, CONST_SETTING_HOLIDAY_NOTICE_EMAIL, self.holiday_notify_leave_req_email)
        
        self._save_setting(config_pool, CONST_SETTING_EXPENSE_PRODUCT_ID, self.expense_product_id.id)

        self._save_setting(config_pool, CONST_SETTING_TIMESHEET_ACCOUNT_ANALYTIC_ID, self.account_analytic_id.id)
