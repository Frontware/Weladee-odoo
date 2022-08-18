# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import skill_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error 
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up
from .common import add_translation, lang_dict

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
        # odoo record exists.
        data['res-mode'] = 'update'
        data['res-id'] = odoo_skill.id
    
    return data, translation

def sync_skill(req):
    req.context_sync['stat-skill'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    sync_loginfo(req.context_sync,'[skill] updating changes from weladee -> odoo')
    weladee_skill = None

    try:
        for weladee_skill in stub.GetSkills(weladee_pb2.Empty(), metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-skill'], 1)
            if not weladee_skill:
                sync_logwarn(req.context_sync['stat-skill'], 1)
                sync_logdebug(req.context_sync, "weladee skill is empty '%s'" % weladee_skill)
                continue
            
            odoo_skill, translation_req = sync_skill_data(weladee_skill, req)

            if odoo_skill and odoo_skill['res-mode'] == 'create':
                newid = req.skill_obj.create(sync_clean_up(odoo_skill))
                if newid and newid.id:
                    # Add translation
                    add_translation(newid.id, 'hr.skill', translation_req, req, lang='th_TH')
                    sync_logdebug(req.context_sync, "Insert skill level '%s' to odoo" % odoo_skill['name'])
                    sync_stat_create(req.context_sync['stat-skill'], 1)
                else:
                    sync_stat_error(req.context_sync['stat-skill'], 1)
            elif odoo_skill and odoo_skill['res-mode'] == 'update' and 'res-id' in odoo_skill:
                odoo_id = req.skill_obj.search([('id','=',odoo_skill['res-id'])], limit=1)
                if odoo_id.id:
                    odoo_id.write(sync_clean_up(odoo_skill))
                    # Add translation
                    add_translation(odoo_id.id, 'hr.skill', translation_req, req, lang='th_TH')
                    sync_logdebug(req.context_sync, "Updated skill '%s' to odoo" % odoo_skill['name'])
                    sync_stat_update(req.context_sync['stat-skill'], 1)
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_skill)
                    sync_logerror(req.context_sync, "Not found this odoo skill id %s of '%s' in odoo" % (odoo_skill['res-id'], odoo_skill['name']))
                    sync_stat_error(req.context_sync['stat-skill'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        if sync_weladee_error(weladee_skill, 'skill', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-skill','[skill] updating changes from weladee-> odoo')

def delete_skill(req):
    auditRequest = weladee_pb2.AuditRequest()
    auditRequest.table = weladee_pb2.RecordType.TableSkill

    try:
        rec = stub.GetDeleted(auditRequest, metadata=req.config.authorization)
        if rec.IDs:
            del_ids = req.skill_obj.search([('weladee_id','in',rec.IDs)])
            if del_ids:
                del_ids.unlink()
                sync_logwarn(req.context_sync, 'remove all linked skills: %s record(s)' % len(del_ids))
    except Exception:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc())
