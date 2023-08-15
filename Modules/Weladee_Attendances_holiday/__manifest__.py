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
         'data/feature.xml',
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

email temmplate
- Weladee Attendance: Employee's Leaves Allocation Request not enough

group
- group_weladee_leave_allocation

employee
- field can_request_holiday

leave type
- field weladee_code
- group by weladee
- search by weladee_code

leave
- no create/edit/delete
- remove allocation menu
- remove manager approve menu
- group by weladee

- field daypart
- field weladee_sick
- field weladee_code
- field weladee_id

user
- remove button leave, leave allocate

Time off 
- company holiday
- mytime off 
  - dashboard (hide new time off, allocation request buttons)
- overview (hide new time off, allocation request buttons)
- approvals
  - timeoff (hide new time off, allocation request buttons)

weladee sync form
- add holiday

weladee sync
- add sync holiday and company holiday
- 1 way from weladee to odoo

weladee settings
- field holiday_period
- field holiday_period_unit
- field holiday_status_id
- field sick_status_id
- field holiday_notify_leave_req
- field holiday_notify_leave_req_email
- field tz
- field sync_holiday

change log:
------------------------------------
* 2023-08-11 KPO updated to odoo 16
"""
}
