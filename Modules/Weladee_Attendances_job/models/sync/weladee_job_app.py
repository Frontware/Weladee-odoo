# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import traceback
from odoo.addons.Weladee_Attendances.models.grpcproto.job_pb2 import ApplicationRefused
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info,sync_clean_up

base_url = 'https://www.weladee.com/jobads/jobapplication/'

def sync_jobapp_data_gender(weladee_job_app):
    '''
    convert weladee job app gender to odoo
    '''
    if weladee_job_app.JobApplication.Gender == 'm':
        return 'male'
    elif weladee_job_app.JobApplication.Gender == 'f':        
        return 'female'
    else:
        return 'other'

def sync_job_app_data(weladee_job_app, req):
    '''
    job_app data to sync
    '''
    data = {'name': weladee_job_app.JobApplication.Title,
            'weladee_id':  weladee_job_app.JobApplication.ID,
            'weladee_url': base_url + str(weladee_job_app.JobApplication.ID),
            'firstname' :  weladee_job_app.JobApplication.FirstName, 
            'lastname' :  weladee_job_app.JobApplication.LastName, 
            'partner_mobile': weladee_job_app.JobApplication.Phone,
            'email_from' : weladee_job_app.JobApplication.Email,
            'note' : weladee_job_app.JobApplication.Note,
            'gender': sync_jobapp_data_gender(weladee_job_app),
            'date_apply': datetime.datetime.fromtimestamp( weladee_job_app.JobApplication.Timestamp ),
            'partner_name': ' '.join([weladee_job_app.JobApplication.FirstName,weladee_job_app.JobApplication.LastName]),
            'source_id': req.utm_source_obj.search([('name','=','Weladee')], limit=1).id,
            'active': weladee_job_app.JobApplication.Status != ApplicationRefused
            }        
    jobadid = req.job_ads_odoo_weladee_ids.get(weladee_job_app.JobApplication.JobAdID, False)
    data['job_id'] = req.jobads_obj.browse(jobadid).position_id.id
    lgid = req.lang_obj.search([('iso_code','=', weladee_job_app.JobApplication.Language)])
    if lgid and lgid.id:
       data['lang_id']  = lgid.id

    data['res-mode'] = 'create'

    # look if there is odoo record with same weladee-id
    # if not found then create else update
    prev_rec = req.jobapp_obj.search( [ ('weladee_id','=', weladee_job_app.JobApplication.ID ), '|', ('active','=',True), ('active','=',False)],limit=1 )
    if prev_rec and prev_rec.id:
        data['res-mode'] = 'update'
        data['res-id'] = prev_rec.id
        del data['weladee_id']
        del data['weladee_url']
        del data['date_apply']
        del data['source_id']
        sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_job_app)
        sync_logdebug(req.context_sync, 'odoo > %s ' % data)

        return data

    # check if there is same name
    # consider it same record
    odoo_job_app = req.jobapp_obj.search( [ ('name','=', data['name'] ), '|', ('active','=',True), ('active','=',False)],limit=1 )
    if odoo_job_app.id:
        data['res-mode'] = 'update'
        data['res-id'] = odoo_job_app.id
        sync_logdebug(req.context_sync, 'odoo > %s' % odoo_job_app)
        sync_logdebug(req.context_sync, 'weladee > %s' % weladee_job_app)

    return data

def sync_job_applicant(req):
    '''
    sync all job_app from weladee (1 way from weladee)

    '''
    req.context_sync['stat-job_app'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_job_app = False
    weladee_job_app = False

    try:
        sync_loginfo(req.context_sync,'[job_app] updating changes from weladee-> odoo')

        # Create `Weladee` source if it does not exist
        source_id = req.utm_source_obj.search([('name','=','Weladee')], limit=1)
        if not source_id.id:
            source_id = req.utm_source_obj.create({'name':'Weladee'})
            if source_id and source_id.id:
                req.translation_obj._set_ids('utm.source,name', 'model', 'th_TH', [source_id.id], 'เวลาดี')

        for weladee_job_app in stub.GetJobApplications(weladee_pb2.Empty(), metadata=req.config.authorization):
            print(weladee_job_app)
            sync_stat_to_sync(req.context_sync['stat-job_app'], 1)
            if not weladee_job_app :
               sync_logwarn(req.context_sync,'weladee job_app is empty')
               continue

            odoo_job_app = sync_job_app_data(weladee_job_app, req)
            
            if odoo_job_app and odoo_job_app['res-mode'] == 'create':
                newid = req.jobapp_obj.create(sync_clean_up(odoo_job_app))
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert job_app '%s' to odoo" % odoo_job_app )
                    sync_stat_create(req.context_sync['stat-job_app'], 1)

                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_job_app) 
                    sync_logerror(req.context_sync, "error while create odoo job_app id %s of '%s' in odoo" % (odoo_job_app['res-id'], odoo_job_app) ) 
                    sync_stat_error(req.context_sync['stat-job_app'], 1)

            elif odoo_job_app and odoo_job_app['res-mode'] == 'update':
                odoo_id = req.jobapp_obj.search([('id','=',odoo_job_app['res-id']),'|',('active','=',True),('active','=',False)])
                if odoo_id.id:
                    odoo_id.write(sync_clean_up(odoo_job_app))
                    sync_logdebug(req.context_sync, "Updated job application '%s' to odoo" % odoo_job_app['name'] )
                    sync_stat_update(req.context_sync['stat-job_app'], 1)
                else:
                    sync_logdebug(req.context_sync, 'weladee > %s' % weladee_job_app)
                    sync_logerror(req.context_sync, "Not found this odoo job application id %s of '%s' in odoo" % (odoo_job_app['res-id'], odoo_job_app['name']) )
                    sync_stat_error(req.context_sync['stat-job_app'], 1)

    except Exception as e:
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_job_app) 
        if sync_weladee_error(weladee_job_app, 'job_app', e, req.context_sync):
            return
    #stat
    sync_stat_info(req.context_sync,'stat-job_app','[job_app] updating changes from weladee-> odoo')