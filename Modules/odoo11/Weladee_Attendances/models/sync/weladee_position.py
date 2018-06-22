# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, sync_loginfo, sync_logerror, myrequest 

def sync_position_data(weladee_position):
    '''
    position data to sync
    '''
    return {"name" : weladee_position.position.NameEnglish,
            "weladee_id" : weladee_position.position.ID}

def sync_position(job_line_obj, authorization, context_sync):
    '''
    sync all positions from weladee

    '''
    #get change data from weladee
    try:
        context_sync['request-logs'].append(['i','updating changes from weladee-> odoo'])
        for weladee_position in stub.GetPositions(myrequest, metadata=authorization):
            if not weladee_position :
               context_sync['request-logs'].append(['d','>weladee position empty'])
            else:    
                if weladee_position.position.ID :
                   context_sync['request-logs'].append(['d','>weladee position id empty']) 
                else:    
                    #search in odoo
                    #all active false,true and weladee match
                    job_line_ids = job_line_obj.search([("weladee_id", "=", weladee_position.position.ID)])
                    if not job_line_ids :
                        context_sync['request-logs'].append(['d','>not found weladee position id in odoo']) 
                        if weladee_position.position.NameEnglish :
                            odoo_position = job_line_obj.search([('name','=',weladee_position.position.NameEnglish )])
                            #_logger.info( "check this position '%s' in odoo %s, %s" % (position.position.name_english, chk_position, position.position.ID) )
                            if not odoo_position :                                
                                __ = job_line_obj.create(sync_position_data(weladee_position))
                                sync_loginfo(context_sync, "Insert position '%s' to odoo" % weladee_position.position.NameEnglish )
                            else:
                                odoo_position.write({"weladee_id" : weladee_position.position.ID})
                                sync_loginfo(context_sync, "update weladee id to position '%s'" % weladee_position.position.NameEnglish )
                        else:
                            sync_logerror(context_sync, "Error while create position '%s' to odoo: there is no english name")
                    else :
                        for odoo_position in job_line_ids :
                            odoo_position.write( sync_position_data(weladee_position) )
                            sync_loginfo(context_sync, "Updated position '%s' to odoo" % weladee_position.position.NameEnglish )
    except Exception as e:
        context_sync['request-error'] = True
        context_sync['request-logs'].append(['d','(position) Error while connect to grpc %s' % e])
        sync_logerror(context_sync, 'Error while connect to GRPC Server, please check your connection or your Weladee API Key')
        return

    #scan in odoo if there is record with no weladee_id
    context_sync['request-logs'].append(['i','updating new changes from odoo -> weladee'])
    odoo_position_line_ids = job_line_obj.search([('weladee_id','=',False)])
    for positionData in odoo_position_line_ids:
        if not positionData.name :
           context_sync['request-logs'].append(['d','>not found odoo position name'])             
        else:            
            if positionData["weladee_id"]:
               context_sync['request-logs'].append(['d','>strange case, found odoo weladee-id %s' % positionData["weladee_id"]])
            else:
                newPosition = odoo_pb2.PositionOdoo()
                newPosition.odoo.odoo_id = positionData.id
                newPosition.odoo.odoo_created_on = int(time.time())
                newPosition.odoo.odoo_synced_on = int(time.time())

                newPosition.position.NameEnglish = positionData.name
                newPosition.position.active = True
                #print(newPosition)
                try:
                    returnobj = stub.AddPosition(newPosition, metadata=authorization)
                    #print( result  )
                    positionData.write({'weladee_id':returnobj.id})
                    sync_loginfo(context_sync, "Added position to weladee : %s" % positionData.name)
                except Exception as e:
                    sync_logerror(context_sync, "Add position '%s' failed : %s" % (positionData.name, e))