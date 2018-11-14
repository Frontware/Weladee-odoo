# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import time

from odoo import osv
from odoo import models, fields, api, _
from datetime import datetime,date, timedelta
from odoo import exceptions

from .grpcproto import odoo_pb2
from . import weladee_settings
from .sync.weladee_base import stub, myrequest, sync_clean_up 
from .sync.weladee_employee import new_employee_data_gender

def get_weladee_employee(weladee_id, authorization):
    '''
    get weladee employeeodoo from weladee_id
    '''
    odooRequest = odoo_pb2.OdooRequest()
    try:
        odooRequest.ID = int(weladee_id or '0')
    except:
        return False

    for emp in stub.GetEmployees(odooRequest, metadata=authorization):
        if emp and emp.employee :
           return emp

    return False

class weladee_employee(models.Model):
    _description="synchronous Employee to weladee"
    _inherit = 'hr.employee'

    #contact info
    work_email = fields.Char(required=True, track_visibility='always')

    #position
    job_id = fields.Many2one(required=True, track_visibility='always')

    #citizenship
    country_id = fields.Many2one(string="Nationality (Country)", required=True, track_visibility='always')
    taxID = fields.Char(string="TaxID", track_visibility='always')
    nationalID = fields.Char(string="NationalID", track_visibility='always')

    #main
    name = fields.Char(required=False)
    first_name_english = fields.Char(string="English First Name", track_visibility='always',required=True)
    last_name_english = fields.Char(string="English Last Name", track_visibility='always',required=True)
    first_name_thai = fields.Char(string="Thai First Name", track_visibility='always')
    last_name_thai = fields.Char(string="Thai Last Name", track_visibility='always')
    nick_name_english = fields.Char(string="English Nick Name", track_visibility='always')
    nick_name_thai = fields.Char(string="Thai Nick Name", track_visibility='always')

    #weladee link
    weladee_profile = fields.Char(string="Weladee Url", default="",copy=False)
    weladee_id = fields.Char(string="Weladee ID",copy=False)
    receive_check_notification = fields.Boolean(string="Receive Check Notification", track_visibility='always')
    can_request_holiday = fields.Boolean(string="Can Request Holiday", track_visibility='always')
    hasToFillTimesheet = fields.Boolean(string="Has To Fill Timesheet", track_visibility='always')

    #other 
    employee_code = fields.Char(string='Employee Code', track_visibility='always',copy=False)
    qr_code = fields.Char('QR Code',copy=False)
    employee_team = fields.Char('Team')

    _sql_constraints = [
      ('emp_code_uniq', 'unique(employee_code)', "Employee code can't duplicate !"),
      ('emp_first_last_name_uniq', 'unique(first_name_english,last_name_english)', "Employee name can't duplicate !"),
      ('emp_mail_uniq', 'unique(work_email)', "Employee working email can't duplicate !"),
      ('emp_first_last_name_t_uniq', 'unique(first_name_thai,last_name_thai)', "Employee name can't duplicate !"),
    ]

    def _create_in_weladee(self, employee_odoo, vals):
        '''
        create new employee record in weladee
        '''
        authorization, __, __ = weladee_settings.get_api_key(self)      
        
        if authorization:
            WeladeeData = odoo_pb2.EmployeeOdoo()
            WeladeeData.odoo.odoo_id = employee_odoo.id
            WeladeeData.odoo.odoo_created_on = int(time.time())
            WeladeeData.odoo.odoo_synced_on = int(time.time())

            if "first_name_english" in vals and vals["first_name_english"]:
                WeladeeData.employee.first_name_english = vals["first_name_english"]
            if "last_name_english" in vals and vals["last_name_english"]:
                WeladeeData.employee.last_name_english = vals["last_name_english"]

            # default from name
            if not "first_name_english" in vals and not "last_name_english" in vals :
               if vals["name"]:
                  defs = vals["name"].split(" ")
                  if len(defs) > 0:                  
                     WeladeeData.employee.first_name_english = defs[0]
                  if len(defs) > 1:
                    WeladeeData.employee.last_name_english = defs[0]

            if "first_name_thai" in vals and vals["first_name_thai"]:
                WeladeeData.employee.first_name_thai = vals["first_name_thai"]
            if "last_name_thai" in vals and vals["last_name_thai"]:
                WeladeeData.employee.last_name_thai = vals["last_name_thai"]

            if "nick_name_english" in vals :
                WeladeeData.employee.nickname_english = vals["nick_name_english"] or ''
            if "nick_name_thai" in vals :
                WeladeeData.employee.nickname_thai = vals["nick_name_thai"] or ''

            #2018-05-28 KPO change to employee_code
            if "employee_code" in vals and vals["employee_code"] :
                WeladeeData.employee.code = vals["employee_code"]
            elif "employee_code_hidden" in vals and vals["employee_code_hidden"] :
                WeladeeData.employee.code = vals["employee_code_hidden"]

            if vals["country_id"] :
                c_line_obj = self.env['res.country']
                cdata = c_line_obj.browse( vals["country_id"] )
                if cdata and cdata.name :
                    WeladeeData.employee.Nationality = cdata.name

            #2018-06-07 KPO don't sync note back
            if vals["work_email"] :
                WeladeeData.employee.email = vals["work_email"] or ''
            
            if "parent_id" in vals :
                manager = self.env['hr.employee'].browse( vals["parent_id"] )
                if manager and manager.weladee_id:
                    WeladeeData.employee.managerID = int(manager.weladee_id)

            if vals["job_id"] :
                positionData = self.env['hr.job'].browse( vals["job_id"] )
                if positionData and positionData.weladee_id :
                    WeladeeData.employee.positionid = int(positionData.weladee_id)

            #language not sync yet
            WeladeeData.employee.lg = "en"
            WeladeeData.employee.Active = vals.get("active",False)
            WeladeeData.employee.receiveCheckNotification = vals["receive_check_notification"]
            WeladeeData.employee.canRequestHoliday = vals["can_request_holiday"]
            WeladeeData.employee.hasToFillTimesheet = vals["hasToFillTimesheet"]

            #2018-05-28 KPO use field from odoo
            if vals["passport_id"]:
                WeladeeData.employee.passportNumber = vals["passport_id"]
            if vals["taxID"]:
                WeladeeData.employee.taxID = vals["taxID"]
            if vals["nationalID"]:
                WeladeeData.employee.nationalID = vals["nationalID"]
            if vals["image"]:
                WeladeeData.employee.photo = vals["image"]

            if "work_phone" in vals:
              if not WeladeeData.employee.Phones:
                 WeladeeData.employee.Phones[:] = [vals['work_phone'] or '']
              else:  
                 WeladeeData.employee.Phones[0] = vals['work_phone'] or ''

            if 'gender' in vals:
                WeladeeData.employee.gender = new_employee_data_gender(vals['gender']) 

            try:
              result = stub.AddEmployee(WeladeeData, metadata=authorization)
              _logger.info("Added employee on Weladee : %s" % result.id)

              #get qrcode back
              towrite={'send2-weladee':False}
              odooRequest = odoo_pb2.OdooRequest()
              odooRequest.odoo_id = employee_odoo.id
              for weladee_emp in stub.GetEmployees(odooRequest, metadata=authorization):
                  if weladee_emp and weladee_emp.employee:
                     towrite['qr_code'] = weladee_emp.employee.QRCode

              employee_odoo.write( towrite )

            except Exception as e:
              _logger.debug("odoo > %s" % vals)
              _logger.error("Error while add employee on Weladee : %s" % e)
        else:
          _logger.error("Error while add employee on Weladee : No authroized")

    def _update_in_weladee(self, employee_odoo, vals):
        '''
        create new record in weladee
        '''
        authorization, __, __ = weladee_settings.get_api_key(self)      
        
        if authorization:
            WeladeeData = False
            WeladeeData_mode = 'create'
            if vals.get('weladee_id', employee_odoo.weladee_id):
                WeladeeData = get_weladee_employee(vals.get('weladee_id',employee_odoo.weladee_id), authorization)
                if WeladeeData:
                   WeladeeData_mode = 'update'                    

            if not WeladeeData:
               WeladeeData = odoo_pb2.EmployeeOdoo()

            WeladeeData.odoo.odoo_id = employee_odoo.id
            WeladeeData.odoo.odoo_created_on = int(time.time())
            WeladeeData.odoo.odoo_synced_on = int(time.time())

            if "first_name_english" in vals:
              WeladeeData.employee.first_name_english = vals["first_name_english"] or bytes()
            else:
              WeladeeData.employee.first_name_english = employee_odoo.first_name_english or bytes()

            if "last_name_english" in vals :
              WeladeeData.employee.last_name_english = vals["last_name_english"] or bytes()
            else:
              WeladeeData.employee.last_name_english = employee_odoo.last_name_english or bytes()

            if "first_name_thai" in vals:
              WeladeeData.employee.first_name_thai = vals["first_name_thai"] or bytes()
            else:
              WeladeeData.employee.first_name_thai = employee_odoo.first_name_thai or bytes()

            if "last_name_thai" in vals :
              WeladeeData.employee.last_name_thai = vals["last_name_thai"] or bytes()
            else:
              WeladeeData.employee.last_name_thai = employee_odoo.last_name_thai or bytes()

            if "nick_name_english" in vals :
              WeladeeData.employee.nickname_english = vals["nick_name_english"] or ''
            else:
              WeladeeData.employee.nickname_english = employee_odoo.nick_name_english or ''

            if "nick_name_thai" in vals :
              WeladeeData.employee.nickname_thai = vals["nick_name_thai"] or ''
            else:
              WeladeeData.employee.nickname_thai = employee_odoo.nick_name_thai or ''

            if "active" in vals :
              WeladeeData.employee.Active = vals["active"]
            else:
              WeladeeData.employee.Active = employee_odoo.active

            if "receive_check_notification" in vals :
              WeladeeData.employee.receiveCheckNotification = vals["receive_check_notification"]
            else :
              WeladeeData.employee.receiveCheckNotification = employee_odoo.receive_check_notification

            if "can_request_holiday" in vals :
              WeladeeData.employee.canRequestHoliday = vals["can_request_holiday"]
            else :
              WeladeeData.employee.canRequestHoliday = employee_odoo.can_request_holiday

            if "hasToFillTimesheet" in vals :
              WeladeeData.employee.hasToFillTimesheet = vals["hasToFillTimesheet"]
            else :
              WeladeeData.employee.hasToFillTimesheet = employee_odoo.hasToFillTimesheet

            #2018-05-28 KPO use passport_id from odoo
            if "passport_id" in vals :
              WeladeeData.employee.passportNumber = vals["passport_id"] or ''
            else :
              WeladeeData.employee.passportNumber = employee_odoo.passport_id or ''

            if "taxID" in vals :
              WeladeeData.employee.taxID = vals["taxID"] or ''
            else :
              WeladeeData.employee.taxID = employee_odoo.taxID or ''

            if "nationalID" in vals :
              WeladeeData.employee.nationalID = vals["nationalID"] or ''
            else :
              WeladeeData.employee.nationalID = employee_odoo.nationalID or ''
            
            #2018-05-28 KPO use employee_code
            #2018-06-23 KPO don't update employee code after create
            #2018-06-07 KPO don't sync note back

            if "parent_id" in vals :
                manager = self.env['hr.employee'].browse( vals["parent_id"] )
                if manager:
                    WeladeeData.employee.managerID = int(manager.weladee_id)
                else:
                    WeladeeData.employee.managerID = 0
            else : 
                if employee_odoo.parent_id:
                    WeladeeData.employee.managerID = int(employee_odoo.parent_id.weladee_id)

            if "work_email" in vals :
                WeladeeData.employee.email = vals["work_email"] or ''
            else:
                WeladeeData.employee.email = employee_odoo.work_email or ''

            if "job_id" in vals :
                positionData = self.env['hr.job'].browse( vals["job_id"] )
                if positionData and positionData.weladee_id :
                    WeladeeData.employee.positionid = int(positionData.weladee_id)
            else :
              if employee_odoo.job_id:
                  WeladeeData.employee.positionid = int(employee_odoo.job_id.weladee_id)

            if "country_id" in vals :
                countryData = self.env['res.country'].browse( vals["country_id"] )
                if countryData.id :
                    WeladeeData.employee.Nationality = countryData.name

            if "image" in vals:
                WeladeeData.employee.photo = vals["image"] or ''

            if "work_phone" in vals:
                if len(WeladeeData.employee.Phones) == 0:
                  WeladeeData.employee.Phones[:] = [vals['work_phone'] or '']
                else:  
                  WeladeeData.employee.Phones[0] = vals['work_phone'] or ''

            if 'gender' in vals:
                WeladeeData.employee.gender = new_employee_data_gender(vals['gender'])   
                  
            #2018-10-29 KPO we don't sync 
            #  department
            #  photo
            # back to weladee    
            
            if WeladeeData_mode == 'create':
                if employee_odoo.weladee_id:
                    _logger.debug("[employee] odoo > %s" % vals)
                    _logger.debug("[employee] weladee > %s" % employee_odoo)
                    _logger.warn("don't find this id %s on Weladee" % employee_odoo.weladee_id)
                else:
                    try:
                        WeladeeData.employee.lg = "en" 

                        result = stub.AddEmployee(WeladeeData, metadata=authorization)
                        _logger.info("created employee on Weladee : %s" % result.id)
                    except Exception as e:
                        _logger.debug("[employee] odoo > %s" % vals)
                        _logger.error("Error while create employee on Weladee : %s" % e)

            elif WeladeeData_mode == 'update':
                if WeladeeData:
                    try:
                        result = stub.UpdateEmployee(WeladeeData, metadata=authorization)
                        _logger.info("updated employee on Weladee : %s" % result)
                    except Exception as e:
                        _logger.debug("[employee] odoo > %s" % vals)
                        _logger.error("Error while update employee on Weladee : %s" % e)
                else:
                    # not found this weladee id anymore, probably deleted on weladee., still keep in odoo without sync.
                    _logger.error("Error while update employee on Weladee : can't find this weladee id %s" % employee_odoo.weladee_id)
        else:
          _logger.error("Error while update employee on Weladee : No authroized")

    def clean_up_space(self, vals):
        if "employee_code" in vals and vals["employee_code"]:
           vals["employee_code"] = (vals["employee_code"] or '').strip(' ')
        if "first_name_english" in vals and vals["first_name_english"]:
           vals["first_name_english"] = (vals["first_name_english"] or '').strip(' ')
        if "last_name_english" in vals and vals["last_name_english"]:
           vals["last_name_english"] = (vals["last_name_english"] or '').strip(' ')
        if "work_email" in vals and vals["work_email"]:
           vals["work_email"] = (vals["work_email"] or '').strip(' ')
        if "first_name_thai" in vals and vals["first_name_thai"]:
           vals["first_name_thai"] = (vals["first_name_thai"] or '').strip(' ')
        if "last_name_thai" in vals and vals["last_name_thai"]:
           vals["last_name_thai"] = (vals["last_name_thai"] or '').strip(' ')

    @api.model
    def create(self, vals):
        odoovals = sync_clean_up(vals)
        self.clean_up_space(odoovals)
        if not odoovals.get('name',False):
           odoovals['name'] = " ".join([vals['first_name_english'] or '', vals['last_name_english'] or '']) 
        if "manager" in odoovals: del odoovals['manager']   
        pid = super(weladee_employee,self).create( odoovals )

        # only when user create from odoo, always send
        # record from sync will not send to weladee again
        if not "weladee_id" in vals:
            self._create_in_weladee(pid, vals)

        return pid

    @api.multi
    def write(self, vals):
        odoovals = sync_clean_up(vals)
        self.clean_up_space(odoovals)
        if "manager" in odoovals: del odoovals['manager']
        ret = super(weladee_employee, self).write( odoovals )
        # if don't need to sync when there is weladee-id in vals
        # case we don't need to send to weladee, like just update weladee-id in odoo
        
        # created, updated from odoo, always send
        # when create didn't success sync to weladeec
        # next update, try create again
        if vals.get('send2-weladee',True):
            for each in self:
               if each.weladee_id:
                  self._update_in_weladee(each, vals) 
               else:
                  self._update_in_weladee(each, vals)

        return ret
        
    
    def open_weladee_employee(self):
      '''
      open weladee employee url
      '''
      if self.weladee_profile :
        return {
              'name': _("Weladee Profile"),
              'type': 'ir.actions.act_url',
              'url': self.weladee_profile,
              'target': 'new'
          }
      else :
        raise exceptions.UserError("This employee don't have weladee url.")

    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if not default:
          default = {}
        default['employee_code'] = False      
        default['first_name_english'] = '%s-%s' % (self.first_name_english, len(self.search([('first_name_english','=', self.first_name_english),'|',('active','=',False),('active','=',True)])))
        return super(weladee_employee, self).copy(default)