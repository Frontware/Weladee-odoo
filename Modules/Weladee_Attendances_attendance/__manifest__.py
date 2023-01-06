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
         "wizards/weladee_attendance_settings.xml",

         'views/fw_hr_attendances.xml',
         'views/fw_hr_employee.xml',
],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances attendance module
========================================
Module to manage synchronous attendance.

It will synchronus employee attendance to odoo.

employee
- field receive_check_notification
- search, group by weladeeid

Attendances
- hide kiosk mode
- hide my attendances
- remove create,edit,delete

change log:
------------------------------------
* 2023-01-06 KPO (6.0) updated to odoo 16.0
"""
}
