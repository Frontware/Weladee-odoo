# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, grpc_time_out, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error, renew_connection
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info

def sync_position_data(weladee_position, req):
    '''
    position data to sync
    '''
    pos = {"name" : weladee_position.position.NameEnglish,
           "weladee_id" : weladee_position.position.ID,
           'send2-weladee':False}

    # look if there is odoo record with same weladee-id
    # if not found then create else update    
    odoo_position = req.job_obj.search([("weladee_id", "=", weladee_position.position.ID)],limit=1) 
    if not odoo_position.id:
       pos['res-mode'] = 'create'
    else:
       pos['res-mode'] = 'update'  
       pos['res-id'] = odoo_position.id
       if not weladee_position.odoo.odoo_id:
          pos['send2-weladee'] = True

    if pos['res-mode'] == 'create':
       # check if there is same name
       # consider it same record 
       odoo_position = req.job_obj.search([('name','=',pos['name'] )],limit=1) 
       if odoo_position.id:
          #if there is weladee id, will update it 
          sync_logdebug(req.context_sync, 'odoo > %s' % odoo_position)
          sync_logdebug(req.context_sync, 'weladee > %s' % weladee_position)
          if odoo_position.weladee_id:
             sync_logwarn(req.context_sync,'will replace old weladee id %s with new one %s' % (odoo_position.weladee_id, weladee_position.position.ID))      
          else:
             sync_logdebug(req.context_sync,'missing weladee link, will update with new one %s' % weladee_position.position.ID)      
          pos['res-mode'] = 'update'
          pos['res-id'] = odoo_position.id

    return pos          

def resync_position(req):
    """
    Resynchronize the position by attempting to renew the connection and retry the synchronization.
 
    This function logs debug messages indicating the detection of an invalid or failed connection,
    attempts to renew the connection, and then retries the synchronization process.
 
    Args:
       req: An object containing the context for synchronization, including the context_sync attribute
           which holds synchronization-related information.
 
    Side Effects:
       - Logs debug messages about the connection status and actions taken.
       - Updates the 'request-logs-y' and 'request-error' keys in the context_sync dictionary to False.
       - Calls the renew_connection() function to attempt to renew the connection.
       - Calls the sync_position(req) function to retry the synchronization process.
    """
    sync_logdebug(req.context_sync, "Detected invalid or failed connection")
    sync_logdebug(req.context_sync, "Attempting to renew the connection and retry synchronization...")
    # reset error
    req.context_sync['request-logs-y'] = False
    req.context_sync['request-error'] = False
    renew_connection()
    sync_position(req)

def sync_position(req):
    '''
    sync all positions from weladee

    '''
    req.context_sync['stat-position'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['stat-w-position'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    #get change data from weladee
    try:
        weladee_position = False
        sync_loginfo(req.context_sync,'[position] updating changes from weladee-> odoo')
        for weladee_position in stub.GetPositions(myrequest, metadata=req.config.authorization, timeout=grpc_time_out):
            sync_stat_to_sync(req.context_sync['stat-position'], 1)
            if not weladee_position :
               sync_logwarn(req.context_sync,'weladee position is empty')
               continue

            odoo_pos = sync_position_data(weladee_position, req)

            if odoo_pos and odoo_pos['res-mode'] == 'create':
               req.job_obj.create(odoo_pos)
               sync_logdebug(req.context_sync, "Insert position '%s' to odoo" % odoo_pos['name'] )
               sync_stat_create(req.context_sync['stat-position'], 1)

            elif odoo_pos and odoo_pos['res-mode'] == 'update':
                odoo_id = req.job_obj.search([('id','=',odoo_pos['res-id'])])
                if odoo_id.id:
                   odoo_id.write(odoo_pos)
                   sync_logdebug(req.context_sync, "Updated position '%s' to odoo" % odoo_pos['name'] )
                   sync_stat_update(req.context_sync['stat-position'], 1)
                else:
                   sync_logdebug(req.context_sync, 'weladee > %s' % weladee_position) 
                   sync_logerror(req.context_sync, "Not found this odoo position id %s of '%s' in odoo" % (odoo_pos['res-id'], odoo_pos['name']) ) 
                   sync_stat_error(req.context_sync['stat-position'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        if sync_weladee_error(weladee_position, 'position', e, req.context_sync):
           return
    #stat
    sync_stat_info(req.context_sync,'stat-position','[position] updating changes from weladee-> odoo')

    #scan in odoo if there is record with no weladee_id
    sync_loginfo(req.context_sync, '[position] updating new changes from odoo -> weladee')
    odoo_position_line_ids = req.job_obj.search([('weladee_id','=',False)])
    for positionData in odoo_position_line_ids:
        sync_stat_to_sync(req.context_sync['stat-w-position'], 1)
        if not positionData.name :
           sync_logdebug(req.context_sync, 'odoo > %s' % positionData) 
           sync_logwarn(req.context_sync, 'do not send empty odoo position name')
           continue
        
        newPosition = odoo_pb2.PositionOdoo()
        newPosition.odoo.odoo_id = positionData.id
        newPosition.odoo.odoo_created_on = int(time.time())
        newPosition.odoo.odoo_synced_on = int(time.time())

        newPosition.position.NameEnglish = positionData.name
        newPosition.position.active = True
        try:
            returnobj = stub.AddPosition(newPosition, metadata=req.config.authorization)
            sync_logdebug(req.context_sync, "return from weladee : %s" % returnobj)
            positionData.write({'send2-weladee': False, 'weladee_id':returnobj.ID})
            sync_logdebug(req.context_sync, "Added position to weladee : %s" % positionData.name)
            sync_stat_create(req.context_sync['stat-w-position'], 1)
        except Exception as e:
            sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
            sync_logdebug(req.context_sync, 'odoo > %s' % positionData)
            sync_logerror(req.context_sync, "Add position '%s' failed : %s" % (positionData.name, e))
            sync_stat_error(req.context_sync['stat-w-position'], 1)
    #stat
    sync_stat_info(req.context_sync,'stat-w-position','[position] updating new changes from odoo -> weladee',newline=True)