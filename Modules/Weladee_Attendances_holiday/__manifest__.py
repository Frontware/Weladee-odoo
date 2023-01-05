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

    "wizards/weladee_attendance_settings.xml",

    'views/fw_hr_leave_type.xml',
    "views/fw_hr_leave.xml",
    'views/fw_hr_employee.xml',
    "views/weladee_company_holiday.xml",
],
'assets': {
    'web.assets_backend': [
        'Weladee_Attendances_holiday/static/src/xml/*.xml',
    ]
},
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances holiday module
=====================================
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
* 2023-01-04 KPO (6.0) updated to odoo 16.0
"""
}
