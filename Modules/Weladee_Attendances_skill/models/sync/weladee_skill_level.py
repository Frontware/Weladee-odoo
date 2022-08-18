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

def sync_skill_level_data(weladee_skill_level, req):
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
        # odoo record does not exist.
        data['res-mode'] = 'create'
    else:
        # odoo record exists.
        data['res-mode'] = 'update'
        data['res-id'] = odoo_skill_level.id
    
    return data, translation

def sync_skill_level(req):
    req.context_sync['stat-skill-level'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    sync_loginfo(req.context_sync,'[skill level] updating changes from weladee -> odoo')
    weladee_skill_level = None

    try:
        for weladee_skill_level in stub.GetSkillLevels(weladee_pb2.Empty(), metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-skill-level'], 1)
            if not weladee_skill_level:
                sync_logwarn(req.context_sync['stat-skill-level'], 1)
                sync_logdebug(req.context_sync, "weladee skill level is empty '%s'" % weladee_skill_level)
                continue
            
            odoo_skill_level, translation_req = sync_skill_level_data(weladee_skill_level, req)

            if odoo_skill_level and odoo_skill_level['res-mode'] == 'create':
                newid = req.skill_level_obj.create(sync_clean_up(odoo_skill_level))
                if newid and newid.id:
                    # Add translation
                    add_translation(newid.id, 'hr.skill.level', translation_req, req, lang='th_TH')
                    sync_logdebug(req.context_sync, "Insert skill level '%s' to odoo" % odoo_skill_level['name'])
                    sync_stat_create(req.context_sync['stat-skill-level'], 1)
                else:
                    sync_stat_error(req.context_sync['stat-skill-level'], 1)
            elif odoo_skill_level and odoo_skill_level['res-mode'] == 'update' and 'res-id' in odoo_skill_level:
                odoo_id = req.skill_level_obj.search([('id','=',odoo_skill_level['res-id'])], limit=1)
                if odoo_id.id:
                    odoo_id.write(sync_clean_up(odoo_skill_level))
                    # Add translation
                    add_translation(odoo_id.id, 'hr.skill.level', translation_req, req, lang='th_TH')
                    sync_logdebug(req.context_sync, "Updated skill level '%s' to odoo" % odoo_skill_level['name'])
                    sync_stat_update(req.context_sync['stat-skill-level'], 1)
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_skill_level)
                    sync_logerror(req.context_sync, "Not found this odoo skill level id %s of '%s' in odoo" % (odoo_skill_level['res-id'], odoo_skill_level['name']))
                    sync_stat_error(req.context_sync['stat-skill-level'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        if sync_weladee_error(weladee_skill_level, 'skill level', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-skill-level','[skill level] updating changes from weladee-> odoo')

def delete_skill_level(req):
    auditRequest = weladee_pb2.AuditRequest()
    auditRequest.table = weladee_pb2.RecordType.TableSkillLevel

    try:
        rec = stub.GetDeleted(auditRequest, metadata=req.config.authorization)
        if rec.IDs:
            del_ids = req.skill_level_obj.search([('weladee_id','in',rec.IDs)])
            if del_ids:
                del_ids.unlink()
                sync_logwarn(req.context_sync, 'remove all linked skill levels: %s record(s)' % len(del_ids))
    except Exception:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc())
