# -*- coding: utf-8 -*-
{
"name" : "Weladee attendances job module",
"version" : "6.00",
"author" : "Frontware International",
"category" : "Generic Modules",
'summary': 'Weladee-Odoo attendances\'s module',
"depends" : ['hr_recruitment', 
             'Weladee_Attendances'],
"data" :[
        "security/ir.model.access.csv",           
        "wizards/weladee_attendance_settings.xml",

        'views/fw_hr_job.xml',
        'views/fw_hr_job_applicant.xml',
        'views/fw_weladee_job_ads.xml',
],
'assets': {
  'web.assets_backend': [
      '/Weladee_Attendances_job/static/src/css/fw_jobweladee.css'
  ]
},
"installable" : True,
"active" : False,
"website" : "https://www.weladee.com/",
"description":"""
Weladee attendances job module
====================================
Module to manage synchronous job.

It will synchronus job to odoo.

job positions
- tab job ads

Recruitment
- weladee jobads

change log:
------------------------------------
* 2023-01-18 KPO (6.0) updated to odoo 16.0
"""
}
