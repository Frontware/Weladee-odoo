# -*- coding: utf-8 -*-

from datetime import datetime
import requests
import subprocess
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import approval_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

_UPDATE = 1 # Update relation

base_url = 'https://www.weladee.com/approval/req/'

model_id = 'fw.approvals.request'

status_dict = {
    'approvalnew':'submitted',
    'approvalrejected':'refused',
    'approvalcancelled':'canceled',
    'approvalapproved':'approved_3',
    'approvallevel1approved':'approved_1',
    'approvallevel2approved':'approved_2',
}

response_dict = {
    'responsewaiting':False,
    'responseapproved':True,
    'responserejected':False,
}

def sync_approvals_request_data(weladee_approvals_request, req):
    data = {
        'weladee_id':weladee_approvals_request.request.ID,
        'weladee_url':base_url + str(weladee_approvals_request.request.ID),
    }

    # Check for odoo approval type with same weladee-id.
    odoo_approvals_type = req.approvals_type_obj.search([("weladee_id","=",weladee_approvals_request.request.TypeID),'|',('active','=',False),('active','=',True)], limit=1)
    if not odoo_approvals_type.id:
        # Approval type with same weladee-id does not exists.
        return
    data['type'] = odoo_approvals_type.id
    data['name'] = odoo_approvals_type.name

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

    # if odoo_approvals_type.field_place != 'none': # Uncomment when place field is available
    #     data['place'] = weladee_approvals_request.request.Place
    if odoo_approvals_type.field_period != 'none':
        data['date_start'] = datetime.fromtimestamp(weladee_approvals_request.request.PeriodFrom)
        data['date_end'] = datetime.fromtimestamp(weladee_approvals_request.request.PeriodTo)
    # if odoo_approvals_type.field_amount != 'none': # Uncomment when amount field is available
    #     data['amount'] = weladee_approvals_request.request.Amount
    # if odoo_approvals_type.field_quantity != 'none': # Uncomment when quantity field is available
    #     data['quantity'] = weladee_approvals_request.request.Quantity
    if odoo_approvals_type.field_date != 'none':
        data['date'] = datetime.fromtimestamp(weladee_approvals_request.request.Date).strftime('%Y-%m-%d')
    # if odoo_approvals_type.field_reference != 'none': # Uncomment when reference field is available
    #     data['reference'] = weladee_approvals_request.Reference
    
    data['state'] = status_dict[approval_pb2.ApprovalStatus.Name(weladee_approvals_request.request.Status).lower()]
    
    # Check for odoo record with same weladee-id
    odoo_approvals_request = req.approvals_request_obj.search([('weladee_id','=',data['weladee_id']),'|',('active','=',False),('active','=',True)], limit=1)
    if not odoo_approvals_request.id:
        # odoo record does not exist.
        data['res-mode'] = 'create'
    else:
        # odoo record exists.
        data['res-mode'] = 'update'
        data['res-id'] = odoo_approvals_request.id
    
    for approver in weladee_approvals_request.request.Responses:
        # Retrieve employee in odoo with the same weladee-id.
        odoo_approver = req.approvals_approver_obj.search([("weladee_id","=",approver.EmployeeID),'|',('active','=',False),('active','=',True)], limit=1)
        if not odoo_approver.id:
            # Approver is not employee in odoo.
            continue

        # Update approver relation command.
        update_approver = (_UPDATE, odoo_approver.id, {
                'status':response_dict[approval_pb2.ApprovalResponse.Name(approver.Answer).lower()],
            },
        )

        if approver.Level == 1:
            if 'approvers_1' not in data:
                data['approvers_1'] = []
            data['approvers_1'].append(update_approver)
        elif approver.Level == 2:
            if 'approvers_2' not in data:
                data['approvers_2'] = []
            data['approvers_2'].append(update_approver)
        else:
            if 'approvers_3' not in data:
                data['approvers_3'] = []
            data['approvers_3'].append(update_approver)

    return data

def sync_approvals_request(req):
    req.context_sync['stat-approvals-request'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    try:
        sync_loginfo(req.context_sync,'[approvals request] updating changes from weladee -> odoo')
        weladee_approvals_request = None
        for weladee_approvals_request in stub.GetRequests(weladee_pb2.Empty(), metadata=req.config.authorization):
            sync_stat_to_sync(req.context_sync['stat-approvals-request'], 1)
            if not weladee_approvals_request:
                sync_logwarn(req.context_sync,'weladee approvals request is empty')
                sync_logdebug(req.context_sync, "weladee approvals request is empty '%s'" % weladee_approvals_request)
                continue

            odoo_approvals_request = sync_approvals_request_data(weladee_approvals_request, req)

            if odoo_approvals_request and odoo_approvals_request['res-mode'] == 'create':
                try:
                    newid = req.approvals_request_obj.create(odoo_approvals_request)
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
                except Exception as e:
                    print(traceback.format_exc())
                    sync_logerror(req.context_sync, 'Add appoval request %s failed : %s' % (weladee_approvals_request, e))
                    sync_stat_error(req.context_sync['stat-approvals-request'], 1)
            elif odoo_approvals_request and odoo_approvals_request['res-mode'] == 'update' and 'res-id' in odoo_approvals_request:
                odoo_id = req.approvals_request_obj.search([("id","=",odoo_approvals_request['res-id']),'|',('active','=',False),('active','=',True)], limit=1)
                if odoo_id.id:
                    try:
                        odoo_id.write(odoo_approvals_request)
                        req.attach_obj.search([('res_model','=',model_id),('res_id','=',odoo_id.id)]).unlink() # Clear attachment
                        if weladee_approvals_request.request.IPFS:
                            # Attach document
                            req.attach_obj.create({
                                'type':'url',
                                'url':weladee_approvals_request.request.IPFS,
                                'name':odoo_id.name,
                                'res_model':model_id,
                                'res_id':odoo_id.id,
                            })
                        sync_stat_update(req.context_sync['stat-approvals-request'], 1)
                    except Exception as e:
                        print(traceback.format_exc())
                        sync_logerror(req.context_sync, 'Update appoval request %s failed : %s' % (weladee_approvals_request, e))
                        sync_stat_error(req.context_sync['stat-approvals-request'], 1)
                else:
                    sync_logerror(req.context_sync, 'Odoo appoval request not found for : %s' % weladee_approvals_request)
                    sync_stat_error(req.context_sync['stat-approvals-request'], 1)

    except Exception as e:
        print(traceback.format_exc())
        if sync_weladee_error(weladee_approvals_request, 'approvals request', e, req.context_sync):
           return
    
    sync_stat_info(req.context_sync,'stat-approvals-request','[approvals request] updating changes from weladee-> odoo')
