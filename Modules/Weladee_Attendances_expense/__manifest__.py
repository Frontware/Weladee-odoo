# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances expense module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['hr_expense', 
             'Weladee_Attendances'],
"data" :["security/ir.model.access.csv",   
        "wizards/weladee_attendance_settings.xml",
        'data/feature.xml',
        'views/fw_hr_expense.xml',
        'views/fw_expense_type.xml',
],
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances expense module
=====================================
Module to manage synchronous expense.

It will synchronus expense to odoo.

expense
- field request_amount
- field receipt_file_name
- field receipt
- field expense_type_id
- field refuse_reason

expenses / Configuration
- weladee expense type

change log:
------------------------------------
* 2023-08-10 KPO updated to odoo 16
"""
}
