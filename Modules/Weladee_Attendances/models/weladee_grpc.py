# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import grpc
from .grpcproto import odoo_pb2_grpc

def weladee_grpc_ctrl():
    """
    Establishes a secure gRPC channel to the Weladee service and returns an OdooStub.

    This function creates SSL channel credentials and uses them to create a secure
    gRPC channel to the Weladee service specified by `weladee_address`. It then
    returns an instance of `OdooStub` which can be used to make RPC calls to the
    Weladee service.

    Returns:
        odoo_pb2_grpc.OdooStub: A stub for making RPC calls to the Weladee service.
    """
    creds = grpc.ssl_channel_credentials()
    channel = grpc.secure_channel(weladee_address, creds)
    return odoo_pb2_grpc.OdooStub(channel)

weladee_address = "grpc.weladee.com:22443"