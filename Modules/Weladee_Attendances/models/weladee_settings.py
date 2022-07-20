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
CONST_SETTING_HOLIDAY_PERIOD = 'weladee-holiday_period'
CONST_SETTING_HOLIDAY_PERIOD_UNIT = 'weladee-holiday_period_unit'

CONST_SETTING_SICK_STATUS_ID = 'weladee-sick_status_id'

CONST_SETTING_EXPENSE_PRODUCT_ID = 'weladee-expense_product_id'
CONST_SETTING_EXPENSE_PERIOD = 'weladee-expense_period'
CONST_SETTING_EXPENSE_PERIOD_UNIT = 'weladee-expense_period_unit'

CONST_SETTING_TIMESHEET_ACCOUNT_ANALYTIC_ID = 'weladee-timesheet_account_analytic_id'
CONST_SETTING_TIMESHEET_PERIOD = 'weladee-timesheet_period'
CONST_SETTING_TIMESHEET_PERIOD_UNIT = 'weladee-timesheet_period_unit'

CONST_SETTING_SYNC_EMPLOYEE = 'weladee-sync-employee'
CONST_SETTING_SYNC_POSITION = 'weladee-sync-position'
CONST_SETTING_SYNC_DEPARTMENT = 'weladee-sync-department'
CONST_SETTING_SYNC_CUSTOMER = 'weladee-sync-customer'
CONST_SETTING_SYNC_ATTENDANCE = 'weladee-sync-attendance'
CONST_SETTING_SYNC_HOLIDAY = 'weladee-sync-holiday'
CONST_SETTING_SYNC_EXPENSE = 'weladee-sync-expense'
CONST_SETTING_SYNC_TIMESHEET = 'weladee-sync-timesheet'
CONST_SETTING_SYNC_JOB = 'weladee-sync-job'
CONST_SETTING_SYNC_SKILL = 'weladee-sync-skill'
CONST_SETTING_SYNC_APPROVAL = 'weladee-sync-approval'
class wiz_setting():
    def __init__(self):
        self.authorization = False
        self.holiday_status_id = False
        self.api_db = False
        self.sick_status_id = False
        self.tz = False
        self.expense_product_id = False
        self.account_analytic_id = False
        self.holiday_period_unit = False
        self.holiday_period = False
        self.timesheet_period_unit = False
        self.timesheet_period = False
        self.expense_period_unit = False
        self.expense_period = False

        self.sync_employee = False
        self.sync_position = False
        self.sync_department = False
        self.sync_customer = False
        self.sync_attendance = False
        self.sync_holiday = False
        self.sync_expense = False
        self.sync_timesheet = False
        self.sync_job = False
        self.sync_skill = False
        self.sync_approval = False

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
        elif dataSet.key == CONST_SETTING_HOLIDAY_PERIOD_UNIT:
            try:
                ret.holiday_period_unit = int(dataSet.value)
            except:
                ret.holiday_period_unit = 1
        elif dataSet.key == CONST_SETTING_HOLIDAY_PERIOD:
            ret.holiday_period = dataSet.value
        elif dataSet.key == CONST_SETTING_TIMESHEET_PERIOD_UNIT:
            try:
                ret.timesheet_period_unit = int(dataSet.value)
            except:
                ret.timesheet_period_unit = 1
        elif dataSet.key == CONST_SETTING_TIMESHEET_PERIOD:
            ret.timesheet_period = dataSet.value
        elif dataSet.key == CONST_SETTING_EXPENSE_PERIOD_UNIT:
            try:
                ret.expense_period_unit = int(dataSet.value)
            except:
                ret.expense_period_unit = 1
        elif dataSet.key == CONST_SETTING_EXPENSE_PERIOD:
            ret.expense_period = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_EMPLOYEE:
            ret.sync_employee = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_POSITION:
            ret.sync_position = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_DEPARTMENT:
            ret.sync_department = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_CUSTOMER:
            ret.sync_customer = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_ATTENDANCE:
            ret.sync_attendance = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_HOLIDAY:
            ret.sync_holiday = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_EXPENSE:
            ret.sync_expense = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_TIMESHEET:
            ret.sync_timesheet = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_JOB:
            ret.sync_job = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_SKILL:
            ret.sync_skill = dataSet.value
        elif dataSet.key == CONST_SETTING_SYNC_APPROVAL:
            ret.sync_approval = dataSet.value

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

def get_holiday_period(self):
    '''
    get synchronous holiday period
    '''
    rets = {'period':'w','unit':'1'}
    config_pool = self.env['ir.config_parameter']
    ret = config_pool.search([('key','=',CONST_SETTING_HOLIDAY_PERIOD)])
    if ret:
       rets['period'] = ret.value
    else:
        config_pool.create({'key':CONST_SETTING_HOLIDAY_PERIOD,'value':'w'})

    ret = config_pool.search([('key','=',CONST_SETTING_HOLIDAY_PERIOD_UNIT)])
    if ret:
       rets['unit'] = ret.value
    else:
        config_pool.create({'key':CONST_SETTING_HOLIDAY_PERIOD_UNIT,'value':'1'})

    return rets

def get_timesheet_period(self):
    '''
    get synchronous timesheet period
    '''
    rets = {'period':'w','unit':'1'}
    config_pool = self.env['ir.config_parameter']
    ret = config_pool.search([('key','=',CONST_SETTING_TIMESHEET_PERIOD)])
    if ret:
       rets['period'] = ret.value
    else:
        config_pool.create({'key':CONST_SETTING_TIMESHEET_PERIOD,'value':'w'})

    ret = config_pool.search([('key','=',CONST_SETTING_TIMESHEET_PERIOD_UNIT)])
    if ret:
       rets['unit'] = ret.value
    else:
        config_pool.create({'key':CONST_SETTING_TIMESHEET_PERIOD_UNIT,'value':'1'})

    return rets

def get_expense_period(self):
    '''
    get synchronous expense period
    '''
    rets = {'period':'w','unit':'1'}
    config_pool = self.env['ir.config_parameter']
    ret = config_pool.search([('key','=',CONST_SETTING_EXPENSE_PERIOD)])
    if ret:
       rets['period'] = ret.value
    else:
        config_pool.create({'key':CONST_SETTING_EXPENSE_PERIOD,'value':'w'})

    ret = config_pool.search([('key','=',CONST_SETTING_EXPENSE_PERIOD_UNIT)])
    if ret:
       rets['unit'] = ret.value
    else:
        config_pool.create({'key':CONST_SETTING_EXPENSE_PERIOD_UNIT,'value':'1'})

    return rets

def get_synchronous_attendance(self):
    '''
    get synchronous attendance setting
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_SYNC_ATTENDANCE)])
    if ret:
        return ret.value == 'Y'

def get_synchronous_holiday(self):
    '''
    get synchronous holiday setting
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_SYNC_HOLIDAY)])
    if ret:
        return ret.value == 'Y'

def get_synchronous_expense(self):
    '''
    get synchronous expense setting
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_SYNC_EXPENSE)])
    if ret:
        return ret.value == 'Y'

def get_synchronous_timesheet(self):
    '''
    get synchronous timesheet setting
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_SYNC_TIMESHEET)])
    if ret:
        return ret.value == 'Y'

def get_synchronous_job(self):
    '''
    get synchronous job setting
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_SYNC_JOB)])
    if ret:
        return ret.value == 'Y'

def get_synchronous_skill(self):
    '''
    get synchronous skill setting
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_SYNC_SKILL)])
    if ret:
        return ret.value == 'Y'

def get_synchronous_approval(self):
    '''
    get synchronous approval setting
    '''
    ret = self.env['ir.config_parameter'].search([('key','=',CONST_SETTING_SYNC_APPROVAL)])
    if ret:
        return ret.value == 'Y'

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
    
    def _get_holiday_period_unit(self):
        ret = int(get_holiday_period(self)['unit'])
        return ret

    def _get_holiday_period(self):
        ret = get_holiday_period(self)['period']
        return ret

    def _get_tz(self):
        ret = get_api_key(self)
        print(ret.tz)
        return ret.tz or self._context.get('tz')

    def _get_expense_product(self):
        ret = get_api_key(self)

        return ret.expense_product_id
    
    def _get_expense_period_unit(self):
        ret = int(get_expense_period(self)['unit'])
        return ret

    def _get_expense_period(self):
        ret = get_expense_period(self)['period']
        return ret
    
    def _get_account_analytic(self):
        ret = get_api_key(self)

        return ret.account_analytic_id
    
    def _get_timesheet_period_unit(self):
        ret = int(get_timesheet_period(self)['unit'])
        return ret

    def _get_timesheet_period(self):
        ret = get_timesheet_period(self)['period']
        return ret

    def _get_sync_attendance(self):
        return get_synchronous_attendance(self)

    def _get_sync_holiday(self):
        return get_synchronous_holiday(self)

    def _get_sync_expense(self):
        return get_synchronous_expense(self)

    def _get_sync_timesheet(self):
        return get_synchronous_timesheet(self)

    def _get_sync_job(self):
        return get_synchronous_job(self)

    def _get_sync_skill(self):
        return get_synchronous_job(self)

    def _get_sync_approval(self):
        return get_synchronous_approval(self)

    holiday_status_id = fields.Many2one("hr.leave.type", String="Default Leave Type",default=_get_holiday_status )
    sick_status_id = fields.Many2one("hr.leave.type", String="Sick leave Type",default=_get_sick_status )
    holiday_notify_leave_req = fields.Boolean('Notify if there is not enough allocated leave request', default=_get_holiday_notify_leave_req )
    holiday_notify_leave_req_email = fields.Text('Notified Email', default=_get_holiday_notify_leave_req_email)

    api_key = fields.Char(string="API Key", required=True,default=_get_api_key )
    email = fields.Text('Email', required=True, default=_get_email )
    api_database = fields.Char('API Database',default=lambda s: s.env.cr.dbname)
    api_debug = fields.Boolean('Show debug info',default=_get_debug)

    log_period_unit = fields.Integer('Period unit',default=_get_log_period_unit)
    log_period = fields.Selection([('w','week(s) ago'),
                                   ('m','month(s) ago'),
                                   ('y','year(s) ago'),
                                   ('all','All')],string='Since',default=_get_log_period)
    tz = fields.Selection(_tz_get, string='Timezone', default=_get_tz)
    holiday_period_unit = fields.Integer('Period unit', default=_get_holiday_period_unit)
    holiday_period = fields.Selection([('w','week(s) ago'),
                                        ('m','month(s) ago'),
                                        ('y','year(s) ago'),
                                        ('all', 'All')], string='Since', default=_get_holiday_period)
    expense_product_id = fields.Many2one("product.product", String="Expense product",default=_get_expense_product )
    expense_period_unit = fields.Integer('Period Unit', default=_get_expense_period_unit)
    expense_period = fields.Selection([('w','week(s) ago'),
                                        ('m','month(s) ago'),
                                        ('y','year(s) ago'),
                                        ('all', 'All')], string='Since', default=_get_expense_period)

    account_analytic_id = fields.Many2one('account.analytic.account', string="Account Analytic", default=_get_account_analytic)
    timesheet_period_unit = fields.Integer('Period Unit', default=_get_timesheet_period_unit)
    timesheet_period = fields.Selection([('w','week(s) ago'),
                                        ('m','month(s) ago'),
                                        ('y','year(s) ago'),
                                        ('all', 'All')], string='Since', default=_get_timesheet_period)

    sync_employee = fields.Boolean('Sync Employee', readonly=True, default=True)
    sync_position = fields.Boolean('Sync Position', readonly=True, default=True)
    sync_department = fields.Boolean('Sync Department', readonly=True, default=True)
    sync_customer = fields.Boolean('Sync Customer', readonly=True, default=True)
    sync_attendance = fields.Boolean('Sync Attendance', default=_get_sync_attendance)
    sync_holiday = fields.Boolean('Sync Holiday', default=_get_sync_holiday)
    sync_expense = fields.Boolean('Sync Expense', default=_get_sync_expense)
    sync_timesheet = fields.Boolean('Sync Timesheet', default=_get_sync_timesheet)
    sync_job = fields.Boolean('Sync Job', default=_get_sync_job)
    sync_skill = fields.Boolean('Sync Skill', default=_get_sync_skill)
    sync_approval = fields.Boolean('Sync Approval', default=_get_sync_approval)

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

        if self.sync_holiday:
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_TIMEZONE, self.tz)
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_STATUS_ID, self.holiday_status_id.id)
           self._save_setting(config_pool, CONST_SETTING_SICK_STATUS_ID, self.sick_status_id.id)
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_NOTICE, "Y" if self.holiday_notify_leave_req else "N")
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_NOTICE_EMAIL, self.holiday_notify_leave_req_email)
           
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_PERIOD_UNIT, self.holiday_period_unit)
           self._save_setting(config_pool, CONST_SETTING_HOLIDAY_PERIOD, self.holiday_period)

        if self.sync_attendance:
           self._save_setting(config_pool, CONST_SETTING_LOG_PERIOD_UNIT, self.log_period_unit)
           self._save_setting(config_pool, CONST_SETTING_LOG_PERIOD, self.log_period)

        if self.sync_expense:
           self._save_setting(config_pool, CONST_SETTING_EXPENSE_PRODUCT_ID, self.expense_product_id.id)
           self._save_setting(config_pool, CONST_SETTING_EXPENSE_PERIOD_UNIT, self.expense_period_unit)
           self._save_setting(config_pool, CONST_SETTING_EXPENSE_PERIOD, self.expense_period)

        if self.sync_timesheet:
           self._save_setting(config_pool, CONST_SETTING_TIMESHEET_ACCOUNT_ANALYTIC_ID, self.account_analytic_id.id)
           self._save_setting(config_pool, CONST_SETTING_TIMESHEET_PERIOD_UNIT, self.timesheet_period_unit)
           self._save_setting(config_pool, CONST_SETTING_TIMESHEET_PERIOD, self.timesheet_period)

        self._save_setting(config_pool, CONST_SETTING_SYNC_EMPLOYEE, "Y" if self.sync_employee else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_POSITION, "Y" if self.sync_position else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_DEPARTMENT, "Y" if self.sync_department else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_CUSTOMER, "Y" if self.sync_customer else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_ATTENDANCE, "Y" if self.sync_attendance else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_HOLIDAY, "Y" if self.sync_holiday else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_EXPENSE, "Y" if self.sync_expense else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_TIMESHEET, "Y" if self.sync_timesheet else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_JOB, "Y" if self.sync_job else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_SKILL, "Y" if self.sync_skill else "")
        self._save_setting(config_pool, CONST_SETTING_SYNC_APPROVAL, "Y" if self.sync_approval else "")
