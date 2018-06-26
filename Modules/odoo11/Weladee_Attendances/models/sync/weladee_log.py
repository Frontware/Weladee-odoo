# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import time
import datetime

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info 

def _compare_2_date(date1, date2, comparer):
    '''
    compare
    '''
    d_date1 = datetime.datetime.strptime(date1,'%Y-%m-%d %H:%M:%S')
    d_date2 = datetime.datetime.strptime(date2,'%Y-%m-%d %H:%M:%S')
    if comparer == '>':
       return d_date1 > d_date2
    elif comparer == '<':
       return d_date1 < d_date2 

def sync_log_data(emp_obj, att_obj, weladee_att, odoo_weladee_ids, context_sync):
    '''
    sync log data from weladee to odoo data

    1 odoo record will link 2 weladee logevent

    '''
    date = datetime.datetime.fromtimestamp(weladee_att.logevent.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    data = {'employee_id': odoo_weladee_ids.get(str(weladee_att.logevent.employeeid),False)}
   
    # look if there is odoo record with same time
    # if not found then create else update    
    check_field = 'check_in'
    if weladee_att.logevent.action == "o" : 
        check_field = 'check_out' 

    oldid = att_obj.search( [ ('employee_id','=', data['employee_id'] ), (check_field,'=', date)] )
    if not oldid.id:
       data['res-mode'] = 'create'
    else:
       data['res-mode'] = 'update'  
       data['res-id'] = oldid.id       
    
    #write checkin/out time
    data[check_field] = date

    # there is previous link
    if weladee_att.odoo and weladee_att.odoo.odoo_id:
        sync_logdebug(context_sync, 'has link to odoo.. ')
        oldid = att_obj.search( [ ('id','=', weladee_att.odoo.odoo_id)] )
        sync_logdebug(context_sync, 'has link to odoo.. %s' % oldid)
        if oldid.id:
            #update link
            if check_field == 'check_in':
                if oldid.check_out and _compare_2_date(oldid.check_out,data['check_in'],'<'):
                    data['check_out'] = False
                    data['res-id'] = oldid.id
                    data['res-mode'] = 'update'
                    sync_logdebug(context_sync, 'weladee > %s ' % weladee_att)
                    sync_logdebug(context_sync, 'odoo > %s ' % {'check_in':oldid.check_in, 'check_out':oldid.check_out,'employee_id':oldid.employee_id})
                    sync_logwarn(context_sync, 'change check in of employee %s bigger than old check out %s, reset old checkout' % (data['check_in'],oldid.check_out))
            elif check_field == 'check_out':
                if oldid.check_in and _compare_2_date(oldid.check_in,data['check_out'],'>'):
                    data['res-mode'] = ''
                    sync_logdebug(context_sync, 'weladee > %s ' % weladee_att)
                    sync_logdebug(context_sync, 'odoo > %s ' % {'check_in':oldid.check_in, 'check_out':oldid.check_out,'employee_id':oldid.employee_id})
                    sync_logwarn(context_sync, 'change check out of employee %s less than old check in %s, do not update' % (data['check_out'],oldid.check_in))
                else:
                    data['res-id'] = oldid.id
                    data['res-mode'] = 'update'
        else:
            sync_logdebug(context_sync, 'weladee > %s ' % weladee_att)
            sync_logwarn(context_sync, 'can''t find this odoo-id %s of this weladee log' % weladee_att.odoo.odoo_id)


    if data['res-mode'] == 'create':

       if check_field == 'check_out':
            prev_rec = att_obj.search( [ ('employee_id','=', data['employee_id'] ), ('check_out','=', False)] )
            if prev_rec.id:
                data['res-mode'] = 'update' 
                data['res-id'] = prev_rec.id

    return data      

def get_emp_odoo_weladee_ids(emp_obj, odoo_weladee_ids):
    '''
    return odoo id from weladee id
    '''
    odoo_weladee_ids = {}
    for each in emp_obj.search([('weladee_id','!=',False),'|',('active','=',False),('active','=',True)]):
        odoo_weladee_ids[each.weladee_id] = each.id

    return odoo_weladee_ids    

def sync_log(emp_obj, att_obj, authorization, context_sync, odoo_weladee_ids):
    '''
    sync all log from weladee

    '''
    context_sync['stat-log'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    odoo_att = False
    iteratorAttendance = []
    try:
        weladee_att = False
        sync_loginfo(context_sync,'[log] updating changes from weladee-> odoo')
        for weladee_att in stub.GetNewAttendance(weladee_pb2.Empty(), metadata=authorization):
            sync_stat_to_sync(context_sync['stat-log'], 1)
            if not weladee_att :
               sync_logwarn(context_sync,'weladee attendance is empty')
               continue

            #if empty, create one 
            if not odoo_weladee_ids: 
                sync_logdebug(context_sync, 'getting all employee-weladee link') 
                odoo_weladee_ids = get_emp_odoo_weladee_ids(emp_obj, odoo_weladee_ids)
            
            odoo_att = sync_log_data(emp_obj, att_obj, weladee_att, odoo_weladee_ids, context_sync)
            
            if odoo_att and odoo_att['res-mode'] == 'create':
                newid = att_obj.create(odoo_att)
                if newid.id:
                    sync_logdebug(context_sync, "Insert log '%s' to odoo" % odoo_att )
                    sync_stat_create(context_sync['stat-log'], 1)
                    #update record to weladee
                    syncLogEvent = odoo_pb2.LogEventOdooSync()
                    syncLogEvent.odoo.odoo_id = newid.id
                    syncLogEvent.odoo.odoo_created_on = int(time.time())
                    syncLogEvent.odoo.odoo_synced_on = int(time.time())
                    syncLogEvent.logid = weladee_att.logevent.id
                    iteratorAttendance.append(syncLogEvent)
                else:
                    sync_logdebug(context_sync, 'weladee > %s' % weladee_att) 
                    sync_logerror(context_sync, "error while create odoo log id %s of '%s' in odoo" % (odoo_att['res-id'], odoo_att) ) 
                    sync_stat_error(context_sync['stat-log'], 1)

            elif odoo_att and odoo_att['res-mode'] == 'update':
                odoo_id = att_obj.search([('id','=',odoo_att['res-id'])])
                if odoo_id.id:
                    if odoo_id.write(odoo_att):
                        sync_logdebug(context_sync, "Updated log '%s' to odoo" % odoo_att )
                        sync_stat_update(context_sync['stat-log'], 1)
                        #update record to weladee
                        syncLogEvent = odoo_pb2.LogEventOdooSync()
                        syncLogEvent.odoo.odoo_id = odoo_id.id
                        syncLogEvent.odoo.odoo_created_on = int(time.time())
                        syncLogEvent.odoo.odoo_synced_on = int(time.time())
                        syncLogEvent.logid = weladee_att.logevent.id
                        iteratorAttendance.append(syncLogEvent)
                    else:
                        sync_logdebug(context_sync, 'odoo > %s' % odoo_att) 
                        sync_logerror(context_sync, "error found while update this odoo log id %s" % odoo_att['res-id']) 
                        sync_stat_error(context_sync['stat-log'], 1)

                else:
                   sync_logdebug(context_sync, 'weladee > %s' % weladee_att) 
                   sync_logerror(context_sync, "Not found this odoo log id %s of '%s' in odoo" % (odoo_att['res-id'], odoo_att) ) 
                   sync_stat_error(context_sync['stat-log'], 1)

    except Exception as e:
        sync_logdebug(context_sync, 'odoo >> %s' % odoo_att) 
        if sync_weladee_error(weladee_att, 'log', e, context_sync):
           return
    #stat
    sync_stat_info(context_sync,'stat-log','[log] updating changes from weladee-> odoo')

    if len( iteratorAttendance ) > 0 :
        ge = generators(iteratorAttendance)
        __ = stub.SyncAttendance( ge , metadata=authorization )
    else:
        sync_loginfo(context_sync, '[log] No data to sent')

def generators(iteratorAttendance):
    for i in iteratorAttendance :
        yield i
