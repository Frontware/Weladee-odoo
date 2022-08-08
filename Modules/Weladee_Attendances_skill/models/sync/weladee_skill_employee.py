# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import skill_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error 
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up

def sync_skill_employee_data(weladee_skill_employee, req):
    data = {}

    odoo_emp = req.employee_obj.search([('weladee_id','=',weladee_skill_employee.EmployeeSkill.EmployeeID),'|',('active','=',True),('active','=',False)], limit=1)
    if not odoo_emp.id:
        # Employee with same weladee-id does not exists.
        raise Exception('Odoo employee not found')
    data['employee_id'] = odoo_emp.id

    odoo_skill_type = req.skill_type_obj.search([('weladee_id','=',weladee_skill_employee.EmployeeSkill.TypeID)], limit=1)
    if not odoo_skill_type.id:
        # Skill type with same weladee-id does not exists.
        raise Exception('Odoo skill type not found')
    data['skill_type_id'] = odoo_skill_type.id

    odoo_skill_level = req.skill_level_obj.search([('weladee_id','=',weladee_skill_employee.EmployeeSkill.LevelID)], limit=1)
    if not odoo_skill_level.id:
        # Skill level with same weladee-id does not exists.
        raise Exception('Odoo skill level not found')
    data['skill_level_id'] = odoo_skill_level.id

    odoo_skill = req.skill_obj.search([('weladee_id','=',weladee_skill_employee.EmployeeSkill.ID)], limit=1)
    if not odoo_skill.id:
        # Skill with same weladee-id does not exists.
        raise Exception('Odoo skill not found')
    data['skill_id'] = odoo_skill.id

    odoo_skill_employee = req.skill_employee_obj.search([('employee_id','=',data['employee_id']),('skill_type_id','=',data['skill_type_id']),('skill_id','=',data['skill_id'])], limit=1)
    if not odoo_skill_employee.id:
        # odoo record does not exist.
        data['res-mode'] = 'create'
    else:
        # odoo record exists.
        data['res-mode'] = 'update'
        data['res-id'] = odoo_skill_employee.id

    return data

def sync_skill_employee(req):
    req.context_sync['stat-skill-employee'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    sync_loginfo(req.context_sync,'[skill employee] updating changes from weladee -> odoo')
    weladee_skill_employee = None

    try:
        for weladee_skill_employee in stub.GetSkillEmployees(weladee_pb2.Empty(), metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-skill-employee'], 1)
            if not weladee_skill_employee:
                sync_logwarn(req.context_sync['stat-skill-employee'], 1)
                sync_logdebug(req.context_sync, "weladee skill employee is empty '%s'" % weladee_skill_employee)
                continue

            odoo_skill_employee = sync_skill_employee_data(weladee_skill_employee, req)

            if odoo_skill_employee and odoo_skill_employee['res-mode'] == 'create':
                newid = req.skill_employee_obj.create(sync_clean_up(odoo_skill_employee))
                sync_logdebug(req.context_sync, "Insert skill employee '%s' to odoo" % odoo_skill_employee)
                sync_stat_create(req.context_sync['stat-skill-employee'], 1)
            elif odoo_skill_employee and odoo_skill_employee['res-mode'] == 'update' and 'res-id' in odoo_skill_employee:
                odoo_id = req.skill_employee_obj.search([('id','=',odoo_skill_employee['res-id'])], limit=1)
                if odoo_id.id:
                    odoo_id.write(sync_clean_up(odoo_skill_employee))
                    sync_logdebug(req.context_sync, "Updated skill employee '%s' to odoo" % odoo_skill_employee)
                    sync_stat_update(req.context_sync['stat-skill-employee'], 1)
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_skill_employee)
                    sync_logerror(req.context_sync, "Not found this odoo skill employee id %s in odoo" % (odoo_skill_employee['res-id']))
                    sync_stat_error(req.context_sync['stat-skill-employee'], 1)

    except Exception as e:
        print(traceback.format_exc())
        if sync_weladee_error(weladee_skill_employee, 'skill employee', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-skill-employee','[skill employee] updating changes from weladee-> odoo')
