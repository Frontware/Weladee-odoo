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
"version" : "5.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['hr_holidays', 
             'Weladee_Attendances'],
"data" :["data/emails/weladee_allocate_error.xml",

         "wizards/weladee_attendance_settings.xml",

         'views/fw_hr_leave_type.xml',
         "views/fw_hr_leave.xml",
         'views/fw_hr_employee.xml',
         "views/weladee_company_holiday.xml",
],
"qweb":[
         "static/src/xml/holiday.xml"
         ],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances holiday module
==========================
Module to manage synchronous Holiday.

It will synchronus employee holidays and company holidas to odoo.
"""
}
