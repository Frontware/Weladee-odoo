# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import time

from odoo import osv
from odoo import models, fields, api
from datetime import datetime,date, timedelta
from odoo import exceptions

from .grpcproto import odoo_pb2
from . import weladee_settings
from .sync.weladee_base import stub, myrequest, sync_clean_up

class weladee_department(models.Model):
    _inherit = 'hr.department'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    code = fields.Char('Code')
    email = fields.Char('Email')
    
    _sql_constraints = [
        ('name_uniq', 'unique(name)', "Department Name can't duplicate !"),
    ]

    @api.model
    def create(self, vals) :
        odoovals = sync_clean_up(vals)
        pid = super(weladee_department,self).create( odoovals )

        # only when user create from odoo, always send
        # record from sync will not send to weladee again
        if not "weladee_id" in vals:
            self._create_in_weladee(pid, vals)

        return pid

    def _create_in_weladee(self, department_odoo, vals):
        '''
        create new record in weladee
        '''
        authorization, __, __ = weladee_settings.get_api_key(self)      
        
        if authorization:
            newDepartment = odoo_pb2.DepartmentOdoo()
            newDepartment.odoo.odoo_id = department_odoo.id
            newDepartment.odoo.odoo_created_on = int(time.time())
            newDepartment.odoo.odoo_synced_on = int(time.time())

            newDepartment.department.name_english = vals["name"]
            newDepartment.department.name_thai = vals["name"]
            newDepartment.department.code = vals["code"]
            newDepartment.department.email = vals["email"]
            newDepartment.department.active = True

            if "manager_id" in vals:
                sel_man = self.env['hr.employee'].search([('id','=',vals['manager_id'])])
                if sel_man.id and sel_man.weladee_id:
                   newDepartment.department.managerID= int(sel_man.weladee_id)

            try:
              result = stub.AddDepartment(newDepartment, metadata=authorization)
              _logger.info("Added department on Weladee : %s" % result.id)
            except Exception as e:
              _logger.debug("odoo > %s" % vals)
              _logger.error("weladee > %s" % newDepartment)
              _logger.error("Error while add department on Weladee : %s" % e)
        else:
          _logger.error("Error while add department on Weladee : No authroized")

    def _update_in_weladee(self, department_odoo, vals):
        '''
        create new record in weladee
        '''
        authorization, __, __ = weladee_settings.get_api_key(self)      
        
        if authorization:
            newDepartment = False
            newDepartment_mode = 'create'
            odooRequest = odoo_pb2.OdooRequest()
            odooRequest.ID = int(department_odoo.weladee_id or '0')
            for weladee_department in stub.GetDepartments(odooRequest, metadata=authorization):
                if weladee_department and weladee_department.department and weladee_department.department.ID > 0 and weladee_department.department.ID == int(department_odoo.weladee_id or '0'):
                   newDepartment = weladee_department
                   newDepartment_mode = 'update'                    

            if not newDepartment:
               newDepartment = odoo_pb2.DepartmentOdoo()  

            newDepartment.odoo.odoo_id = department_odoo.id
            newDepartment.odoo.odoo_created_on = int(time.time())
            newDepartment.odoo.odoo_synced_on = int(time.time())

            if 'name' in vals:
                newDepartment.department.name_english = vals["name"]
            else:
                newDepartment.department.name_english = department_odoo.name

            if 'code' in vals:
                newDepartment.department.code = vals["code"]
            else:
                newDepartment.department.code = department_odoo.code

            if 'email' in vals:
                newDepartment.department.email = vals["email"]
            else:
                newDepartment.department.email = department_odoo.email

            if 'active' in vals:
              newDepartment.department.active = vals['active']
            else:
              newDepartment.department.active = department_odoo.active

            if "manager_id" in vals:
                sel_man = self.env['hr.employee'].search([('id','=',vals['manager_id'])])
                if sel_man.id and sel_man.weladee_id:
                   newDepartment.department.managerID = int(sel_man.weladee_id)
            else:
                if department_odoo.manager_id.weladee_id:
                    newDepartment.department.managerID = int(department_odoo.manager_id.weladee_id)
            
            if newDepartment_mode == 'create':
                if department_odoo.weladee_id:
                    _logger.debug("[department] odoo > %s" % vals)
                    _logger.warn("don't find this id on Weladee : %s" % e)
                else:
                    try:
                        newDepartment.department.active = True
                        newDepartment.department.name_thai = newDepartment.department.name_english

                        result = stub.AddDepartment(newDepartment, metadata=authorization)
                        _logger.info("created department on Weladee : %s" % result.id)
                    except Exception as e:
                        _logger.debug("[department] odoo > %s" % vals)
                        _logger.error("Error while create department on Weladee : %s" % e)

            elif newDepartment_mode == 'update':
                if newDepartment:
                    try:
                        result = stub.UpdateDepartment(newDepartment, metadata=authorization)
                        _logger.info("updated department on Weladee : %s" % result)
                    except Exception as e:
                        #print("[department] odoo > %s" % vals)
                        #print("[department] weladee > %s" % newDepartment)
                        _logger.error("weladee > %s" % newDepartment)
                        _logger.error("Error while update department on Weladee : %s" % e)
                else:
                    # not found this weladee id anymore, probably deleted on weladee., still keep in odoo without sync.
                    _logger.error("Error while update department on Weladee : can't find this weladee id %s" % department_odoo.weladee_id)
        else:
          _logger.error("Error while update department on Weladee : No authroized")

    @api.multi
    def write(self, vals):
        odoovals = sync_clean_up(vals)
        ret = super(weladee_department, self).write( odoovals )
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