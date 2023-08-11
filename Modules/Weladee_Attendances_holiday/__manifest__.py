# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances holiday module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['hr_holidays', 
             'Weladee_Attendances'],
"data" :[
        'security/security.xml',
        'security/ir.model.access.csv',
        "data/emails/weladee_allocate_error.xml",
         "wizards/weladee_attendance_settings.xml",

         'views/fw_hr_leave_type.xml',
         "views/fw_hr_leave.xml",
         'views/fw_hr_employee.xml',
         "views/weladee_company_holiday.xml",
         'views/fw_user_profile.xml',
],
'assets': {
    'web.assets_backend': [
         "Weladee_Attendances_holiday/static/src/xml/holiday.css"
    ],
},
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances holiday module
===================================
Module to manage synchronous Holiday.

It will synchronus employee holidays and company holidays to odoo.

change log:
------------------------------------
* 2023-08-11 KPO updated to odoo 16
"""
}
