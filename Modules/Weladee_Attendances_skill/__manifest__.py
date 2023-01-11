# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances skill module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['hr_skills', 
             'Weladee_Attendances'],
"data" :[
        "wizards/weladee_attendance_settings.xml",

        'views/fw_hr_skill.xml',
        'views/fw_hr_skill_type.xml',
        'views/fw_hr_skill_level.xml',
],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances skill module
===================================
Module to manage synchronous skill.

It will synchronus skill to odoo.

change log:
------------------------------------
* 2023-01-09 KPO (6.0) updated to odoo 16.0
"""
}
