# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
# Weladee grpc server address is hrpc.weladee.com:22443
import logging
_logger = logging.getLogger(__name__)

from odoo.addons.Weladee_Attendances.models import weladee_grpc
from odoo.addons.Weladee_Attendances.models.grpcproto import weladee_pb2

stub = weladee_grpc.weladee_grpc_ctrl()
myrequest = weladee_pb2.EmployeeRequest()

def sync_loginfo(context_sync, log):
    '''
    write in context and log info
    '''
    _logger.info( log )
    context_sync['request-debug'].append( log ) 

def sync_logerror(context_sync, log):
    '''
    write in context and log info
    '''
    _logger.error(log)
    context_sync['request-errors'].append(log)

