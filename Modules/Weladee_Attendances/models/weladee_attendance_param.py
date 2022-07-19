# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
class weladee_attendance_param():
      def __init__(self):
          self.config = False
          self.context_sync = False
          self.to_email = False

          self.job_obj = False

          self.department_obj = False
          self.department_managers = {}

          self.country = {}

          self.employee_managers = {}
          self.employee_obj = False

          self.log_obj = False
          self.employee_odoo_weladee_ids = {}
          self.period_settings = False

          self.skill_type_obj = False
          self.skill_level_obj = False
          self.skill_obj = False
          self.skill_employee_obj = False

          self.leave_obj = False  
          self.company_holiday_obj = False

          self.customer_obj = False
          self.customer_odoo_weladee_ids = {}

          self.project_obj = False
          self.project_odoo_weladee_ids = {}

          self.task_obj = False
          self.task_odoo_weladee_ids = {}

          self.work_type_obj = False
          self.work_type_odoo_weladee_ids = {}

          self.timesheet_obj = False  

          self.jobads_obj = False  
          self.job_ads_odoo_weladee_ids = {}

          self.jobapp_obj = False  
          self.lang_obj = False

          self.expense_obj = False
          self.expense_sheet_obj = False
          self.attach_obj = False

          self.approvals_type_obj = False
          self.approvals_approver_obj = False
          self.approvals_request_obj = False

          self.translation_obj = False
