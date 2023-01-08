##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-Now Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
"name" : "Weladee attendances module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['base', 'hr', 'web'],
"data" :["security/security.xml",
         "security/ir.model.access.csv",   

         "data/emails/weladee_attendance.xml",

         "wizards/weladee_attendance_settings.xml",
         "wizards/weladee_attendance.xml",

         "data/templates/asset_Weladee_Attendances.xml",
         "data/schedule.xml",

         "views/fw_hr_department.xml",
         "views/fw_hr_employee.xml",
         "views/fw_hr_position.xml",

         'views/menu.xml',
],
'assets': {
  'web.assets_backend': [
      'Weladee_Attendances/static/src/css/fw_weladee.css'
  ]
},
'external_dependencies': {
  'python': ['protobuf', 'grpcio']
},
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances module
==========================
Module to manage synchronous Employee, Department.

It will synchronus employee, department, position to odoo.

Weladee
- Weladee settings
- Weladee Synchronization

Email template
- Weladee Attendance: Synchronization task
- Weladee Attendance: Synchronization task (debug)

Schedule
- Weladee Attendance: Synchronous task

Employee
- field work_email
- field job_id

- field country_id
- field taxID

- field name (set mandatory)
- field first_name_english
- field last_name_english
- field first_name_thai 
- field last_name_thai
- field nick_name_english
- field nick_name_thai

- field weladee_profile
- field weladee_id
- field is_weladee
- field receive_check_notification
- field can_request_holiday
- field hasToFillTimesheet

- field employee_code
- field qr_code
- field employee_team

- field driving_license_number
- field driving_license_place_issue
- field driving_license_date_issue
- field driving_license_expiration_date

- field religion
- field military_status

- field resignation_date
- field resignation_reason
- field probation_due_date
- field timesheet_cost

- field marital

- first + last name eng. can't duplicate
- first + last name thai can't duplicate
- work_email can't duplicate
- employee_code can't duplicate

- search by weladee
- group by weladee
- weladee button link

department
- name can't duplicate
- field code
- field email

- search by weladee
- group by weladee
- weladee button link

position
- name can't duplicate

- search by weladee
- group by weladee
- weladee button link

change log:
------------------------------------
* 2022-12-28 KPO (6.0) updated to odoo 16.0
* 2021-11-02 KPO updated to odoo14
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

* imagemagick
  
  install:
  
  sudo apt install imagemagick-6.q16 

note:
------------------------------------
* you must have weladee's account to use this module.
"""
}
