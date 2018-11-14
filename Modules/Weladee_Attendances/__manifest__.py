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
         'views/weladee_holiday_status.xml',
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
* 2018-11-14 KPO allow to sync with multiple leave type
* 2018-06-12 KPO fixed sync
* 2017-07-18 CKA add view synchronous menu For sync Employee, Department, Holiday and attences on Attendances menu
* 2018-05-15 CKA change code for support odoo 11
* 2018-05-16 CKA add event sync odoo to weladee
* 2018-05-17 CKA Sync employee for update on odoo datas, check duplicate check in
* 2018-05-18 CKA add button to open weladee employee
* 2018-05-21 CKA add new event when syn and fix problem when update employee
* 2018-05-22 CKA fixed problem when sync position on odoo to weladee
* 2018-05-23 CKA changed code for sync odoo to weladee
* 2018-05-24 CKA fixed problem when sync, add new fields on employee
* 2018-05-25 CKA add new fields for sync
                
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