# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _

class weladee_settings(models.TransientModel):
    _name="weladee_attendance.synchronous.setting"
    _description="Weladee settings"

    '''
    purpose : get default holiday_status_id
    remarks :
    2017-09-26 CKA created
    '''
    def _get_holiday_status(self):
        line_obj = self.env['weladee_attendance.synchronous.setting']
        line_ids = line_obj.search([])
        holiday_status_id = False

        for sId in line_ids:
            dataSet = line_obj.browse(sId.id)
            if dataSet.holiday_status_id :
                holiday_status_id = dataSet.holiday_status_id

        if not holiday_status_id :
            holiday_status_id = self.env['hr.holidays.status'].create({ 'name' : 'Sync From Weladee',
                                                                        'double_validation':False,
                                                                        'limit':True,
                                                                        'categ_id':False,
                                                                        'color_name':'blue'})


        return holiday_status_id

    def _get_api_key(self):
        line_obj = self.env['weladee_attendance.synchronous.setting']
        line_ids = line_obj.search([])
        api_key = False

        for sId in line_ids:
            dataSet = line_obj.browse(sId.id)
            if dataSet.api_key :
                api_key = dataSet.api_key

        return api_key


    holiday_status_id = fields.Many2one("hr.holidays.status", String="Leave Type",required=True,default=_get_holiday_status )
    api_key = fields.Char(string="API Key", required=True,default=_get_api_key )

    def saveBtn(self):
        print("--------Save-----------")

weladee_settings()
