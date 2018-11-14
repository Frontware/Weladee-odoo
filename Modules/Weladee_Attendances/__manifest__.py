# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances module",
"version" : "5.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['base', 'hr', 'hr_attendance', 'hr_holidays', 'hr_timesheet'],
"data" :["security/security.xml",
         "security/ir.model.access.csv",    
         "views/emails/weladee_attendance.xml",
         "views/emails/weladee_allocate_error.xml",
         "views/weladee_attendance_settings.xml",
         "views/weladee_attendance.xml",
         "views/asset_Weladee_Attendances.xml",
         "views/fw_hr_timesheet.xml",
         "views/fw_hr_department.xml",
         "views/fw_hr_attendances.xml",
         "views/weladee_holiday.xml",
         "views/weladee_company_holiday.xml",
         "views/fw_hr_employee.xml"],
"installable" : True,
"active" : False,
"website" : "https://github.com/Frontware/Weladee-odoo",
"description":"""
Weladee attendances module
==========================
Module to manage synchronous Employee, Department, Holiday and attendances.

It will synchronus employee, department, position, holidays and import attendances to odoo.

change log:
------------------------------------
* 2018-11-14 KPO compatible with odoo12
                
requirement:
------------------------------------

* grpc
  
  install: 
    
  pip3 install --upgrade grpcio==1.7.3

* imagemagick
  
  install:
  
  sudo apt install imagemagick-6.q16 

note:
------------------------------------
* you must have weladee's account to use this module.
"""
}