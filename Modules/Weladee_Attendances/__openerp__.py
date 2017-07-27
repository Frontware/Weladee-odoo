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
"version" : "4.00",
"author" : "Frontware International",
"category" : "Generic Modules",
"depends" : ['base', 'hr_attendance', 'hr', 'hr_holidays'],
"data" :['weladee_attendance.xml'],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""

Module to manage synchronous Employee, Department, Holiday and attences.
====================================

change log:
------------------------------------
* 2017-07-18 CKA add view synchronous menu For sync Employee, Department, Holiday and attences on Attendances menu
                
requirement:
------------------------------------
* none
                
note:
------------------------------------
* none                
"""
}