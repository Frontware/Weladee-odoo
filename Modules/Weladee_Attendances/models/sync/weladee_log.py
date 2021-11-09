# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import traceback

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from .weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error,sync_clean_up
from .weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info 
from odoo.addons.Weladee_Attendances.library.weladee_lib import _convert_to_tz_time

def sync_log_data(weladee_att, req):
    '''
    sync log data from weladee to odoo data

    1 odoo record will link 2 weladee logevent

    '''
    date = datetime.datetime.fromtimestamp(weladee_att.logevent.timestamp).strftime('%Y-%m-%d %H:%M:%S')
    data = {'employee_id': req.employee_odoo_weladee_ids.get(str(weladee_att.logevent.employeeid),False)}
   
    # look if there is odoo record with same time
    # if not found then create else update    
    check_field = 'check_in'
    if weladee_att.logevent.action == "o" : 
        check_field = 'check_out' 

    data['res-mode'] = 'create'
    #write checkin/out time
    data[check_field] = date

    if not data['employee_id']:
        data['res-mode'] = '' 
        sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_att)
        sync_logdebug(req.context_sync, 'odoo > %s ' % data)
        sync_logwarn(req.context_sync, 'this checkin has no employee id, no change')

    if data['res-mode'] == 'create':
       if check_field == 'check_in': 
          prev_rec = req.log_obj.search( [ ('employee_id','=', data['employee_id'] ), (check_field,'=', date)],limit=1 )
          if prev_rec and prev_rec.id:
             data['res-mode'] = '' 
             sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_att)
             sync_logdebug(req.context_sync, 'odoo > %s ' % data)
             sync_logwarn(req.context_sync, 'this checkin record already exist for this %s exist, no change ' % data['employee_id'])

       elif check_field == 'check_out':
            prev_rec = req.log_obj.search( [ ('employee_id','=', data['employee_id'] ), ('check_out','=', False)],limit=1)
            if prev_rec and prev_rec.id:
                data['res-mode'] = 'update' 
                data['res-id'] = prev_rec.id
            else:
                data['res-mode'] = '' 
                sync_logdebug(req.context_sync, 'weladee > %s ' % weladee_att)
                sync_logdebug(req.context_sync, 'odoo > %s ' % data)
                sync_logwarn(req.context_sync, 'can''t find this odoo-employee-id %s with no checkout ' % data['employee_id'])
    return data      

def get_emp_odoo_weladee_ids(req):
    '''
    return odoo id from weladee id
    '''
    odoo_weladee_ids = {}
    for each in req.employee_obj.search([('weladee_id','!=',False),'|',('active','=',False),('active','=',True)]):
        odoo_weladee_ids[each.weladee_id] = each.id

    return odoo_weladee_ids    

def create_odoo_log(req, data):    
    '''
    create odoo with new connection to be able to continue
    '''
    ret = False
    try:
        ret = req.log_obj.create(sync_clean_up(data))
    except Exception as e:
        pass
    return ret

def update_odoo_log(req, odoo_log, data):    
    '''
    update odoo with new connection to be able to continue
    '''
    try:
        return req.log_obj.browse(odoo_log.id).write(sync_clean_up(data))
    except Exception as e:
        return False

def sync_delete_log(self, req):
    '''
    delete the hr attendance according filter
    '''
    dt_today = datetime.datetime.today()
    dt_unit = int(req.period_settings["unit"])
    dt_from = False
    if req.period_settings["period"] == "w":
       dt_from = dt_today - datetime.timedelta(days=(dt_unit * 7))
    elif req.period_settings["period"] == "m":       
       dt_from = dt_today.replace(month=dt_today.month - dt_unit) 
    elif req.period_settings["period"] == "y":       
       dt_from = dt_today.replace(month=dt_today.year - dt_unit)             

    dt_from_utc = False
    dt_delete_msg = ''
    if req.period_settings["period"] == "all":
        del_ids = req.log_obj.search([])
        dt_delete_msg = 'remove all %s attendance(s) from all records' % len(del_ids)
    else:
       # delete every record that has checkin after the select period
       dt_from_utc = _convert_to_tz_time(self, dt_from.strftime('%Y-%m-%d 00:00:00'))
       del_ids = req.log_obj.search([('check_in','>=', dt_from_utc.strftime('%Y-%m-%d 00:00:00'))])
       dt_delete_msg = 'remove all %s attendance after this period (%s)' % (len(del_ids),dt_from.strftime('%Y-%m-%d 00:00:00'))

    if del_ids: 
       del_ids.unlink()
       sync_logwarn(req.context_sync, dt_delete_msg)

    return dt_from_utc 

def sync_log(self, req):
    '''
    sync all log from weladee

    '''
    req.context_sync['stat-log'] = {'to-sync':0, "create":0, "update": 0, "error":0}
    req.context_sync['error-emp'] = {}
    req.context_sync['cursor'] = False
    
    dt_from_utc = sync_delete_log(self, req)

    odoo_att = False
    weladee_att = False    
    try:
        sync_loginfo(req.context_sync,'[log] updating changes from weladee-> odoo')
        reqw = odoo_pb2.AttendanceRequest()
        if dt_from_utc:
           reqw.From = int(dt_from_utc.timestamp())

        ireq = 0
        for weladee_att in stub.GetNewAttendance(reqw, metadata=req.config.authorization):
            ireq +=1

            sync_stat_to_sync(req.context_sync['stat-log'], 1)
            if not weladee_att :
                sync_logwarn(req.context_sync,'weladee attendance is empty')
                continue

            #if empty, create one 
            if not req.employee_odoo_weladee_ids: 
                sync_logdebug(req.context_sync, 'getting all employee-weladee link') 
                req.employee_odoo_weladee_ids = get_emp_odoo_weladee_ids(req)
            
            # this function should write enough, odoo and weladee current record data
            odoo_att = sync_log_data(weladee_att, req)
            
            if odoo_att and odoo_att['res-mode'] == 'create':
                newid = create_odoo_log(req, odoo_att)                
                
                if newid and newid.id:
                    sync_logdebug(req.context_sync, "Insert log '%s' to odoo" % odoo_att )
                    sync_stat_create(req.context_sync['stat-log'], 1)

                    
                else:
                    sync_stat_error(req.context_sync['stat-log'], 1)
            elif odoo_att and odoo_att['res-mode'] == 'update':
                odoo_id = req.log_obj.search([('id','=',odoo_att.get('res-id',False) )])
                if odoo_id.id:                    
                    if update_odoo_log(req, odoo_id, odoo_att):
                        sync_logdebug(req.context_sync, "Updated log '%s' to odoo" % odoo_att )
                        sync_stat_update(req.context_sync['stat-log'], 1)

                    else:
                        sync_stat_error(req.context_sync['stat-log'], 1)

                else:
                    sync_logerror(req.context_sync, "Not found this odoo log id %s of '%s' in odoo" % (odoo_att.get('res-id',False) , odoo_att) ) 
                    sync_stat_error(req.context_sync['stat-log'], 1)

    except Exception as e:
        print(traceback.format_exc())
        sync_logdebug(req.context_sync, 'weladee >> %s' % weladee_att or '-') 
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_att or '-') 
        if sync_weladee_error(weladee_att, 'log', e, req.context_sync):
           return
    #stat
    del req.context_sync['cursor']
    sync_stat_info(req.context_sync,'stat-log','[log] updating changes from weladee-> odoo')
