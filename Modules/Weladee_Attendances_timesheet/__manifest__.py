# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances timesheet module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['hr_timesheet', 
             'hr_timesheet_attendance',
             'mail',
             'Weladee_Attendances'],
"data" :[
        "wizards/weladee_attendance_settings.xml",

        'views/fw_hr_employee.xml',
        'views/fw_hr_work_type.xml',
        'views/fw_hr_project_project.xml',
        'views/fw_hr_project_task.xml',
        'views/fw_hr_timesheet.xml',
        'views/fw_res_partner.xml',
],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances timesheet module
===================================================================
Module to manage synchronous customer, project, task and timesheet.

It will synchronus customer, project, task and timesheet to odoo.

change log:
------------------------------------
* 2023-08-11 KPO updated to odoo 16
"""
}
