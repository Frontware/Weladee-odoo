# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
class weladee_attendance_param():
      def __init__(self):
          self.config = False
          ''' weladee_attendance.synchronous.setting get_settings'''
          self.context_sync = False
          ''' data for log '''
          self.to_email = False
          ''' flag to send email or not '''

          self.job_obj = False
          ''' hr.job pool'''

          self.department_obj = False
          ''' hr.department pool'''
          self.department_managers = {}
          ''' map of department manager, key: department odoo id/value: weladee managerid '''

          self.country = {}
          ''' map of country list, key: country code/value: country odoo id'''

          self.employee_managers = {}
          ''' map of employee manager, key = employee odoo.id/value: weladee managerid'''
          self.employee_obj = False
          ''' hr.employee pool '''
          self.employee_odoo_weladee_ids = {}
          ''' map emloyee : key = weladee employee id/value = employee odoo id '''
