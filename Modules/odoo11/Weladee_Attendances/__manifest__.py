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
"version" : "4.02",
"author" : "Frontware International",
"category" : "Generic Modules",
"depends" : ['base', 'hr_attendance', 'hr', 'hr_holidays'],
"data" :["weladee_attendance.xml",
         "views/asset_Weladee_Attendances.xml",
         "views/fw_holiday.xml",
         "views/fw_hr_employee.xml"],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""

Module to manage synchronous Employee, Department, Holiday and attendances.

It will synchronus employee, department, position, holidays and import attendances to odoo.

====================================

change log:
------------------------------------
* 2017-07-18 CKA add view synchronous menu For sync Employee, Department, Holiday and attences on Attendances menu
* 2018-05-15 CKA change code for support odoo 11
* 2018-05-16 CKA add event sync odoo to weladee
* 2018-05-17 CKA Sync employee for update on odoo datas, check duplicate check in
* 2018-05-18 CKA add button to open weladee employee
* 2018-05-21 CKA add new event when syn and fix problem when update employee
* 2018-05-22 CKA fixed problem when sync position on odoo to weladee
* 2018-05-23 CKA changed code for sync odoo to weladee
* 2018-05-24 CKA fixed problem when sync, add new fields on employee
                
requirement:
------------------------------------
* none
                
note:
------------------------------------
* none                
"""
}