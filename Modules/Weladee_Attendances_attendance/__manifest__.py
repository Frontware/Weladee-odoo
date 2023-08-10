# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances attendance module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['hr_attendance', 
             'Weladee_Attendances'],
"data" :[
         "security/ir.model.access.csv",
         "wizards/weladee_attendance_settings.xml",

         'views/fw_hr_attendances.xml',
         'views/fw_hr_employee.xml',
         'views/weladee_gate.xml',
],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances attendance module
========================================
Module to manage synchronous attendance.

It will synchronus employee attendance to odoo.

change log:
------------------------------------
* 2023-08-09 KPO updated to odoo 16
"""
}
