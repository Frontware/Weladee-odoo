# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import skill_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error 
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up
from .common import add_translation, base_url, lang_dict

def sync_skill_type_data(weladee_skill_type, req):
    data = {
        'weladee_id':weladee_skill_type.SkillType.ID,
        'weladee_url':base_url + str(weladee_skill_type.SkillType.ID),
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
        # odoo record exists.
        data['res-mode'] = 'update'
        data['res-id'] = odoo_skill_type.id
    
    return data, translation

def sync_skill_type(req):
    req.context_sync['stat-skill-type'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    sync_loginfo(req.context_sync,'[skill type] updating changes from weladee -> odoo')
    weladee_skill_type = None

    try:
        for weladee_skill_type in stub.GetSkillTypes(weladee_pb2.Empty(), metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-skill-type'], 1)
            if not weladee_skill_type:
                sync_logwarn(req.context_sync['stat-skill-type'], 1)
                sync_logdebug(req.context_sync, "weladee skill type is empty '%s'" % weladee_skill_type)
                continue
            
            odoo_skill_type, translation_req = sync_skill_type_data(weladee_skill_type, req)

            if odoo_skill_type and odoo_skill_type['res-mode'] == 'create':
                newid = req.skill_type_obj.create(sync_clean_up(odoo_skill_type))
                if newid and newid.id:
                    # Add translation
                    add_translation(newid.id, 'hr.skill.type', translation_req, req, lang='th_TH')
                    sync_logdebug(req.context_sync, "Insert skill type '%s' to odoo" % odoo_skill_type['name'])
                    sync_stat_create(req.context_sync['stat-skill-type'], 1)
                else:
                    sync_stat_error(req.context_sync['stat-skill-type'], 1)
            elif odoo_skill_type and odoo_skill_type['res-mode'] == 'update' and 'res-id' in odoo_skill_type:
                odoo_id = req.skill_type_obj.search([('id','=',odoo_skill_type['res-id'])], limit=1)
                if odoo_id.id:
                    odoo_id.write(sync_clean_up(odoo_skill_type))
                    # Add translation
                    add_translation(odoo_id.id, 'hr.skill.type', translation_req, req, lang='th_TH')
                    sync_logdebug(req.context_sync, "Updated skill type '%s' to odoo" % odoo_skill_type['name'])
                    sync_stat_update(req.context_sync['stat-skill-type'], 1)
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_skill_type)
                    sync_logerror(req.context_sync, "Not found this odoo skill type id %s of '%s' in odoo" % (odoo_skill_type['res-id'], odoo_skill_type['name']))
                    sync_stat_error(req.context_sync['stat-skill-type'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        if sync_weladee_error(weladee_skill_type, 'skill type', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-skill-type','[skill type] updating changes from weladee-> odoo')

def delete_skill_type(req):
    auditRequest = weladee_pb2.AuditRequest()
    auditRequest.table = weladee_pb2.RecordType.TableSkillType

    try:
        rec = stub.GetDeleted(auditRequest, metadata=req.config.authorization)
        if rec.IDs:
            del_ids = req.skill_type_obj.search([('weladee_id','in',rec.IDs)])
            if del_ids:
                del_ids.unlink()
                sync_logwarn(req.context_sync, 'remove all linked skill types: %s record(s)' % len(del_ids))
    except Exception:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc())
