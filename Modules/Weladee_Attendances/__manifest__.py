# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['base', 'hr'],
"data" :["security/security.xml",
         "security/ir.model.access.csv",   

         "data/emails/weladee_attendance.xml",

         "wizards/weladee_attendance_settings.xml",
         "wizards/weladee_attendance.xml",

         "data/schedule.xml",

         "views/fw_hr_department.xml",
         "views/fw_hr_employee.xml",
         "views/fw_hr_position.xml",

         'views/menu.xml',
],
'assets': {
    'web.assets_backend': [
            'Weladee_Attendances/static/src/css/fw_weladee.css',
    ],
},
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances module
==========================
Module to manage synchronous Employee, Department.

It will synchronus employee, department, position to odoo.

change log:
------------------------------------
* 2023-08-02 KPO updated to odoo 16
* 2021-11-02 KPO updated to odoo 14
* 2019-02-18 KPO allow to resync if 1st connection failed.
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
* protobuf

  pip3 install protobuf

* grpcio

  pip3 install grpcio  

* grpc
  
  install: 
    
  pip3 install --upgrade grpcio==1.7.3

* imagemagick
  
  install:
  
  sudo apt install imagemagick-6.q16 

note:
------------------------------------
* you must have weladee's account to use this module.
""",
'license': 'LGPL-3',
}
