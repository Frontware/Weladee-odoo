# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances approval module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['fw_approvals', 
             'Weladee_Attendances'],
"data" :[
        "wizards/weladee_attendance_settings.xml",

        'views/fw_approvals_type.xml',
        'views/fw_approvals_request.xml',
],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances approval module
======================================
Module to manage synchronous approval.

It will synchronus approval to odoo.

change log:
------------------------------------
* 2023-08-14 KPO updated to odoo 16
"""
}
