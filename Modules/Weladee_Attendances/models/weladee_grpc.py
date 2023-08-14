# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import grpc

from .grpcproto import odoo_pb2
from .grpcproto import odoo_pb2_grpc
from .grpcproto import weladee_pb2

def weladee_grpc_ctrl():
    '''
    create weladee grpc connection object

    return: stub    
    '''
    creds = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel(weladee_address, creds)
    return odoo_pb2_grpc.OdooStub(channel)

weladee_address = "grpc.weladee.com:22443"