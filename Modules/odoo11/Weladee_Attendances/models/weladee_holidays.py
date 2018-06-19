# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

import base64
import requests
import time
import webbrowser

from odoo import osv
from odoo import models, fields, api
from datetime import datetime,date, timedelta
from odoo import exceptions

from .grpcproto import odoo_pb2
from .grpcproto import odoo_pb2_grpc
from .grpcproto import weladee_pb2
from . import weladee_grpc
from . import weladee_employee
from .sync.weladee_base import stub, myrequest

class weladee_holidays(models.Model):
  _description="synchronous holidays to weladee"
  _inherit = 'hr.holidays'
  
  @api.multi
  def action_validate( self ):
    mainHol = False
    authorization, holiday_status_id, __ = weladee_employee.get_api_key(self)
    #print("API : %s" % authorization)
    if authorization :
      if True :
        originHolidays = self.env['hr.holidays'].browse( self.id )
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        
        weladeeEmp = {}
        for emp in stub.GetEmployees(weladee_pb2.Empty(), metadata=authorization):
          if emp :
            if emp.odoo :
              if emp.odoo.odoo_id :
                if emp.employee :
                  weladeeEmp[ emp.odoo.odoo_id ] = emp.employee.ID

        if originHolidays :
          if originHolidays.date_from and originHolidays.date_to  :
            df = datetime.strptime( originHolidays.date_from, "%Y-%m-%d %H:%M:%S" )
            dt = datetime.strptime( originHolidays.date_to, "%Y-%m-%d %H:%M:%S" )

            delta = dt - df
            if delta.days + 1 > 1 :
              for i in range(delta.days + 1):
                odooDate = ( df + timedelta(days=i) ).strftime("%Y-%m-%d")
                weladeeDate = ( df + timedelta(days=i) ).strftime("%Y%m%d")
                if i == 0 :
                  if "date_from" in originHolidays :
                    vals = {"date_to" : originHolidays["date_from"],
                            "number_of_days_temp" : 1.0}

                    print(vals)
                    try:
                      mainHol = originHolidays.write( vals )
                      appr = super(weladee_holidays, self).action_validate( )
                      if appr :
                        newHoliday = odoo_pb2.HolidayOdoo()
                        newHoliday.odoo.odoo_id = self.id
                        newHoliday.odoo.odoo_created_on = int(time.time())
                        newHoliday.odoo.odoo_synced_on = int(time.time())

                        newHoliday.Holiday.name_english = originHolidays["name"]
                        newHoliday.Holiday.name_thai = originHolidays["name"]
                        newHoliday.Holiday.active = True

                        weladeeDate = ( df ).strftime("%Y%m%d")
                        newHoliday.Holiday.date = int( weladeeDate )
                        if originHolidays["employee_id"]["id"] in weladeeEmp :
                          newHoliday.Holiday.employeeid = weladeeEmp[ originHolidays["employee_id"]["id"] ]

                          print(newHoliday)
                          try:
                            result = stub.AddHoliday(newHoliday, metadata=authorization)
                            print ("Created Employee holiday" )
                          except Exception as ee :
                            print("Error when Create Employee holiday main : ",ee)
                        else :
                          print(weladeeEmp)
                          print(originHolidays["employee_id"]["id"])
                          print("Don't have emp id on Weladee")

                    except Exception as e:
                      print("Error on main approve : ",e)

                else :
                  vals = {}

                  vals["date_from"] = odooDate
                  vals["date_to"] = odooDate
                  vals["message_follower_ids"] = []
                  vals["message_ids"] = []
                  vals["number_of_days_temp"] = 1.0

                  if "name" in originHolidays :
                    vals["name"] = originHolidays["name"] + "(" + str(i+1) +")"
                  if "holiday_status_id" in originHolidays and "id" in originHolidays["holiday_status_id"] :
                    vals["holiday_status_id"] = originHolidays["holiday_status_id"]["id"]
                  if "employee_id" in originHolidays :
                    vals["employee_id"] = originHolidays["employee_id"]["id"]
                  if "payslip_status" in originHolidays :
                    vals["payslip_status"] = originHolidays["payslip_status"]
                  if "category_id" in originHolidays and "id" in originHolidays["category_id"] :
                    vals["category_id"] = originHolidays["category_id"]["id"]
                  if "type" in originHolidays :
                    vals["type"] = originHolidays["type"]
                  if "report_note" in originHolidays :
                    if originHolidays["report_note"] :
                      vals["notes"] = originHolidays["report_note"] + "\n*****\nSplit leave from " + originHolidays["name"] + "\n*****"
                    else :
                      vals["notes"] = "*****\nSplit leave from " + originHolidays["name"] + "\n*****"
                  else :
                    vals["notes"] = "*****\nSplit leave from " + originHolidays["name"] + "\n*****"

                  vals["report_note"] = vals["notes"]

                  if "department_id" in originHolidays  and "id" in originHolidays["department_id"] :
                    vals["department_id"] = originHolidays["department_id"]["id"]

                  try:
                    lid = self.env['hr.holidays'].create( vals )
                    appr = lid.action_validate( )
                    if appr :
                      newHoliday = odoo_pb2.HolidayOdoo()
                      newHoliday.odoo.odoo_id = lid.id
                      newHoliday.odoo.odoo_created_on = int(time.time())
                      newHoliday.odoo.odoo_synced_on = int(time.time())

                      newHoliday.Holiday.name_english = vals["name"]
                      newHoliday.Holiday.name_thai = vals["name"]
                      newHoliday.Holiday.date = int( weladeeDate )
                      newHoliday.Holiday.active = True

                      if vals["employee_id"] in weladeeEmp :
                        newHoliday.Holiday.employeeid = weladeeEmp[ vals["employee_id"] ]
                        print(newHoliday)
                        try:
                          result = stub.AddHoliday(newHoliday, metadata=authorization)
                          print ("Created Employee holiday" )
                        except Exception as ee :
                          print("Error when Create Employee holiday : ",ee)
                      else :
                        print("Don't have emp id on Weladee")

                  except Exception as e:
                      print("Error on submain approve : ",e)
            else :
              try:
                appr = super(weladee_holidays, self).action_validate( )
                if appr :
                  newHoliday = odoo_pb2.HolidayOdoo()
                  newHoliday.odoo.odoo_id = self.id
                  newHoliday.odoo.odoo_created_on = int(time.time())
                  newHoliday.odoo.odoo_synced_on = int(time.time())

                  newHoliday.Holiday.name_english = originHolidays["name"]
                  newHoliday.Holiday.name_thai = originHolidays["name"]
                  newHoliday.Holiday.active = True

                  weladeeDate = ( df ).strftime("%Y%m%d")
                  newHoliday.Holiday.date = int( weladeeDate )
                  if originHolidays["employee_id"]["id"] in weladeeEmp :
                    newHoliday.Holiday.employeeid = weladeeEmp[ originHolidays["employee_id"]["id"] ]

                    print(newHoliday)
                    try:
                      result = stub.AddHoliday(newHoliday, metadata=authorization)
                      print ("Created Employee holiday" )
                    except Exception as ee :
                      print("Error when Create Employee holiday main : ",ee)
                  else :
                    print(weladeeEmp)
                    print(originHolidays["employee_id"]["id"])
                    print("Don't have emp id on Weladee")

              except Exception as e:
                print("Error on main2 approve : ",e)



        return mainHol
weladee_holidays()