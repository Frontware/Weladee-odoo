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

def sync_weladee_error(weladee_obj, weladee_type, e, context_sync, stop_if_connection_error=False):
    sync_stop(context_sync)
    if weladee_obj:
       sync_logdebug(context_sync, 'weladee >> %s' % weladee_obj)   

    sync_logdebug(context_sync, '[%s] Error while update data from grpc %s' % (weladee_type, e))
    sync_logerror(context_sync, '[%s] %s' % (weladee_type, grpc_error))
    if 'connection refused' in ('%s' % e):
       return True
    if 'Endpoint read failed' in ('%s' % e):
       return True 

    return False 


def sync_clean_up(vals):
    if 'res-mode' in vals: del vals['res-mode']
    if 'res-id' in vals: del vals['res-id']
    return vals    