# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Weladee grpc server address is hrpc.weladee.com:22443
import logging
_logger = logging.getLogger(__name__)

from odoo.addons.Weladee_Attendances.models import weladee_grpc
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2

stub = weladee_grpc.weladee_grpc_ctrl()
myrequest = weladee_pb2.EmployeeRequest()
grpc_error = 'Error while connect to GRPC Server, please check if your connection available or your Weladee API Key is valid.'

def sync_loginfo(context_sync, log):
    '''
    write in context and log info
    '''
    _logger.info('%s' % log )
    context_sync['request-logs'].append(['i', log]) 

def sync_logdebug(context_sync, log):
    '''
    write in context and log debug
    '''
    _logger.debug('%s' % log )
    print('[DEBUG]>%s' % log )
    context_sync['request-logs'].append(['d', log]) 

def sync_logerror(context_sync, log):
    '''
    write in context and log error
    '''
    _logger.error('%s' % log )
    context_sync['request-logs-y'] = 'Y'
    context_sync['request-logs'].append(['e', log])

def sync_logwarn(context_sync, log):
    '''
    write in context and log warn
    '''
    _logger.warn('%s' % log )
    context_sync['request-logs'].append(['w', log])

def sync_stop(context_sync):
    context_sync['request-error'] = True

def sync_has_error(context_sync):
    return context_sync.get('request-error',False)

def sync_weladee_error(weladee_obj, weladee_type, e, context_sync, stop_if_connection_error=False):
    sync_stop(context_sync)
    if weladee_obj:
       sync_logdebug(context_sync, 'weladee >> %s' % weladee_obj)   

    if 'connection refused' in ('%s' % e):
       sync_logerror(context_sync, '[%s] %s' % (weladee_type, grpc_error))
       return True
    if 'Endpoint read failed' in ('%s' % e):
       sync_logerror(context_sync, '[%s] %s' % (weladee_type, grpc_error))
       return True 

    sync_logerror(context_sync, '[%s] Error while update data from grpc %s' % (weladee_type, e))
    return False 

def sync_clean_up(in_vals):
    vals = in_vals.copy()
    if 'res-mode' in vals: del vals['res-mode']
    if 'res-id' in vals: del vals['res-id']
    if 'send2-weladee' in vals: del vals['send2-weladee']
    return vals    

def sync_stat_to_sync(context_sync, value):
    context_sync['to-sync'] += value
def sync_stat_create(context_sync, value):
    context_sync['create'] += value
def sync_stat_update(context_sync, value):
    context_sync['update'] += value
def sync_stat_error(context_sync, value):
    context_sync['error'] += value

def sync_stat_info(context_sync, key, keyname, newline=False):
    sync_loginfo(context_sync, '%s wait to sync %s item(s): %s created, %s updated, %s error' % (keyname,\
                                                                                             context_sync.get(key,{}).get('to-sync',0),\
                                                                                             context_sync.get(key,{}).get('create',0),\
                                                                                             context_sync.get(key,{}).get('update',0),\
                                                                                             context_sync.get(key,{}).get('error',0)))
    if newline: sync_loginfo(context_sync, ' ') 
    del context_sync[key]                                                                                            