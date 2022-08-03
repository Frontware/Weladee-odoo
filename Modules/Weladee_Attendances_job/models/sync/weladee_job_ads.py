# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import traceback
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up

def sync_job_ads_data(weladee_job_ads, req):
    '''
    job_ads data to sync
    '''
    data = {'name': weladee_job_ads.JobAd.Title,
            'description': weladee_job_ads.JobAd.Description,
            'skills': weladee_job_ads.JobAd.Skills,
            'location': weladee_job_ads.JobAd.Location,
            'publish_date': datetime.datetime.fromtimestamp(weladee_job_ads.JobAd.PublishDate),
            'expire_date': datetime.datetime.fromtimestamp(weladee_job_ads.JobAd.ExpireDate),
            'weladee_id':  weladee_job_ads.JobAd.ID,            
            }        

    data['res-mode'] = 'create'

    # look if there is odoo record with same weladee-id
    # if not found then create else update
    prev_rec = req.jobads_obj.search( [ ('weladee_id','=', weladee_job_ads.JobAd.ID )],limit=1 )
    if prev_rec and prev_rec.id:
        data['res-mode'] = 'update'
        data['res-id'] = prev_rec.id
        sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_job_ads)
        sync_logdebug(req.context_sync, 'odoo > %s ' % data)
        # sync_logwarn(req.context_sync, 'this job_ads\'name record already exist for this %s exist, no change will apply' % data['name'])
        # return data

    # check if there is same name
    # consider it same record
    # odoo_job_ads = req.jobads_obj.search( [ ('name','=', data['name'] ) ],limit=1 )
    # if odoo_job_ads.id:
    #     data['res-mode'] = 'update'
    #     data['res-id'] = odoo_job_ads.id
    #     sync_logdebug(req.context_sync, 'odoo > %s' % odoo_job_ads)
    #     sync_logdebug(req.context_sync, 'weladee > %s' % weladee_job_ads)

    return data   

def sync_delete_jobapp(req):
    del_ids = req.jobapp_obj.search([('weladee_id','!=',False)])
    if del_ids: 
       del_ids.unlink()
       sync_logwarn(req.context_sync, 'remove all linked jobapp: %s record(s)' % len(del_ids))

def sync_delete_jobads(req):
    del_ids = req.jobads_obj.search([('weladee_id','!=',False)])
    if del_ids: 
       del_ids.unlink()
       sync_logwarn(req.context_sync, 'remove all linked jobads: %s record(s)' % len(del_ids))

def sync_job_ads(req):
    '''
    sync all job_ads from weladee (1 way from weladee)

    '''
    req.context_sync['stat-job_ads'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_job_ads = False
    weladee_job_ads = False

    # sync_delete_jobapp(req)
    # sync_delete_jobads(req)

    try:        
        sync_loginfo(req.context_sync,'[job_ads] updating changes from weladee-> odoo')
        for weladee_job_ads in stub.GetJobAds(weladee_pb2.Empty(), metadata=req.config.authorization):
            
            sync_stat_to_sync(req.context_sync['stat-job_ads'], 1)
            if not weladee_job_ads :
               sync_logwarn(req.context_sync,'weladee job_ads is empty')
               continue

            odoo_job_ads = sync_job_ads_data(weladee_job_ads, req)
            
            if odoo_job_ads and odoo_job_ads['res-mode'] == 'create':
                newid = req.jobads_obj.create(sync_clean_up(odoo_job_ads))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert job_ads '%s' to odoo" % odoo_job_ads )
                    sync_stat_create(req.context_sync['stat-job_ads'], 1)

                    req.job_ads_odoo_weladee_ids[weladee_job_ads.JobAd.ID] = newid.id
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_job_ads) 
                    sync_logerror(req.context_sync, "error while create odoo job_ads id %s of '%s' in odoo" % (odoo_job_ads['res-id'], odoo_job_ads) ) 
                    sync_stat_error(req.context_sync['stat-job_ads'], 1)

            elif odoo_job_ads and odoo_job_ads['res-mode'] == 'update':
                odoo_id = req.jobads_obj.search([('id','=',odoo_job_ads['res-id'])])
                if odoo_id.id:
                    odoo_id.write(sync_clean_up(odoo_job_ads))
                    sync_logdebug(req.context_sync, "Updated job ads '%s' to odoo" % odoo_job_ads['name'] )
                    sync_stat_update(req.context_sync['stat-job_ads'], 1)

                    req.job_ads_odoo_weladee_ids[weladee_job_ads.JobAd.ID] = odoo_id.id
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_job_ads)
                    sync_logerror(req.context_sync, "Not found this odoo job ads id %s of '%s' in odoo" % (odoo_job_ads['res-id'], odoo_job_ads['name']) )
                    sync_stat_error(req.context_sync['stat-job_ads'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_job_ads) 
        if sync_weladee_error(weladee_job_ads, 'job_ads', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-job_ads','[job_ads] updating changes from weladee-> odoo')