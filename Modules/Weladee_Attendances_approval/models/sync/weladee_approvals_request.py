# -*- coding: utf-8 -*-

import base64
import datetime
from dateutil.relativedelta import relativedelta
import requests
import subprocess
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import approval_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

_CREATE = 0 # Create new relation
_UPDATE = 1 # Update relation
_CLEAR = 5 # Clear relation
_SET = 6 # Clear and then select relation

base_url = 'https://www.weladee.com/approval/req/'

model_id = 'fw.approvals.request'

def sync_approvals_request_data_request_status(weladee_approvals_request):
    '''
    convert weladee approvals request status to odoo
    '''
    status = approval_pb2.ApprovalStatus.Name(weladee_approvals_request.request.Status).lower()

    if status == 'approvalnew':
        return 'submitted'
    elif status == 'approvalrejected':
        return 'refused'
    elif status == 'approvalcancelled':
        return 'canceled'
    elif status == 'approvalapproved':
        return 'approved_3'
    elif status == 'approvallevel1approved':
        return 'approved_1'
    elif status == 'approvallevel2approved':
        return 'approved_2'

    return None

def sync_approvals_request_data_answer_approved(weladee_approvals_request_response):
    '''
    convert weladee approvals request answer approved to odoo
    '''
    status = approval_pb2.ApprovalResponse.Name(weladee_approvals_request_response.Answer).lower()

    return status == 'responseapproved'

def sync_approvals_request_data_answer_rejected(weladee_approvals_request_response):
    '''
    convert weladee approvals request answer rejected to odoo
    '''
    status = approval_pb2.ApprovalResponse.Name(weladee_approvals_request_response.Answer).lower()

    return status == 'responserejected'

def sync_approvals_request_data(weladee_approvals_request, req):
    data = {
        'weladee_id':weladee_approvals_request.request.ID,
        'weladee_url':base_url + str(weladee_approvals_request.request.ID),
    }

    odoo_approvers_by_level = {} # Set of k:v pairs where k is the name of the field and v is a set of approver's ids
    odoo_approvers_to_update = {} # Set of k:v pairs where k is the name of the field and v is a set of approver's ids (subset of odoo_approvers_by_level)

    # Check for odoo approval type with same weladee-id.
    odoo_approvals_type = req.approvals_type_obj.search([("weladee_id","=",weladee_approvals_request.request.TypeID),'|',('active','=',False),('active','=',True)], limit=1)
    if not odoo_approvals_type.id:
        # Approval type with same weladee-id does not exists.
        return
    data['type'] = odoo_approvals_type.id
    data['name'] = odoo_approvals_type.name
    data['date_confirmed'] = datetime.datetime.fromtimestamp(weladee_approvals_request.request.CreatedOn)

    # Retrieve employee in odoo with the same weladee-id.
    odoo_employee = req.employee_obj.search([("weladee_id","=",weladee_approvals_request.request.EmployeeID),'|',('active','=',False),('active','=',True)], limit=1)
    if not odoo_employee.id:
        return
    data['owner_request'] = odoo_employee.id

    data['note'] = 'Created by %s' % weladee_approvals_request.request.CreatedByName

    # Link weladee project and odoo project.
    if weladee_approvals_request.request.ProjectID:
        odoo_project = req.project_obj.search([("weladee_id","=",weladee_approvals_request.request.ProjectID),'|',('active','=',False),('active','=',True)], limit=1)
        if not odoo_project.id:
            return
        data['project'] = odoo_project.id

    data['description'] = weladee_approvals_request.request.Description

    if odoo_approvals_type.field_place != 'none':
        data['place'] = weladee_approvals_request.request.Place
    if odoo_approvals_type.field_period != 'none':
        data['date_start'] = datetime.datetime.fromtimestamp(weladee_approvals_request.request.PeriodFrom)
        data['date_end'] = datetime.datetime.fromtimestamp(weladee_approvals_request.request.PeriodTo)
    if odoo_approvals_type.field_amount != 'none':
        data['amount'] = weladee_approvals_request.request.Amount
    if odoo_approvals_type.field_quantity != 'none':
        data['quantity'] = weladee_approvals_request.request.Quantity
    if odoo_approvals_type.field_date != 'none':
        data['date'] = datetime.datetime.fromtimestamp(weladee_approvals_request.request.Date).strftime('%Y-%m-%d')
    if odoo_approvals_type.field_reference != 'none':
        data['reference'] = weladee_approvals_request.request.Reference
    
    data['state'] = sync_approvals_request_data_request_status(weladee_approvals_request)
    
    # Check for odoo record with same weladee-id
    odoo_approvals_request = req.approvals_request_obj.search([('weladee_id','=',data['weladee_id']),'|',('active','=',False),('active','=',True)], limit=1)
    if not odoo_approvals_request.id:
        # odoo record does not exist.
        data['res-mode'] = 'create'
    else:
        # odoo record exists.
        data['res-mode'] = 'update'
        data['res-id'] = odoo_approvals_request.id
        for level in filter(lambda x: x.startswith('approvers_'), dir(odoo_approvals_request)):
            approvers_x = getattr(odoo_approvals_request, level)
            for approver in approvers_x:
                if level not in odoo_approvers_by_level:
                    odoo_approvers_by_level[level] = set()
                odoo_approvers_by_level[level].add(approver.id)
    
    for response in weladee_approvals_request.request.Responses:
        # Retrieve approver from approval type in odoo with the same weladee-id.
        odoo_approver_type = req.approvals_type_approver_obj.search([('approval_type_id','=',odoo_approvals_type.id),("weladee_id","=",response.EmployeeID)], limit=1)
        if not odoo_approver_type.id:
            # Approver is not in odoo.
            continue

        if response.RefuseReason:
            data['text_text'] = response.RefuseReason

        vals = {
            'employee_id':odoo_approver_type.employee_id.id,
            'required':odoo_approver_type.required,
            'level':odoo_approver_type.level,
            'status':sync_approvals_request_data_answer_approved(response),
            'refuse':sync_approvals_request_data_answer_rejected(response),
        }

        if response.Timestamp:
            vals['timestamp'] = datetime.datetime.fromtimestamp(response.Timestamp)

        # Create new approver relation command.
        new_approver = (_CREATE, False, vals)

        # Retrieve approver related to the request id.
        odoo_approver = getattr(req, 'approvals_approver_' + str(odoo_approver_type.level) + '_obj').search([('request_id','=',odoo_approvals_request.id),('employee_id','=',odoo_approver_type.employee_id.id)], limit=1)
        if odoo_approver.id:
            # Add this approver id to the list of approvers to update.
            if 'approvers_' + str(odoo_approver_type.level) not in odoo_approvers_to_update:
                odoo_approvers_to_update['approvers_' + str(odoo_approver_type.level)] = set()
            odoo_approvers_to_update['approvers_' + str(odoo_approver_type.level)].add(odoo_approver.id)

            # Update existing approver.
            new_approver = (_UPDATE, odoo_approver.id, vals)

        approvers_x = 'approvers_' + str(odoo_approver_type.level)
        if approvers_x not in data:
            data[approvers_x] = []
        data[approvers_x].append(new_approver)

    # Clean up approver relation
    if data['res-mode'] == 'update':
        for level in filter(lambda x: x.startswith('approvers_'), dir(odoo_approvals_request)):
            if level not in data:
                # No new approver and approver not updated.
                if level in odoo_approvers_by_level:
                    # Approver(s) in level L exist(s) in odoo.
                    if level not in odoo_approvers_to_update:
                        # Approver(s) in level L exist(s) but it's not kept.
                        data[level] = [(_CLEAR, False, False)] # Don't keep the approvers.
                        continue

                    # Approver(s) in level L exist(s) and some are kept.
                    intersection = odoo_approvers_by_level[level] & odoo_approvers_to_update[level]
                    if len(intersection) < len(odoo_approvers_by_level[level]):
                        # Keep some of the approvers, not all.
                        data[level] = [(_SET, False, list(intersection))]
                continue

            # New approver(s) or approver(s) updated.
            if level not in odoo_approvers_by_level:
                # New approver(s) only
                continue

            if level not in odoo_approvers_to_update:
                # Dangling approver records
                continue

            data[level].append((_SET, False, list(odoo_approvers_by_level[level] & odoo_approvers_to_update[level])))
    
    if weladee_approvals_request.request.IPFS:
        if data['res-mode'] == 'update':
            odoo_attach = req.attach_obj.search([('res_model','=',model_id),('res_id','=',odoo_approvals_request.id)], limit=1)
            if odoo_attach.id and odoo_attach.url == weladee_approvals_request.request.IPFS:
                # Same IPFS url
                return data

        # Download new file
        try:
            r = requests.get(weladee_approvals_request.request.IPFS)
            content = r.content
            data['document'] = base64.b64encode(content)
            data['document_file_name'] = data['name']
        except requests.Timeout as e:
            sync_logwarn(req.context_sync, 'request: %s' % e)
        except requests.RequestException as e:
            sync_logwarn(req.context_sync, 'request: %s' % e)
        except Exception as e:
            sync_logwarn(req.context_sync, 'Error: %s' % (e or 'undefined'))
    else:
        data['document_file_name'] = False
        data['document'] = False

    return data

def sync_approvals_request(req):
    req.context_sync['stat-approvals-request'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    try:
        sync_loginfo(req.context_sync,'[approvals request] updating changes from weladee -> odoo')
        weladee_approvals_request = None

        # Calculate period
        period = odoo_pb2.Period()
        if req.config.approval_period == 'w':
            period.From = int((datetime.datetime.now() - relativedelta(weeks=abs(req.config.approval_period_unit))).timestamp())
        elif req.config.approval_period == 'm':
            period.From = int((datetime.datetime.now() - relativedelta(months=abs(req.config.approval_period_unit))).timestamp())
        elif req.config.approval_period == 'y':
            period.From = int((datetime.datetime.now() - relativedelta(years=abs(req.config.approval_period_unit))).timestamp())
        elif req.config.approval_period == 'all':
            period = weladee_pb2.Empty()
        else:
            period.From = int((datetime.datetime.now() - relativedelta(weeks=1)).timestamp())

        for weladee_approvals_request in stub.GetRequests(period, metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-approvals-request'], 1)
            if not weladee_approvals_request:
                sync_logwarn(req.context_sync,'weladee approvals request is empty')
                sync_logdebug(req.context_sync, "weladee approvals request is empty '%s'" % weladee_approvals_request)
                continue

            odoo_approvals_request = sync_approvals_request_data(weladee_approvals_request, req)

            if odoo_approvals_request and odoo_approvals_request['res-mode'] == 'create':
                newid = req.approvals_request_obj.with_context({'skip_validation':True}).create(odoo_approvals_request)
                if newid and newid.id:
                    if weladee_approvals_request.request.IPFS:
                        req.attach_obj.create({
                            'type':'url',
                            'url':weladee_approvals_request.request.IPFS,
                            'name':newid.name,
                            'res_model':model_id,
                            'res_id':newid.id,
                        })
                    sync_stat_create(req.context_sync['stat-approvals-request'], 1)
                else:
                    sync_stat_error(req.context_sync['stat-approvals-request'], 1)
            elif odoo_approvals_request and odoo_approvals_request['res-mode'] == 'update' and 'res-id' in odoo_approvals_request:
                odoo_id = req.approvals_request_obj.search([("id","=",odoo_approvals_request['res-id']),'|',('active','=',False),('active','=',True)], limit=1)
                if odoo_id.id:
                    odoo_id.with_context({'skip_validation':True}).write(odoo_approvals_request)
                    if weladee_approvals_request.request.IPFS:
                        odoo_attach = req.attach_obj.search([('res_model','=',model_id),('res_id','=',odoo_id.id)], limit=1)
                        if not odoo_attach.id or (odoo_attach.id and odoo_attach.url != weladee_approvals_request.request.IPFS):
                            # Attach document
                            req.attach_obj.create({
                                'type':'url',
                                'url':weladee_approvals_request.request.IPFS,
                                'name':odoo_id.name,
                                'res_model':model_id,
                                'res_id':odoo_id.id,
                            })
                    else:
                        req.attach_obj.search([('res_model','=',model_id),('res_id','=',odoo_id.id)], limit=1).unlink() # Clear attachment
                    sync_stat_update(req.context_sync['stat-approvals-request'], 1)
                else:
                    sync_logerror(req.context_sync, 'Odoo appoval request not found for : %s' % weladee_approvals_request)
                    sync_stat_error(req.context_sync['stat-approvals-request'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        if sync_weladee_error(weladee_approvals_request, 'approvals request', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-approvals-request','[approvals request] updating changes from weladee-> odoo')
