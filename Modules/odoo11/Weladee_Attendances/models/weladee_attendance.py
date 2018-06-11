# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import time
import pytz
from datetime import datetime,date, timedelta

from odoo import osv
from odoo import models, fields, api, _

from .grpcproto import odoo_pb2
from .grpcproto import weladee_pb2

from odoo.addons.Weladee_Attendances.models.weladee_settings import get_synchronous_email 
from odoo.addons.Weladee_Attendances.models.sync.weladee_position import sync_position_data, sync_position 
from odoo.addons.Weladee_Attendances.models.sync.weladee_department import sync_department_data, sync_department
from odoo.addons.Weladee_Attendances.models.sync.weladee_employee import sync_employee_data, sync_employee
from odoo.addons.Weladee_Attendances.models.sync.weladee_manager import sync_manager

class weladee_attendance_working(models.TransientModel):
      _name="weladee_attendance.working"  

      last_run = fields.Datetime('Last run')

class weladee_attendance(models.TransientModel):
    _name="weladee_attendance.synchronous"
    _description="synchronous Employee, Department, Holiday and attendance"

    @api.model
    def start_sync(self):
        '''
            request-date : date user request to sync
            request-synced : text to display in email
            request-error : if error and stop ?
            request-errors : error details
            request-debug : debug info
            request-email : email recipient
        '''
        elapse_start = datetime.today()
        user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        today = elapse_start.astimezone(user_tz)
        context_sync = {
            'request-date':today.strftime('%d/%m/%Y %H:%M'),
            'request-synced':[],
            'request-debug':[],
            'request-error':False,
            'request-errors':[],
            'request-email':get_synchronous_email(self)
        }
        _logger.info("Starting sync..")
        authorization, holiday_status_id = weladee_employee.get_api_key(self)
                
        if not holiday_status_id or not authorization :
            #raise exceptions.UserError('Must to be set Leave Type on Weladee setting')
            print('Must to be set Leave Type on Weladee setting')
            context_sync['request-error'] = True
            context_sync['request-errors'].append('You must setup API Key, Holiday Status on Attendances -> Weladee settings')
        else:

            _logger.info("Start sync...Positions")
            job_obj = self.env['hr.job']    
            sync_position(job_obj, myrequest, authorization, context_sync) 

            if not context_sync['request-error']:
               _logger.info("Start sync...Departments")
               department_obj = self.env['hr.department']    
               sync_department(department_obj, myrequest, authorization, context_sync)

            if not context_sync['request-error']:
               _logger.info("Loading...Countries")
               country = {}
               country_line_ids = self.env['res.country'].search([])
               for cu in country_line_ids:
                   if cu.name :
                      country[ cu.name.lower() ] = cu.id

            if not context_sync['request-error']:
               _logger.info("Start sync...Employee")
               return_managers = {}
               emp_obj = self.env['hr.employee']    
               sync_employee(job_obj, emp_obj, department_obj, country, authorization, return_managers, context_sync)

            if not context_sync['request-error']:
               _logger.info("Start sync...Manager")
               sync_manager(emp_obj, return_managers, authorization, context_sync)

            if not context_sync['request-error']:
               _logger.info("Start sync...Log")
               sync_log(emp_obj, return_managers, authorization, context_sync)

        _logger.info('sending result to %s' % context_sync['request-email'])
        self.send_result_mail(context_sync)
        works = self.env['weladee_attendance.working'].search([])
        if works: works.unlink()

    def send_result_mail(self, ctx):
        '''
        send result email to admin
        '''
        template = self.env.ref('Weladee_Attendances.weladee_attendance_synchronous_cron_mail', raise_if_not_found=False)
        print(template)
        if template:
           template.with_context(ctx).send_mail(self.id)        


    def generators(self, iteratorAttendance):
          for i in iteratorAttendance :
              yield i

    def weladeeEmpIdToOdooId(self, weladeeId) :
        odooid = False
        line_obj = self.env['hr.employee']
        line_ids = line_obj.search([("weladee_id", "=", weladeeId)])
        for cu in line_ids:
             employee_datas = line_obj.browse( cu )
             if employee_datas :
                 odooid = employee_datas.id
        if odooid :
            return odooid.id
        else :
            return odooid

    def manageAttendance(self, wEidTooEid, authorization):
        iteratorAttendance = []
        att_line_obj = self.env['hr.attendance']
        testCount = 0
        lastAttendance = False
        for att in stub.GetNewAttendance(weladee_pb2.Empty(), metadata=authorization):
            #if testCount <= 5 :
                #testCount = testCount + 1
                newAttendance = False
                if att :
                    if att.odoo :
                        attendanceData = False
                        if not att.odoo.odoo_id :
                            newAttendance = True
                        else :
                            attendanceData = att_line_obj.browse( att.odoo.odoo_id )

                        if att.logevent :
                            try:
                                print("------------[ logevent ]----------------")
                                print(att.logevent)
                                print("----------------------------")
                                ac = False
                                if att.logevent.action == "i" :
                                    ac = "sign_in"
                                if att.logevent.action == "o" :
                                    ac = "sign_out"
                                dte = datetime.datetime.fromtimestamp(
                                    att.logevent.timestamp
                                ).strftime('%Y-%m-%d %H:%M:%S')
                                acEid = False
                                #if att.logevent.employeeid in wEidTooEid :
                                    #acEid = wEidTooEid[ att.logevent.employeeid ]
                                if self.weladeeEmpIdToOdooId( att.logevent.employeeid ) :
                                    acEid =  self.weladeeEmpIdToOdooId( att.logevent.employeeid )
                                packet = {"employee_id" : acEid}
                                if acEid :
                                    if newAttendance :                 
                                        aid = False
                                        try :
                                            attendace_odoo_id = False
                                            if att.logevent.action == "i" :
                                                packet["check_in"] = dte
                                                print( packet )
                                                check_dp = self.env['hr.attendance'].search( [ ('employee_id','=', acEid ),('check_in','=', dte ) ] )
                                                if not check_dp :
                                                    try :
                                                        aid = self.env["hr.attendance"].create( packet )
                                                        lastAttendance = aid
                                                        attendace_odoo_id = aid.id
                                                        print ("Created check in : %s" % aid.id)
                                                    except Exception as e:
                                                        print ("Error when create check in. : %s" %(e))
                                                else :
                                                    print ("Check in duplicate.")
                                            else :
                                                if lastAttendance :
                                                    oldAttendance = self.env["hr.attendance"].browse( lastAttendance.id )
                                                    if oldAttendance :
                                                        packet = {"check_in" : oldAttendance.check_in,
                                                                "check_out" : dte
                                                        }
                                                        try :
                                                            print( packet )
                                                            oldAttendance.write( packet )
                                                            attendace_odoo_id = lastAttendance.id
                                                            lastAttendance = False
                                                            print ("Updated check out.")
                                                        except Exception as e:
                                                            print ("Error when fill check out. : %s" %(e) )
                                                else :
                                                    print ("Receive checkout with lastAttendance is False")

                                            if attendace_odoo_id :
                                                print("Update odoo id")
                                                syncLogEvent = odoo_pb2.LogEventOdooSync()
                                                syncLogEvent.odoo.odoo_id = attendace_odoo_id
                                                syncLogEvent.odoo.odoo_created_on = int(time.time())
                                                syncLogEvent.odoo.odoo_synced_on = int(time.time())
                                                syncLogEvent.logid = att.logevent.id
                                                iteratorAttendance.append(syncLogEvent)

                                        except Exception as e:
                                            print("Create log event is failed",e)

                                    else :
                                        if attendanceData :
                                            if att.logevent.action == "i" :
                                                attendanceData["check_in"] = dte
                                            elif att.logevent.action == "o" :
                                                attendanceData["check_out"] = dte
                                            try :
                                                attendanceData.write( attendanceData )
                                                print ("Updated log event on odoo")
                                            except Exception as e:
                                                print("Updated log event is failed",e)

                                            print("Update odoo id")
                                            syncLogEvent = odoo_pb2.LogEventOdooSync()
                                            syncLogEvent.odoo.odoo_id = attendanceData.id
                                            syncLogEvent.odoo.odoo_created_on = int(time.time())
                                            syncLogEvent.odoo.odoo_synced_on = int(time.time())
                                            syncLogEvent.logid = att.logevent.id
                                            iteratorAttendance.append(syncLogEvent)

                            except Exception as e:
                                print("Found problem when create attendance on odoo",e)

        if len( iteratorAttendance ) > 0 :
            #print("CKAA %s" % (iteratorAttendance))
            ge = self.generators(iteratorAttendance)
            a = stub.SyncAttendance( ge , metadata=authorization )
            print(a)
    
weladee_attendance()
