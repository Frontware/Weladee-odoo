# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error

def sync_position_data(weladee_position, job_line_obj, context_sync):
    '''
    position data to sync
    '''
    pos = {"name" : weladee_position.position.NameEnglish,
           "weladee_id" : weladee_position.position.ID}

    # look if there is odoo record with same weladee-id
    # if not found then create else update    
    odoo_position = job_line_obj.search([("weladee_id", "=", weladee_position.position.ID)])
    if not odoo_position.id:
       pos['res-mode'] = 'create'
    else:
       pos['res-mode'] = 'update'  
       pos['res-id'] = odoo_position.id

    if pos['res-mode'] == 'create':
       # check if there is same name
       # consider it same record 
       odoo_position = job_line_obj.search([('name','=',pos['name'] )]) 
       if odoo_position.id:
          #if there is weladee id, will update it 
          sync_logdebug(context_sync, 'odoo > %s' % odoo_position)
          sync_logdebug(context_sync, 'weladee > %s' % weladee_position)
          if odoo_position.weladee_id:
             sync_logwarn(context_sync,'will replace old weladee id %s with new one %s' % (odoo_position.weladee_id, weladee_position.position.ID))      
          else:
             sync_logdebug(context_sync,'missing weladee link, will update with new one %s' % weladee_position.position.ID)      
          pos['res-mode'] = 'update'
          pos['res-id'] = odoo_position.id

    return pos          

def sync_position(job_line_obj, authorization, context_sync):
    '''
    sync all positions from weladee

    '''
    #get change data from weladee
    try:
        weladee_position = False
        sync_loginfo(context_sync,'[position] updating changes from weladee-> odoo')
        for weladee_position in stub.GetPositions(myrequest, metadata=authorization):
            if not weladee_position :
               sync_logwarn(context_sync,'weladee position is empty')
               return

            odoo_pos = sync_position_data(weladee_position, job_line_obj, context_sync)

            if odoo_pos and odoo_pos['res-mode'] == 'create':
               job_line_obj.create(odoo_pos)
               sync_loginfo(context_sync, "Insert position '%s' to odoo" % odoo_pos['name'] )

            elif odoo_pos and odoo_pos['res-mode'] == 'update':
                odoo_id = job_line_obj.search([('id','=',odoo_pos['res-id'])])
                if odoo_id.id:
                   odoo_id.write(odoo_pos)
                   sync_loginfo(context_sync, "Updated position '%s' to odoo" % odoo_pos['name'] )
                else:
                   sync_logdebug(context_sync, 'weladee > %s' % weladee_position) 
                   sync_logerror(context_sync, "Not found this odoo position id %s of '%s' in odoo" % (odoo_pos['res-id'], odoo_pos['name']) ) 

    except Exception as e:
        if sync_weladee_error(weladee_position, 'position', e, context_sync):
           return

    #scan in odoo if there is record with no weladee_id
    sync_loginfo(context_sync, '[position] updating new changes from odoo -> weladee')
    odoo_position_line_ids = job_line_obj.search([('weladee_id','=',False)])
    for positionData in odoo_position_line_ids:
        if not positionData.name :
           sync_logdebug(context_sync, 'odoo > %s' % positionData) 
           sync_logwarn(context_sync, 'do not send empty odoo position name')
           continue
        
        newPosition = odoo_pb2.PositionOdoo()
        newPosition.odoo.odoo_id = positionData.id
        newPosition.odoo.odoo_created_on = int(time.time())
        newPosition.odoo.odoo_synced_on = int(time.time())

        newPosition.position.NameEnglish = positionData.name
        newPosition.position.active = True
        try:
            returnobj = stub.AddPosition(newPosition, metadata=authorization)
            #print( result  )
            positionData.write({'weladee_id':returnobj.id})
            sync_loginfo(context_sync, "Added position to weladee : %s" % positionData.name)
        except Exception as e:
            sync_logdebug(context_sync, 'odoo > %s' % positionData)
            sync_logerror(context_sync, "Add position '%s' failed : %s" % (positionData.name, e))