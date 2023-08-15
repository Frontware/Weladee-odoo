# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances OT module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['fw_ot', 
             'Weladee_Attendances'],
"data" :[
        "wizards/weladee_attendance_settings.xml",
        'data/feature.xml',

        'views/fw_ot_type.xml',
        'views/fw_ot_request.xml',
],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances OT module
======================================
Module to manage synchronous OT.

It will synchronus weladee OT to odoo.

change log:
------------------------------------
* 2023-08-14 KPO updated to odoo 16
"""
}
