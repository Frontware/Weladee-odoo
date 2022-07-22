# -*- coding: utf-8 -*-

import base64
import requests
import subprocess
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import approval_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

_CREATE = 0 # Create new relation
_UPDATE = 1 # Update relation
_CLEAR = 5 # Clear relation
_SET = 6 # Clear and then select relation

base_url = 'https://www.weladee.com/approval/type/'

model_id = 'fw.approvals.type'

lang_dict = {
    'en_US':'english',
    'th_TH':'thai',
}

def sync_approvals_type_data_show_field_date(weladee_approvals_type):
    '''
    convert weladee approvals type show field date to odoo
    '''
    return approval_pb2.ApprovalFieldShow.Name(weladee_approvals_type.Approvaltype.FieldDate).lower()

def sync_approvals_type_data_show_field_period(weladee_approvals_type):
    '''
    convert weladee approvals type show field period to odoo
    '''
    return approval_pb2.ApprovalFieldShow.Name(weladee_approvals_type.Approvaltype.FieldPeriod).lower()

def sync_approvals_type_data_show_field_quantity(weladee_approvals_type):
    '''
    convert weladee approvals type show field quantity to odoo
    '''
    return approval_pb2.ApprovalFieldShow.Name(weladee_approvals_type.Approvaltype.FieldQuantity).lower()

def sync_approvals_type_data_show_field_amount(weladee_approvals_type):
    '''
    convert weladee approvals type show field amount to odoo
    '''
    return approval_pb2.ApprovalFieldShow.Name(weladee_approvals_type.Approvaltype.FieldAmount).lower()

def sync_approvals_type_data_show_field_reference(weladee_approvals_type):
    '''
    convert weladee approvals type show field reference to odoo
    '''
    return approval_pb2.ApprovalFieldShow.Name(weladee_approvals_type.Approvaltype.FieldReference).lower()

def sync_approvals_type_data_show_field_project(weladee_approvals_type):
    '''
    convert weladee approvals type show field project to odoo
    '''
    return approval_pb2.ApprovalFieldShow.Name(weladee_approvals_type.Approvaltype.FieldProject).lower()

def sync_approvals_type_data_show_field_place(weladee_approvals_type):
    '''
    convert weladee approvals type show field place to odoo
    '''
    return approval_pb2.ApprovalFieldShow.Name(weladee_approvals_type.Approvaltype.FieldPlace).lower()

def sync_approvals_type_data_show_field_document(weladee_approvals_type):
    '''
    convert weladee approvals type show field document to odoo
    '''
    return approval_pb2.ApprovalFieldShow.Name(weladee_approvals_type.Approvaltype.FieldDocument).lower()

def sync_approvals_type_data_show_manager_approver(weladee_approvals_type):
    '''
    convert weladee approvals type show field manager approver to odoo
    '''
    return approval_pb2.ApprovalFieldShow.Name(weladee_approvals_type.Approvaltype.ManagerIsApprover).lower()

def sync_approvals_type_data(weladee_approvals_type, req):
    data = {
        'weladee_id':weladee_approvals_type.Approvaltype.ID,
        'weladee_url':base_url + str(weladee_approvals_type.Approvaltype.ID),
        'name':weladee_approvals_type.Approvaltype.NameEnglish,
        # 'code':weladee_approvals_type.Approvaltype.Code,
        # 'sequence':weladee_approvals_type.Approvaltype.Code,
        'active':weladee_approvals_type.Approvaltype.Active,
        'description':weladee_approvals_type.Approvaltype.DescriptionEnglish,
        # 'note':weladee_approvals_type.Approvaltype.Note,
        'field_date':sync_approvals_type_data_show_field_date(weladee_approvals_type),
        'field_period':sync_approvals_type_data_show_field_period(weladee_approvals_type),
        'field_quantity':sync_approvals_type_data_show_field_quantity(weladee_approvals_type),
        'field_amount':sync_approvals_type_data_show_field_amount(weladee_approvals_type),
        'field_reference':sync_approvals_type_data_show_field_reference(weladee_approvals_type),
        'field_project':sync_approvals_type_data_show_field_project(weladee_approvals_type),
        'field_place':sync_approvals_type_data_show_field_place(weladee_approvals_type),
        'field_document':sync_approvals_type_data_show_field_document(weladee_approvals_type),
        'manager_approver':sync_approvals_type_data_show_manager_approver(weladee_approvals_type),
        'minimum_approval':weladee_approvals_type.Approvaltype.Level1MinApproval,
    }

    translation = {
        'thai_name':weladee_approvals_type.Approvaltype.NameThai,
        'thai_description':weladee_approvals_type.Approvaltype.DescriptionThai,
    }

    odoo_approvers_employee = {} # Set of k:v pairs where k is the employee id and v is the approver object
    odoo_approvers_by_level = {} # Set of k:v pairs where k is the name of the field and v is a set of approver's ids
    odoo_approvers_to_update = set() # Set of approver(s) id that has/have either been updated or is/are kept in weladee

    # Check for odoo record with same weladee-id
    odoo_approvals_type = req.approvals_type_obj.search([('weladee_id','=',data['weladee_id']),'|',('active','=',False),('active','=',True)], limit=1)
    if not odoo_approvals_type.id:
        # odoo record does not exist.
        data['res-mode'] = 'create'
    else:
        # odoo record exists.
        data['res-mode'] = 'update'
        data['res-id'] = odoo_approvals_type.id
        for level in filter(lambda x: x.startswith('level_') and x.endswith('_ids'), dir(odoo_approvals_type)):
            level_x_ids = getattr(odoo_approvals_type, level) # Approver's list in level x
            for approver in level_x_ids:
                odoo_approvers_employee[approver.employee_id.id] = approver
                if level not in odoo_approvers_by_level:
                    odoo_approvers_by_level[level] = set()
                odoo_approvers_by_level[level].add(approver.id)
    
    for approver in weladee_approvals_type.Approvaltype.Approvers:
        # Retrieve employee in odoo with the same weladee-id.
        odoo_employee = req.employee_obj.search([("weladee_id","=",approver.EmployeeID),'|',('active','=',False),('active','=',True)], limit=1)
        if not odoo_employee.id:
            # Approver is not employee in odoo.
            continue

        # Create new approver relation command.
        new_approver = (_CREATE, False, {
                'weladee_id':approver.EmployeeID,
                'employee_id':odoo_employee.id,
                'required':approver.Required,
                'level':approver.Level,
            },
        )

        if data['res-mode'] == 'update':
            if odoo_employee.id in odoo_approvers_employee:
                # New approver is an existing approver.
                # Update approver attribute.
                odoo_approvers_to_update.add(odoo_approvers_employee[odoo_employee.id].id)
                val = {}
                if odoo_approvers_employee[odoo_employee.id].required != approver.Required:
                    val['required'] = approver.Required
                if odoo_approvers_employee[odoo_employee.id].level != approver.Level:
                    val['level'] = approver.Level
                if val:
                    # Updated approver
                    new_approver = (_UPDATE, odoo_approvers_employee[odoo_employee.id].id, val)
                    approver.Level = odoo_approvers_employee[odoo_employee.id].level
                else:
                    # Unchanged approver
                    new_approver = ()
        if not new_approver:
            # Approver not updated
            continue

        field_name = 'level_' + str(approver.Level) + '_ids'
        if field_name not in data:
            data[field_name] = []
        data[field_name].append(new_approver)
    
    # Clean up approver relation
    if data['res-mode'] == 'update':
        for level in filter(lambda x: x.startswith('level_') and x.endswith('_ids'), dir(odoo_approvals_type)):
            if level not in data:
                # No new approver and approver not updated.
                if level in odoo_approvers_by_level:
                    # Approver(s) in level L exist(s) in odoo.
                    intersection = odoo_approvers_by_level[level] & odoo_approvers_to_update
                    if not intersection:
                        # Don't keep the approvers.
                        data[level] = [(_CLEAR, False, False)]
                        continue
                    if len(intersection) < len(odoo_approvers_by_level[level]):
                        # Keep some of the approvers, not all.
                        data[level] = [(_SET, False, list(intersection))]
                continue
            # New approver(s) or approver(s) updated.
            if level not in odoo_approvers_by_level:
                # New approver(s) only
                continue
            data[level].append((_SET, False, list(odoo_approvers_by_level[level] & odoo_approvers_to_update)))

    # Download icon and convert icon to base64.
    if weladee_approvals_type.Approvaltype.Icon:
        # Approval type has icon.
        bstderr = False
        try:
            proc = subprocess.Popen(['convert',
                                    '-',
                                    'png:-'],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            r = requests.get(weladee_approvals_type.Approvaltype.Icon)
            content = r.content
            bstdout, bstderr = proc.communicate(input=content)
            iconBase64 = base64.b64encode(bstdout)
            data['image'] = iconBase64
        except requests.Timeout as e:
            sync_logwarn(req.context_sync, 'request: %s' % e)
        except requests.RequestException as e:
            sync_logwarn(req.context_sync, 'request: %s' % e)
        except subprocess.TimeoutExpired as e:
            sync_logwarn(req.context_sync, 'convert: %s' % e)
        except Exception as e:
            sync_logwarn(req.context_sync, 'Error: %s' % (bstderr or e or 'undefined'))
    else:
        # Approval type does not have icon
        data['image'] = False

    return data, translation

def sync_approvals_type(req):
    req.context_sync['stat-approvals-type'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    try:
        sync_loginfo(req.context_sync,'[approvals type] updating changes from weladee -> odoo')
        weladee_approvals_type = None
        for weladee_approvals_type in stub.GetApprovalTypes(weladee_pb2.Empty(), metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-approvals-type'], 1)
            if not weladee_approvals_type:
                sync_logwarn(req.context_sync,'weladee approvals type is empty')
                sync_logdebug(req.context_sync, "weladee approvals type is empty '%s'" % weladee_approvals_type)
                continue

            odoo_approvals_type, translation_req = sync_approvals_type_data(weladee_approvals_type, req)

            if odoo_approvals_type and odoo_approvals_type['res-mode'] == 'create':
                newid = req.approvals_type_obj.create(odoo_approvals_type)
                if newid and newid.id:
                    add_translation(newid.id, translation_req, req, lang='th_TH')
                    sync_stat_create(req.context_sync['stat-approvals-type'], 1)
                else:
                    sync_stat_error(req.context_sync['stat-approvals-type'], 1)
            elif odoo_approvals_type and odoo_approvals_type['res-mode'] == 'update' and 'res-id' in odoo_approvals_type:
                odoo_id = req.approvals_type_obj.search([("id","=",odoo_approvals_type['res-id']),'|',('active','=',False),('active','=',True)], limit=1)
                if odoo_id.id:
                    odoo_id.write(odoo_approvals_type)
                    add_translation(odoo_id.id, translation_req, req, lang='th_TH')
                    sync_stat_update(req.context_sync['stat-approvals-type'], 1)
                else:
                    sync_logerror(req.context_sync, 'Odoo appoval type not found for : %s' % weladee_approvals_type)
                    sync_stat_error(req.context_sync['stat-approvals-type'], 1)

    except Exception as e:
        print(traceback.format_exc())
        if sync_weladee_error(weladee_approvals_type, 'approvals type', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-approvals-type','[approvals type] updating changes from weladee-> odoo')

def add_translation(identifiers, translation_req, req, lang='en_US'):
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
