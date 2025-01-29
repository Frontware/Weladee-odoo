# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import traceback
import re

from odoo.addons.Weladee_Attendances.models.grpcproto import odoo_pb2
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import stub, myrequest, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_weladee_error,sync_clean_up
from odoo.addons.Weladee_Attendances.models.sync.weladee_base import sync_stat_to_sync,sync_stat_create,sync_stat_update,sync_stat_error,sync_stat_info 
from odoo.addons.Weladee_Attendances.library.weladee_lib import _convert_to_tz_time
from odoo.addons.Weladee_Attendances.models.sync.weladee_employee import get_emp_odoo_weladee_ids

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
    gate_field = 'gate_in'
    if weladee_att.logevent.action == "o" : 
        check_field = 'check_out' 
        gate_field = 'gate_out'

    data['res-mode'] = 'create'
    #write checkin/out time
    data[check_field] = date
    data[gate_field] = req.gate_odoo_weladee_ids.get(str(weladee_att.logevent.gateid))

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

def create_odoo_log(req, data):    
    '''
    create odoo with new connection to be able to continue
    '''
    ret = False
    try:
        ret = req.log_obj.create(sync_clean_up(data))
    except Exception as e:        
        check_log_error(req, e)
        print('create error %s' % traceback.format_exc())
    return ret

def check_log_error(req, e):
    """
    Checks for a specific error pattern in the provided exception and updates the request context with the earliest redo date.

    Args:
        req: The request object which contains the context_sync dictionary.
        e: The exception object to be checked for the error pattern.

    The function looks for an error message that matches the pattern:
    "attendance record for ... checked ... since DD/MM/YYYY HH:MM:SS".
    If a match is found, it extracts the date and updates the 'redo-date' in the request's context_sync dictionary.
    If 'redo-date' is already present, it updates it only if the new date is earlier.
    """
    pat = r"attendance record for(.+?)checked (.+?)since (\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})"
    mat = re.search(pat, str(e))
    if mat and len(mat.groups()) == 3:
       redodate = datetime.datetime.strptime(mat.group(3)[:10],'%d/%m/%Y')
       if not req.context_sync.get('redo-date'):
          req.context_sync['redo-date'] = redodate
       else:
          if redodate < req.context_sync['redo-date']:
             req.context_sync['redo-date'] = redodate                
    
    if req.context_sync.get('redo-date'): return
    if not ('duplicate key value violates unique constraint' in str(e)): return
    pat = r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
    mat = re.search(pat, str(e))
    if mat and len(mat.groups()) == 1:
       redodate = datetime.datetime.strptime(mat[0][:10],'%Y-%m-%d')
       if not req.context_sync.get('redo-date'):
          req.context_sync['redo-date'] = redodate
       else:
          if redodate < req.context_sync['redo-date']:
             req.context_sync['redo-date'] = redodate                
        
def update_odoo_log(req, odoo_log, data):    
    '''
    update odoo with new connection to be able to continue
    '''
    try:
        return req.log_obj.browse(odoo_log.id).write(sync_clean_up(data))
    except Exception as e:
        print('update error %s' % traceback.format_exc())
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
       newm = dt_today.month - dt_unit
       newy = dt_today.year
       if newm <= 0: 
          newm = 12 + newm
          newy -= 1
       dt_from = dt_today.replace(month=newm,year=newy) 
    elif req.period_settings["period"] == "y":       
       dt_from = dt_today.replace(year=dt_today.year - dt_unit)             

    return _sync_delete_log(self, req, dt_from)

def _sync_delete_log(self, req, dt_from):
    """
    Synchronize and delete attendance logs based on the given date.

    This method deletes attendance records from the log object based on the 
    provided date. If no date is provided or the period setting is "all", 
    all attendance records are deleted. Otherwise, only records with a 
    check-in time after the specified date are deleted.

    Args:
        req: An object containing the log object and period settings.
        dt_from (datetime): The date from which to start deleting records.

    Returns:
        datetime: The UTC datetime from which records were deleted, or False 
        if no date was provided.
    """
    dt_from_utc = False
    dt_delete_msg = ''
    if (not dt_from) or req.period_settings["period"] == "all":
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
    
    dt_from_utc = False
    if req.context_sync.get('redo-date'):
        sync_logdebug(req.context_sync, 'resync again at %s' % req.context_sync.get('redo-date')) 
        dt_from_utc = _sync_delete_log(self, req, req.context_sync.get('redo-date'))
        del req.context_sync['redo-date']
    else:        
        dt_from_utc = sync_delete_log(self, req)
    
    #if empty, create one 
    if not req.employee_odoo_weladee_ids: 
        sync_logdebug(req.context_sync, 'getting all employee-weladee link') 
        req.employee_odoo_weladee_ids = get_emp_odoo_weladee_ids(req)

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
        print('xxxxxxxxxxxxxxxxxxxxxxxxxx')
        print(traceback.format_exc())
        sync_logdebug(req.context_sync, 'exception > %s' % traceback.format_exc()) 
        sync_logdebug(req.context_sync, 'weladee >> %s' % weladee_att or '-') 
        sync_logdebug(req.context_sync, 'odoo >> %s' % odoo_att or '-') 
        print('xxxxxxxxxxxxxxxxxxxxxxxxxx')
        if sync_weladee_error(weladee_att, 'log', e, req.context_sync):
           return
    #stat
    del req.context_sync['cursor']
    sync_stat_info(req.context_sync,'stat-log','[log] updating changes from weladee-> odoo')
