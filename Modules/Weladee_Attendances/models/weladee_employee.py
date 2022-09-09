# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
import traceback
_logger = logging.getLogger(__name__)
import time

from odoo import osv
from odoo import models, fields, api, _
from datetime import datetime,date, timedelta
from odoo import exceptions

from .grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from . import weladee_settings
from .sync.weladee_base import stub, myrequest, sync_clean_up, sync_message_log 
from .sync.weladee_employee import new_employee_data_gender,new_employee_data_marital, new_employee_data_military, new_employee_data_religion,new_employee_data_religion,new_employee_data_military

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
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    receive_check_notification = fields.Boolean(string="Receive Check Notification", track_visibility='always')
    can_request_holiday = fields.Boolean(string="Can Request Holiday", track_visibility='always')
    hasToFillTimesheet = fields.Boolean(string="Has To Fill Timesheet", track_visibility='always')

    #other 
    employee_code = fields.Char(string='Employee Code', track_visibility='always',copy=False)
    qr_code = fields.Char('QR Code',copy=False)
    employee_team = fields.Char('Team')

    driving_license_number = fields.Char('Driving license number')
    driving_license_place_issue = fields.Char('Driving license issued place')
    driving_license_date_issue = fields.Date('Driving license issued date')
    driving_license_expiration_date = fields.Date('Driving license expired date')

    religion = fields.Selection(selection='_get_religion',string='Religion',default=lambda s: s._get_religion_default())
    military_status = fields.Selection(selection='_get_military',string='Military status',default=lambda s: s._get_military_default())

    resignation_date = fields.Date('Resignation date')
    resignation_reason = fields.Text('Resignation reason')
    probation_due_date = fields.Date('Probation due date')
    timesheet_cost = fields.Float('Timesheet cost')

    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widowed', 'Widower'),
        ('divorced', 'Divorced'),
        ('separated', 'Separated'),
        ('other', 'Other'),
        ('unknownmaritalstatus', 'Unknown')
    ])

    _sql_constraints = [
      ('emp_code_uniq', 'unique(employee_code)', "Employee code can't duplicate !"),
      ('emp_first_last_name_uniq', 'unique(first_name_english,last_name_english)', "Employee name can't duplicate !"),
      ('emp_mail_uniq', 'unique(work_email)', "Employee working email can't duplicate !"),
      ('emp_first_last_name_t_uniq', 'unique(first_name_thai,last_name_thai)', "Employee name can't duplicate !"),
    ]

    @api.model
    def _get_religion_default(self):
        return weladee_pb2.Religion.keys()[0]

    @api.model
    def _get_military_default(self):
        return weladee_pb2.MilitaryStatus.keys()[0]

    @api.model
    def _get_religion(self):
        return [(x, x) for x in weladee_pb2.Religion.keys()]

    @api.model
    def _get_military(self):        
        return [(x, x) for x in weladee_pb2.MilitaryStatus.keys()]

    def _create_in_weladee(self, employee_odoo, vals):
        '''
        create new employee record in weladee
        '''
        ret = self.env['weladee_attendance.synchronous.setting'].get_settings()
        
        if ret.authorization:
            WeladeeData = odoo_pb2.EmployeeOdoo()
            WeladeeData.odoo.odoo_id = employee_odoo.id
            WeladeeData.odoo.odoo_created_on = int(time.time())
            WeladeeData.odoo.odoo_synced_on = int(time.time())

            if "first_name_english" in vals and vals["first_name_english"]:
                WeladeeData.employee.FirstNameEnglish = vals["first_name_english"]
            if "last_name_english" in vals and vals["last_name_english"]:
                WeladeeData.employee.LastNameEnglish = vals["last_name_english"]

            # default from name
            if not "first_name_english" in vals and not "last_name_english" in vals :
               if vals["name"]:
                  defs = vals["name"].split(" ")
                  if len(defs) > 0:                  
                     WeladeeData.employee.FirstNameEnglish = defs[0]
                  if len(defs) > 1:
                    WeladeeData.employee.LastNameEnglish = defs[0]

            if "first_name_thai" in vals:
                WeladeeData.employee.FirstNameThai = vals["first_name_thai"] or ''
            if "last_name_thai" in vals:
                WeladeeData.employee.LastNameThai = vals["last_name_thai"] or ''

            if "nick_name_english" in vals :
                WeladeeData.employee.nickname_english = vals["nick_name_english"] or ''
            if "nick_name_thai" in vals :
                WeladeeData.employee.nickname_thai = vals["nick_name_thai"] or ''

            #2018-05-28 KPO change to employee_code
            if "employee_code" in vals:
                WeladeeData.employee.Code = vals["employee_code"] or ''
            elif "employee_code_hidden" in vals:
                WeladeeData.employee.Code = vals["employee_code_hidden"] or ''

            if "country_id" in vals:                
                c_line_obj = self.env['res.country']
                cdata = c_line_obj.browse( vals["country_id"] )
                if cdata and cdata.id :
                    WeladeeData.employee.Nationality = cdata.code

            #2018-06-07 KPO don't sync note back
            if "work_email" in vals:    
                WeladeeData.employee.email = vals["work_email"] or ''
            
            if "parent_id" in vals :
                manager = self.env['hr.employee'].browse( vals["parent_id"] )
                if manager and manager.weladee_id:
                    WeladeeData.employee.ManagerID = int(manager.weladee_id)

            if "job_id" in vals :    
                positionData = self.env['hr.job'].browse( vals["job_id"] )
                if positionData and positionData.weladee_id :
                    WeladeeData.employee.PositionID = int(positionData.weladee_id)

            if "birthday" in vals:    
                if vals['birthday']:
                   if type(vals['birthday']) is datetime:
                      WeladeeData.employee.Birthday = int(vals["birthday"].timestamp())
                   else: 
                      WeladeeData.employee.Birthday = int(datetime.strptime(vals["birthday"],'%Y-%m-%d').timestamp())

            #language not sync yet
            WeladeeData.employee.lg = "en"
            WeladeeData.employee.Active = vals.get("active",False)
            WeladeeData.employee.receiveCheckNotification = vals.get("receive_check_notification",False)
            WeladeeData.employee.CanRequestHoliday = vals.get("can_request_holiday",False)
            WeladeeData.employee.HasToFillTimesheet = vals.get("hasToFillTimesheet",False)

            #2018-05-28 KPO use field from odoo
            if "passport_id" in vals:
                WeladeeData.employee.PassportNumber = vals["passport_id"] or ''
            if "taxID" in vals:
                WeladeeData.employee.TaxID = vals["taxID"] or ''
            if "identification_id" in vals:
                WeladeeData.employee.NationalID = vals["identification_id"] or ''
            if "image_1920" in vals:
                WeladeeData.employee.photo = vals["image_1920"]

            if "work_phone" in vals:
              if not WeladeeData.employee.Phones:
                 WeladeeData.employee.Phones[:] = [vals['work_phone'] or '']
              else:  
                 WeladeeData.employee.Phones[0] = vals['work_phone'] or ''

            if 'gender' in vals:
                WeladeeData.employee.Gender = new_employee_data_gender(vals['gender']) 

            if 'timesheet_cost' in vals:
                WeladeeData.employee.HourlyCost = vals.get('timesheet_cost', 0)

            if 'driving_license_number' in vals:
                WeladeeData.employee.DrivingLicenseNumber = vals['driving_license_number'] or ''
            if 'driving_license_place_issue' in vals:
                WeladeeData.employee.DrivingLicensePlaceIssue = vals['driving_license_place_issue'] or ''
            if "driving_license_date_issue" in vals:
                if vals['driving_license_date_issue']:
                   if type(vals['driving_license_date_issue']) is datetime:
                      WeladeeData.employee.DrivingLicenseDateIssue = int(vals["driving_license_date_issue"].timestamp())
                   else:
                      WeladeeData.employee.DrivingLicenseDateIssue = int(datetime.strptime(vals["driving_license_date_issue"],'%Y-%m-%d').timestamp())

            if "driving_license_expiration_date" in vals:                
                if vals['driving_license_expiration_date']:
                   if type(vals['driving_license_expiration_date']) is datetime:
                      WeladeeData.employee.DrivingLicenseExpirationDate = int(vals["driving_license_expiration_date"].timestamp())
                   else:
                      WeladeeData.employee.DrivingLicenseExpirationDate = int(datetime.strptime(vals["driving_license_expiration_date"],'%Y-%m-%d').timestamp())

            if "religion" in vals:
                WeladeeData.employee.Religion = new_employee_data_religion( vals['religion'] or '')
            if "marital_status" in vals:
               WeladeeData.employee.MaritalStatus = new_employee_data_marital( vals['marital_status'] or '')
            if "military_status" in vals:
                WeladeeData.employee.MilitaryStatus = new_employee_data_military(vals['military_status'] or '')
            if "resignation_date" in vals:                
                if vals['resignation_date']:
                   if type(vals['resignation_date']) is datetime:
                      WeladeeData.employee.ResignationDate = int(vals["resignation_date"].timestamp())
                   else:
                      WeladeeData.employee.ResignationDate = int(datetime.strptime(vals["resignation_date"],'%Y-%m-%d').timestamp())
            if "probation_due_date" in vals:                
                if vals['probation_due_date']:
                   if type(vals['probation_due_date']) is datetime:
                      WeladeeData.employee.ProbationDueDate = int(vals["probation_due_date"].timestamp())
                   else:
                      WeladeeData.employee.ProbationDueDate = int(datetime.strptime(vals["probation_due_date"],'%Y-%m-%d').timestamp())
            if "resignation_reason" in vals:
                WeladeeData.employee.ResignationReason = vals['resignation_reason'] or ''

            #2018-06-07 KPO don't sync note back
            #2018-06-15 KPO don't sync badge

            try:
              result = stub.AddEmployee(WeladeeData, metadata=ret.authorization)
              _logger.info("Added employee on Weladee : %s" % result.ID)

              #get qrcode back
              towrite={'send2-weladee':False}
              odooRequest = odoo_pb2.OdooRequest()
              odooRequest.odoo_id = employee_odoo.id
              for weladee_emp in stub.GetEmployees(odooRequest, metadata=ret.authorization):
                  if weladee_emp and weladee_emp.employee:
                     towrite['qr_code'] = weladee_emp.employee.QRCode
              towrite['weladee_id'] = result.ID
              employee_odoo.write( towrite )

            except Exception as e:
              _logger.debug("odoo > %s" % vals)
              _logger.error("Error while add employee on Weladee : %s" % e)
              sync_message_log(employee_odoo, 'when hr.employee is created', e)
        else:
          _logger.error("Error while add employee on Weladee : No authroized")

    def _update_in_weladee(self, employee_odoo, vals):
        '''
        create new record in weladee
        '''
        ret = self.env['weladee_attendance.synchronous.setting'].get_settings()
        
        if ret.authorization:
            WeladeeData = False
            WeladeeData_mode = 'create'
            if vals.get('weladee_id', employee_odoo.weladee_id):
                WeladeeData = get_weladee_employee(vals.get('weladee_id',employee_odoo.weladee_id), ret.authorization)
                if WeladeeData:
                   WeladeeData_mode = 'update'                    

            if not WeladeeData:
               WeladeeData = odoo_pb2.EmployeeOdoo()

            WeladeeData.odoo.odoo_id = employee_odoo.id
            WeladeeData.odoo.odoo_created_on = int(time.time())
            WeladeeData.odoo.odoo_synced_on = int(time.time())

            if "first_name_english" in vals:
              WeladeeData.employee.FirstNameEnglish = vals.get("first_name_english", '') or ''
            else:
              WeladeeData.employee.FirstNameEnglish = employee_odoo.first_name_english or ''

            if "last_name_english" in vals :
              WeladeeData.employee.LastNameEnglish = vals.get("last_name_english", '') or ''
            else:
              WeladeeData.employee.LastNameEnglish = employee_odoo.last_name_english or ''

            if "first_name_thai" in vals:
              WeladeeData.employee.FirstNameThai = vals.get("first_name_thai", '') or ''
            else:
              WeladeeData.employee.FirstNameThai = employee_odoo.first_name_thai or ''

            if "last_name_thai" in vals :
              WeladeeData.employee.LastNameThai = vals.get("last_name_thai", '') or ''
            else:
              WeladeeData.employee.LastNameThai = employee_odoo.last_name_thai or ''

            if "nick_name_english" in vals :
              WeladeeData.employee.nickname_english = vals.get("nick_name_english", '') or ''
            else:
              WeladeeData.employee.nickname_english = employee_odoo.nick_name_english or ''

            if "nick_name_thai" in vals :
              WeladeeData.employee.nickname_thai = vals.get("nick_name_thai", '') or ''
            else:
              WeladeeData.employee.nickname_thai = employee_odoo.nick_name_thai or ''

            #2018-06-23 KPO don't update employee code after create
            if "country_id" in vals:
                if vals["country_id"]:
                   countryData = self.env['res.country'].browse( vals["country_id"] )
                   if countryData.id :
                       WeladeeData.employee.Nationality = countryData.code
            else :
                if employee_odoo.country_id.id:
                   WeladeeData.employee.Nationality = employee_odoo.country_id.code or ''

            if "work_email" in vals :
                WeladeeData.employee.email = vals.get("work_email", '')
            else:
                WeladeeData.employee.email = employee_odoo.work_email or ''

            if "parent_id" in vals:
                if vals["parent_id"]:
                   manager = self.env['hr.employee'].browse( vals["parent_id"] )
                   if manager:
                      WeladeeData.employee.ManagerID = int(manager.weladee_id)
            else : 
                if employee_odoo.parent_id:
                    WeladeeData.employee.ManagerID = int(employee_odoo.parent_id.weladee_id)

            if "job_id" in vals:
                if vals["job_id"]:
                   positionData = self.env['hr.job'].browse( vals["job_id"] )
                   if positionData and positionData.weladee_id :
                      WeladeeData.employee.PositionID = int(positionData.weladee_id)
            else :
                if employee_odoo.job_id:
                   WeladeeData.employee.PositionID = int(employee_odoo.job_id.weladee_id)

            if 'birthday' in vals:
                if vals["birthday"]:
                    if type(vals['birthday']) is datetime:
                      WeladeeData.employee.Birthday = int(vals["birthday"].timestamp())
                    else: 
                      WeladeeData.employee.Birthday = int(datetime.strptime(vals["birthday"],'%Y-%m-%d').timestamp())
            else :
                if employee_odoo.birthday:
                   WeladeeData.employee.Birthday = int(datetime.strptime(employee_odoo.birthday.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())

            #language not sync yet

            if "active" in vals :
              WeladeeData.employee.Active = vals["active"]
            else:
              WeladeeData.employee.Active = employee_odoo.active

            if "receive_check_notification" in vals :
              WeladeeData.employee.receiveCheckNotification = vals.get("receive_check_notification",False)
            else :
              WeladeeData.employee.receiveCheckNotification = employee_odoo.receive_check_notification

            if "can_request_holiday" in vals :
              WeladeeData.employee.CanRequestHoliday = vals["can_request_holiday"]
            else :
              WeladeeData.employee.CanRequestHoliday = employee_odoo.can_request_holiday

            if "hasToFillTimesheet" in vals :
              WeladeeData.employee.HasToFillTimesheet = vals["hasToFillTimesheet"]
            else :
              WeladeeData.employee.HasToFillTimesheet = employee_odoo.hasToFillTimesheet

            #2018-05-28 KPO use passport_id from odoo
            if "passport_id" in vals :
              WeladeeData.employee.PassportNumber = vals["passport_id"] or ''
            else :
              WeladeeData.employee.PassportNumber = employee_odoo.passport_id or ''

            if "taxID" in vals :
              WeladeeData.employee.TaxID = vals["taxID"] or ''
            else :
              WeladeeData.employee.TaxID = employee_odoo.taxID or ''

            if "identification_id" in vals :
              WeladeeData.employee.NationalID = vals["identification_id"] or ''
            else :
              WeladeeData.employee.NationalID = employee_odoo.identification_id or ''
            
            if "image_1920" in vals:
                WeladeeData.employee.photo = vals["image_1920"] or ''

            if "work_phone" in vals:
                if len(WeladeeData.employee.Phones) == 0:
                  WeladeeData.employee.Phones[:] = [vals['work_phone'] or '']
                else:  
                  WeladeeData.employee.Phones[0] = vals['work_phone'] or ''

            if 'gender' in vals:
                WeladeeData.employee.Gender = new_employee_data_gender(vals['gender'])   
            else:
                WeladeeData.employee.Gender = new_employee_data_gender(employee_odoo.gender)

            if 'timesheet_cost' in vals:
                WeladeeData.employee.HourlyCost = vals.get('timesheet_cost', 0)
            else:
                WeladeeData.employee.HourlyCost = employee_odoo.timesheet_cost or 0

            if 'driving_license_number' in vals:
                WeladeeData.employee.DrivingLicenseNumber = vals['driving_license_number'] or ''
            else:
                WeladeeData.employee.DrivingLicenseNumber = employee_odoo.driving_license_number or ''

            if 'driving_license_place_issue' in vals:
                WeladeeData.employee.DrivingLicensePlaceIssue = vals['driving_license_place_issue'] or ''
            else:
                WeladeeData.employee.DrivingLicensePlaceIssue = employee_odoo.driving_license_place_issue or ''
                
            if 'driving_license_date_issue' in vals:
                if vals["driving_license_date_issue"]:
                    if type(vals['driving_license_date_issue']) is datetime:
                      WeladeeData.employee.DrivingLicenseDateIssue = int(vals["driving_license_date_issue"].timestamp())
                    else:
                      WeladeeData.employee.DrivingLicenseDateIssue = int(datetime.strptime(vals["driving_license_date_issue"],'%Y-%m-%d').timestamp())
            else :
                if employee_odoo.driving_license_date_issue:
                   WeladeeData.employee.DrivingLicenseDateIssue = int(datetime.strptime(employee_odoo.driving_license_date_issue.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())
                   
            if 'driving_license_expiration_date' in vals:
                if vals["driving_license_expiration_date"]:
                   if type(vals['driving_license_expiration_date']) is datetime:
                      WeladeeData.employee.DrivingLicenseExpirationDate = int(vals["driving_license_expiration_date"].timestamp())
                   else: 
                      WeladeeData.employee.DrivingLicenseExpirationDate = int(datetime.strptime(vals["driving_license_expiration_date"],'%Y-%m-%d').timestamp())
            else :
                if employee_odoo.driving_license_expiration_date:
                   WeladeeData.employee.DrivingLicenseExpirationDate = int(datetime.strptime(employee_odoo.driving_license_expiration_date.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())
                   
            if 'religion' in vals:
                WeladeeData.employee.Religion = new_employee_data_religion( vals['religion'] )
            else:
                WeladeeData.employee.Religion = new_employee_data_religion( employee_odoo.religion )
                
            if 'marital' in vals:
               WeladeeData.employee.MaritalStatus = new_employee_data_marital(vals['marital'])
            else:
               WeladeeData.employee.MaritalStatus = new_employee_data_marital(employee_odoo.marital)

            if 'military_status' in vals:
                WeladeeData.employee.MilitaryStatus = new_employee_data_military(  vals['military_status'] or '')
            else:
                WeladeeData.employee.MilitaryStatus = new_employee_data_military( employee_odoo.military_status)
                
            if "resignation_date" in vals:
                if vals["resignation_date"]:
                   if type(vals['resignation_date']) is datetime:
                      WeladeeData.employee.ResignationDate = int(vals["resignation_date"].timestamp())
                   else:  
                      WeladeeData.employee.ResignationDate = int(datetime.strptime(vals["resignation_date"],'%Y-%m-%d').timestamp())
            else:
                if employee_odoo.resignation_date:
                   WeladeeData.employee.ResignationDate = int(datetime.strptime(employee_odoo.resignation_date.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())

            if "probation_due_date" in vals:
                if vals["probation_due_date"]:
                    if type(vals['probation_due_date']) is datetime:
                      WeladeeData.employee.ProbationDueDate = int(vals["probation_due_date"].timestamp())
                    else:  
                      WeladeeData.employee.ProbationDueDate = int(datetime.strptime(vals["probation_due_date"],'%Y-%m-%d').timestamp())
            else:
                if employee_odoo.probation_due_date:
                   WeladeeData.employee.ProbationDueDate = int(datetime.strptime(employee_odoo.probation_due_date.strftime('%Y-%m-%d'),'%Y-%m-%d').timestamp())

            if "resignation_reason" in vals:
                WeladeeData.employee.ResignationReason = vals['resignation_reason'] or ''
            else:
                WeladeeData.employee.ResignationReason = employee_odoo.resignation_reason or ''

            #2018-05-28 KPO use employee_code
            #2018-06-23 KPO don't update employee code after create
            #2018-06-07 KPO don't sync note back                  
            #2018-06-15 KPO don't sync badge
            #2018-10-29 KPO we don't sync 
            #  department
            #  photo
            # back to weladee                
            if WeladeeData_mode == 'create':
                if employee_odoo.weladee_id:
                    _logger.debug("[employee] odoo > %s" % vals)
                    _logger.debug("[employee] weladee > %s" % employee_odoo)
                    _logger.warning("don't find this id %s on Weladee" % employee_odoo.weladee_id)
                else:
                    try:
                        WeladeeData.employee.lg = "en" 

                        result = stub.AddEmployee(WeladeeData, metadata=ret.authorization)
                        employee_odoo.write({'weladee_id':result.ID,'send2-weladee':False})
                        _logger.info("created employee on Weladee : %s" % result.ID)
                    except Exception as e:
                        _logger.debug("[employee] odoo > %s" % vals)
                        _logger.error("Error while create employee on Weladee : %s" % e)
                        sync_message_log(employee_odoo, 'when hr.employee is updated', e)


            elif WeladeeData_mode == 'update':
                if WeladeeData:
                    try:
                        result = stub.UpdateEmployee(WeladeeData, metadata=ret.authorization)
                        _logger.info("updated employee on Weladee : %s" % result)
                    except Exception as e:
                        _logger.debug("[employee] odoo > %s" % vals)
                        _logger.error("Error while update employee on Weladee : %s" % e)
                        sync_message_log(employee_odoo, 'when hr.employee is updated', e)
                else:
                    # not found this weladee id anymore, probably deleted on weladee., still keep in odoo without sync.
                    _logger.error("Error while update employee on Weladee : can't find this weladee id %s" % employee_odoo.weladee_id)
        else:
          _logger.error("Error while update employee on Weladee : No authroized")

    def clean_up_space(self, vals):
        """
        remove space in employee_code,first_name_english,last_name_english,work_email,first_name_thai,last_name_thai
        when parent id = 0, set to False
        convert country_name to country_id
        """
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
        if vals.get('parent_id', False) == 0:
           vals['parent_id'] = False        
        if vals.get('country_name', False):
           vals['country_id'] = self.env['res.country'].with_context(lang='en_US').search([('name','=', vals['country_name'])]).id
           del vals['country_name']

    @api.model
    def create(self, vals):
        odoovals = sync_clean_up(vals)
        self.clean_up_space(odoovals)
        if not odoovals.get('name',False):
           odoovals['name'] = " ".join([vals['first_name_english'] or '', vals['last_name_english'] or '']) 
        pid = super(weladee_employee,self).create( odoovals )

        # only when user create from odoo, always send
        # record from sync will not send to weladee again
        if not "weladee_id" in vals:
            self._create_in_weladee(pid, vals)

        return pid

    def write(self, vals):
        odoovals = sync_clean_up(vals)
        self.clean_up_space(odoovals)
        ret = False
        for each in self:
            wid = vals.get('weladee_id', each.weladee_id)
            wp = vals.get('weladee_profile', each.weladee_profile)
            if wid and not wp:
               vals['weladee_profile'] = "https://www.weladee.com/employee/%s" % wid

            ret = super(weladee_employee, each).write( odoovals )
        # if don't need to sync when there is weladee-id in vals
        # case we don't need to send to weladee, like just update weladee-id in odoo
        
        if (len(vals.keys) == 1) and ('leave_manager_id' in vals):
           return ret
             
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
        raise exceptions.UserError(_("This employee don't have weladee url."))

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        if not default:
          default = {}
        default['employee_code'] = False      
        default['first_name_english'] = '%s-%s' % (self.first_name_english, len(self.search([('first_name_english','=', self.first_name_english),'|',('active','=',False),('active','=',True)])))
        return super(weladee_employee, self).copy(default)

    @api.depends('weladee_id')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_id:
                record.is_weladee = True
            else:
                record.is_weladee = False
