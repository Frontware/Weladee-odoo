# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, sync_loginfo, sync_logerror 

def sync_holiday(employee_line_obj, managers, authorization):
    pass
'''
#List of Company holiday
print("Company Holiday And Employee holiday")
if True :
    for chol in stub.GetCompanyHolidays(weladee_pb2.Empty(), metadata=authorization):
        if chol :
            if chol.odoo :
                if not chol.odoo.odoo_id :
                    if chol.Holiday :
                        print("----------------------------------")
                        print(chol.Holiday)
                        if chol.Holiday.date :
                            if len( str (chol.Holiday.date ) ) == 8 :
                                dte = str( chol.Holiday.date )
                                fdte = dte[:4] + "-" + dte[4:6] + "-" + dte[6:8]
                                data = { "name" : chol.Holiday.name_english }
                                if chol.Holiday.employeeid :
                                    print("Employee holiday")
                                    data["holiday_status_id"] = holiday_status_id.id
                                    data["holiday_type"] = "employee"
                                    data["date_from"] = fdte
                                    data["date_to"] = fdte
                                    data["message_follower_ids"] = []
                                    data["message_ids"] = []
                                    data["number_of_days_temp"] = 1.0
                                    data["payslip_status"] = False
                                    data["notes"] = "Import from weladee"
                                    data["report_note"] = "Import from weladee"
                                    data["department_id"] = False
                                    #if chol.Holiday.employeeid in wEidTooEid :
                                        #empId = wEidTooEid[ chol.Holiday.employeeid ]
                                    if self.weladeeEmpIdToOdooId( chol.Holiday.employeeid  ) :
                                        empId =  self.weladeeEmpIdToOdooId( chol.Holiday.employeeid  )
                                        data["employee_id"] = empId
                                        dateid = self.env["hr.holidays"].create( data )
                                        print("odoo id : %s" % dateid.id)

                                        newHoliday = odoo_pb2.HolidayOdoo()
                                        newHoliday.odoo.odoo_id = dateid.id
                                        newHoliday.odoo.odoo_created_on = int(time.time())
                                        newHoliday.odoo.odoo_synced_on = int(time.time())

                                        newHoliday.Holiday.id = chol.Holiday.id
                                        newHoliday.Holiday.name_english = chol.Holiday.name_english
                                        newHoliday.Holiday.name_thai = chol.Holiday.name_english
                                        newHoliday.Holiday.date = chol.Holiday.date
                                        newHoliday.Holiday.active = True

                                        newHoliday.Holiday.employeeid = chol.Holiday.employeeid

                                        print(newHoliday)
                                        try:
                                            result = stub.UpdateHoliday(newHoliday, metadata=authorization)
                                            print ("Created Employee holiday" )
                                        except Exception as ee :
                                            print("Error when Create Employee holiday : ",ee)



                                    else :
                                        print("** Don't have employee id **")
                                else :
                                    if True:
                                        print("Company holiday")
                                        holiday_line_obj = self.env['weladee_attendance.company.holidays']
                                        holiday_line_ids = holiday_line_obj.search( [ ('company_holiday_date','=', fdte )] )

                                        if not holiday_line_ids :
                                            data = { 'company_holiday_description' :  chol.Holiday.name_english,
                                                    'company_holiday_active' : True,
                                                    'company_holiday_date' : fdte
                                            }
                                            dateid = self.env["weladee_attendance.company.holidays"].create( data )
                                            print("odoo id : %s" % dateid.id)

                                            newHoliday = odoo_pb2.HolidayOdoo()
                                            newHoliday.odoo.odoo_id = dateid.id
                                            newHoliday.odoo.odoo_created_on = int(time.time())
                                            newHoliday.odoo.odoo_synced_on = int(time.time())

                                            newHoliday.Holiday.id = chol.Holiday.id
                                            newHoliday.Holiday.name_english = chol.Holiday.name_english
                                            newHoliday.Holiday.name_thai = chol.Holiday.name_english
                                            newHoliday.Holiday.date = chol.Holiday.date
                                            newHoliday.Holiday.active = True

                                            newHoliday.Holiday.employeeid = 0

                                            print(newHoliday)
                                            try:
                                                result = stub.UpdateHoliday(newHoliday, metadata=authorization)
                                                print ("Created Company holiday" )
                                            except Exception as ee :
                                                print("Error when Create Company holiday : ",ee)
'''