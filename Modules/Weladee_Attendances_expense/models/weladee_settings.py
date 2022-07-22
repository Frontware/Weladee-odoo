# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

CONST_SETTING_EXPENSE_PRODUCT_ID = 'weladee-expense_product_id'
CONST_SETTING_EXPENSE_PERIOD = 'weladee-expense_period'
CONST_SETTING_EXPENSE_PERIOD_UNIT = 'weladee-expense_period_unit'

CONST_SETTING_SYNC_EXPENSE = 'weladee-sync-expense'

class weladee_settings_expense(models.TransientModel):
    _inherit="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    @api.model
    def get_sync_expense(self):
        return self._get_params_value(CONST_SETTING_SYNC_EXPENSE) == 'Y'

    @api.model
    def get_expense_period_unit(self):
        return self._get_params_value(CONST_SETTING_EXPENSE_PERIOD_UNIT, number=True, default=1)

    @api.model
    def get_expense_period(self):
        return self._get_params_value(CONST_SETTING_EXPENSE_PERIOD, number=False, default='w')

    @api.model
    def get_expense_product(self):
        return self._get_params_value(CONST_SETTING_EXPENSE_PRODUCT_ID, number=True)

    expense_product_id = fields.Many2one("product.product", String="Expense product",default=get_expense_product )
    expense_period_unit = fields.Integer('Period Unit', default=get_expense_period_unit)
    expense_period = fields.Selection([('w','week(s) ago'),
                                        ('m','month(s) ago'),
                                        ('y','year(s) ago'),
                                        ('all', 'All')], string='Since', default=get_expense_period)

    
    sync_expense = fields.Boolean('Sync Expense', default=get_sync_expense)
    

    @api.model
    def get_settings(self):
        r = super(weladee_settings_expense, self).get_settings()
        r.sync_expense = self.get_sync_expense()
        
        r.expense_period_unit = self.get_expense_period_unit()
        r.expense_period = self.get_expense_period()
        r.expense_product_id = self.get_expense_product()
       
        return r

    def saveBtn(self):
        ret = super(weladee_settings_expense, self).saveBtn()

        config_pool = self.env['ir.config_parameter']
        if self.sync_expense:
           self._save_setting(config_pool, CONST_SETTING_EXPENSE_PRODUCT_ID, self.expense_product_id.id)
           self._save_setting(config_pool, CONST_SETTING_EXPENSE_PERIOD_UNIT, self.expense_period_unit)
           self._save_setting(config_pool, CONST_SETTING_EXPENSE_PERIOD, self.expense_period)

        self._save_setting(config_pool, CONST_SETTING_SYNC_EXPENSE, "Y" if self.sync_expense else "")
        return ret
