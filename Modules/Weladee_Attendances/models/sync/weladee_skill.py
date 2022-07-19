# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import skill_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error 
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

lang_dict = {
    'en_US':'english',
    'th_TH':'thai',
}

def sync_skill_type_data(weladee_skill_type, req):
    data = {
        'weladee_id':weladee_skill_type.SkillType.ID,
        'name':weladee_skill_type.SkillType.NameEnglish,
    }

    translation = {
        'thai_name':weladee_skill_type.SkillType.NameThai,
    }

    # Check for odoo record with same weladee-id
    odoo_skill_type = req.skill_type_obj.search([('weladee_id','=',data['weladee_id'])], limit=1)
    if not odoo_skill_type.id:
        # odoo record does not exist.
        data['res-mode'] = 'create'
    else:
        # odoo record exists
        data['res-mode'] = 'update'
        data['res-id'] = odoo_skill_type.id
    
    return data, translation

def sync_skill_level(weladee_skill_level, req):
    data = {
        'weladee_id':weladee_skill_level.SkillLevel.ID,
        'name':weladee_skill_level.SkillLevel.NameEnglish,
        'level_progress':weladee_skill_level.SkillLevel.Progress,
    }

    translation = {
        'thai_name':weladee_skill_level.SkillLevel.NameThai,
    }

    odoo_skill_type = req.skill_type_obj.search([('weladee_id','=',weladee_skill_level.SkillLevel.TypeID)])
    if not odoo_skill_type.id:
        # Skill type with same weladee-id does not exists
        raise Exception('Odoo skill type not found')
    data['skill_type_id'] = odoo_skill_type.id

    odoo_skill_level = req.skill_level_obj.search([('weladee_id','=',data['weladee_id'])], limit=1)
    if not odoo_skill_level.id:
        data['res-mode'] = 'create'
    else:
        data['res-mode'] = 'update'
        data['res-id'] = odoo_skill_level.id
    
    return data, translation

def sync_skill_data(weladee_skill, req):
    data = {
        'weladee_id':weladee_skill.Skill.ID,
        'name':weladee_skill.Skill.NameEnglish,
    }

    translation = {
        'thai_name':weladee_skill.Skill.NameThai
    }

    odoo_skill_type = req.skill_type_obj.search([('weladee_id','=',weladee_skill.Skill.TypeID)])
    if not odoo_skill_type.id:
        # Skill type with same weladee-id does not exists.
        raise Exception('Odoo skill type not found')
    data['skill_type_id'] = odoo_skill_type.id

    # Check for odoo record with same weladee-id
    odoo_skill = req.skill_obj.search([('weladee_id','=',data['weladee_id'])], limit=1)
    if not odoo_skill.id:
        # odoo record does not exist.
        data['res-mode'] = 'create'
    else:
        # odoo record exists
        data['res-mode'] = 'update'
        data['res-id'] = odoo_skill.id
    
    return data, translation

def sync_skill_employee_data(weladee_skill_employee, req):
    pass

def sync_skill(req):
    req.context_sync['stat-skill-type'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['stat-skill-level'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['stat-skill'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['stat-skill-employee'] = {'to-sync':0, "create":0, "update": 0, "error":0}

    # Sync skill type
    sync_loginfo(req.context_sync,'[skill type] updating changes from weladee -> odoo')
    weladee_skill_type = None
    try:
        for weladee_skill_type in stub.GetSkillTypes(weladee_pb2.Empty(), metadata=req.config.authorization):
            if not weladee_skill_type:
                sync_logwarn(req.context_sync['stat-skill-type'], 1)
                sync_logdebug(req.context_sync, "weladee skill type is empty '%s'" % weladee_skill_type)
                continue

            try:
                odoo_skill_type, translation_req = sync_skill_type_data(weladee_skill_type, req)
            except Exception as e:
                sync_logerror(req.context_sync, 'Sync skill type %s failed : %s' % (weladee_skill_type, e))
                sync_stat_error(req.context_sync['stat-skill-type'], 1)
                continue

            if odoo_skill_type and odoo_skill_type['res-mode'] == 'create':
                try:
                    newid = req.skill_type_obj.create(odoo_skill_type)
                    if newid and newid.id:
                        # Add translation
                        add_translation(newid.id, 'hr.skill.type', translation_req, req, lang='th_TH')
                        sync_stat_create(req.context_sync['stat-skill-type'], 1)
                    else:
                        sync_stat_error(req.context_sync['stat-skill-type'], 1)
                except Exception as e:
                    print(traceback.format_exc())
                    sync_logerror(req.context_sync, 'Add skill type %s failed : %s' % (weladee_skill_type, e))
                    sync_stat_error(req.context_sync['stat-skill-type'], 1)
            elif odoo_skill_type and odoo_skill_type['res-mode'] == 'update' and 'res-id' in odoo_skill_type:
                odoo_id = req.skill_type_obj.search([('id','=',odoo_skill_type['res-id'])], limit=1)
                if odoo_id.id:
                    try:
                        odoo_id.write(odoo_skill_type)
                        # Add translation
                        add_translation(odoo_id.id, 'hr.skill.type', translation_req, req, lang='th_TH')
                        sync_stat_update(req.context_sync['stat-skill-type'], 1)
                    except Exception as e:
                        print(traceback.format_exc())
                        sync_logerror(req.context_sync, 'Update skill type %s failed : %s' % (weladee_skill_type, e))
                        sync_stat_error(req.context_sync['stat-skill-type'], 1)
                else:
                    sync_logerror(req.context_sync, 'Odoo skill type not found for : %s' % weladee_skill_type)
                    sync_stat_error(req.context_sync['stat-skill-type'], 1)

    except Exception as e:
        print(traceback.format_exc())
        if sync_weladee_error(weladee_skill_type, 'skill type', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-skill-type','[skill type] updating changes from weladee-> odoo')

    # Sync skill level
    sync_loginfo(req.context_sync,'[skill level] updating changes from weladee -> odoo')
    weladee_skill_level = None
    try:
        for weladee_skill_level in stub.GetSkillLevels(weladee_pb2.Empty(), metadata=req.config.authorization):
            if not weladee_skill_level:
                sync_logwarn(req.context_sync['stat-skill-level'], 1)
                sync_logdebug(req.context_sync, "weladee skill level is empty '%s'" % weladee_skill_level)
                continue

            try:
                odoo_skill_level, translation_req = sync_skill_level(weladee_skill_level, req)
            except Exception as e:
                sync_logerror(req.context_sync, 'Sync skill level %s failed : %s' % (weladee_skill_level, e))
                sync_stat_error(req.context_sync['stat-skill-level'], 1)
                continue

            if odoo_skill_level and odoo_skill_level['res-mode'] == 'create':
                try:
                    newid = req.skill_level_obj.create(odoo_skill_level)
                    if newid and newid.id:
                        # Add translation
                        add_translation(newid.id, 'hr.skill.level', translation_req, req, lang='th_TH')
                        sync_stat_create(req.context_sync['stat-skill-level'], 1)
                    else:
                        sync_stat_error(req.context_sync['stat-skill-level'], 1)
                except Exception as e:
                    print(traceback.format_exc())
                    sync_logerror(req.context_sync, 'Add skill type %s failed : %s' % (weladee_skill_level, e))
                    sync_stat_error(req.context_sync['stat-skill-level'], 1)
            elif odoo_skill_level and odoo_skill_level['res-mode'] == 'update' and 'res-id' in odoo_skill_level:
                odoo_id = req.skill_level_obj.search([('id','=',odoo_skill_level['res-id'])], limit=1)
                if odoo_id.id:
                    try:
                        odoo_id.write(odoo_skill_level)
                        # Add translation
                        add_translation(odoo_id.id, 'hr.skill.level', translation_req, req, lang='th_TH')
                        sync_stat_update(req.context_sync['stat-skill-level'], 1)
                    except Exception as e:
                        print(traceback.format_exc())
                        sync_logerror(req.context_sync, 'Update skill %s failed : %s' % (weladee_skill_level, e))
                        sync_stat_error(req.context_sync['stat-skill-level'], 1)
                else:
                    sync_logerror(req.context_sync, 'Odoo skill not found for : %s' % weladee_skill_level)
                    sync_stat_error(req.context_sync['stat-skill-level'], 1)

    except Exception as e:
        print(traceback.format_exc())
        if sync_weladee_error(weladee_skill_level, 'skill level', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-skill-level','[skill level] updating changes from weladee-> odoo')

    # Sync skill
    sync_loginfo(req.context_sync,'[skill] updating changes from weladee -> odoo')
    weladee_skill = None
    try:
        for weladee_skill in stub.GetSkills(weladee_pb2.Empty(), metadata=req.config.authorization):
            if not weladee_skill:
                sync_logwarn(req.context_sync['stat-skill'], 1)
                sync_logdebug(req.context_sync, "weladee skill is empty '%s'" % weladee_skill)
                continue

            try:
                odoo_skill, translation_req = sync_skill_data(weladee_skill, req)
            except Exception as e:
                sync_logerror(req.context_sync, 'Sync skill %s failed : %s' % (weladee_skill, e))
                sync_stat_error(req.context_sync['stat-skill'], 1)
                continue

            if odoo_skill and odoo_skill['res-mode'] == 'create':
                try:
                    newid = req.skill_obj.create(odoo_skill)
                    if newid and newid.id:
                        # Add translation
                        add_translation(newid.id, 'hr.skill', translation_req, req, lang='th_TH')
                        sync_stat_create(req.context_sync['stat-skill'], 1)
                    else:
                        sync_stat_error(req.context_sync['stat-skill'], 1)
                except Exception as e:
                    print(traceback.format_exc())
                    sync_logerror(req.context_sync, 'Add skill type %s failed : %s' % (weladee_skill, e))
                    sync_stat_error(req.context_sync['stat-skill'], 1)
            elif odoo_skill and odoo_skill['res-mode'] == 'update' and 'res-id' in odoo_skill:
                odoo_id = req.skill_obj.search([('id','=',odoo_skill['res-id'])], limit=1)
                if odoo_id.id:
                    try:
                        odoo_id.write(odoo_skill)
                        # Add translation
                        add_translation(odoo_id.id, 'hr.skill', translation_req, req, lang='th_TH')
                        sync_stat_update(req.context_sync['stat-skill'], 1)
                    except Exception as e:
                        print(traceback.format_exc())
                        sync_logerror(req.context_sync, 'Update skill %s failed : %s' % (weladee_skill, e))
                        sync_stat_error(req.context_sync['stat-skill'], 1)
                else:
                    sync_logerror(req.context_sync, 'Odoo skill not found for : %s' % weladee_skill)
                    sync_stat_error(req.context_sync['stat-skill'], 1)

    except Exception as e:
        print(traceback.format_exc())
        if sync_weladee_error(weladee_skill, 'skill', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-skill','[skill] updating changes from weladee-> odoo')

    # TODO: sync GetSkillEmployees
    # Sync skill employee
    sync_loginfo(req.context_sync,'[skill employee] updating changes from weladee -> odoo')
    weladee_skill_employee = None
    # try:
    #     for weladee_skill_employee in stub.GetSkillEmployees(weladee_pb2.Empty(), metadata=req.config.authorization):
    #         if not weladee_skill_employee:
    #             sync_logwarn(req.context_sync['stat-skill-employee'], 1)
    #             sync_logdebug(req.context_sync, "weladee skill employee is empty '%s'" % weladee_skill_employee)
    #             continue

    #         odoo_skill_employee = sync_skill_employee_data(weladee_skill_employee, req)

    #         if odoo_skill_employee and odoo_skill_employee['res-mode'] == 'create':
    #             try:
    #                 newid = req.skill_employee_obj.create(odoo_skill_employee)
    #                 if newid and newid.id:
    #                     sync_stat_create(req.context_sync['stat-skill-employee'], 1)
    #                 else:
    #                     sync_stat_error(req.context_sync['stat-skill-employee'], 1)
    #             except Exception as e:
    #                 print(traceback.format_exc())
    #                 sync_logerror(req.context_sync, 'Add skill employee %s failed : %s' % (weladee_skill_employee, e))
    #                 sync_stat_error(req.context_sync['stat-skill-employee'], 1)
    #         elif odoo_skill_employee and odoo_skill_employee['res-mode'] == 'update' and 'res-id' in odoo_skill_employee:
    #             odoo_id = req.skill_employee_obj.search([('id','=',odoo_skill_employee['res-id'])], limit=1)
    #             if odoo_id.id:
    #                 try:
    #                     odoo_id.write(odoo_skill_employee)
    #                     sync_stat_update(req.context_sync['stat-skill-employee'], 1)
    #                 except Exception as e:
    #                     print(traceback.format_exc())
    #                     sync_logerror(req.context_sync, 'Update skill employee %s failed : %s' % (weladee_skill_employee, e))
    #                     sync_stat_error(req.context_sync['stat-skill-employee'], 1)
    #             else:
    #                 sync_logerror(req.context_sync, 'Odoo skill not found for : %s' % weladee_skill_employee)
    #                 sync_stat_error(req.context_sync['stat-skill-employee'], 1)

    # except Exception as e:
    #     print(traceback.format_exc())
    #     if sync_weladee_error(weladee_skill_employee, 'skill employee', e, req.context_sync):
    #        return
    
    sync_stat_info(req.context_sync,'stat-skill-employee','[skill employee] updating changes from weladee-> odoo')


def add_translation(identifiers, model_id, translation_req, req, lang='en_US'):
    if lang not in lang_dict:
        return
    
    if isinstance(identifiers, int):
        identifiers = [identifiers]
    
    prefix = lang_dict[lang] + '_'
    for field in filter(lambda f: f.startswith(prefix), translation_req):
        field_name = field[len(prefix):]
        name = ','.join([model_id, field_name])
        value = translation_req[field]
        req.translation_obj._set_ids(name, 'model', lang, identifiers, value)
