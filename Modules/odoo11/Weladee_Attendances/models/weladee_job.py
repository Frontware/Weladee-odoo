# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import time

from odoo import osv
from odoo import models, fields, api
from datetime import datetime,date, timedelta
from odoo import exceptions

from .grpcproto import odoo_pb2
from . import weladee_employee
from .sync.weladee_base import stub, myrequest
class weladee_job(models.Model):
    _inherit = 'hr.job'

    weladee_id = fields.Char(string="Weladee ID")

    @api.model
    def create(self, vals) :
        pid = super(weladee_job,self).create( vals )

        # only when user create from odoo, always send
        # record from sync will not send to weladee again
        if not "weladee_id" in vals:
            self._create_in_weladee(pid, vals)

        return pid

    def _create_in_weladee(self, position_odoo, vals):
        '''
        create new record in weladee
        '''
        authorization, __, __ = weladee_employee.get_api_key(self)      
        
        if authorization:
            newPosition = odoo_pb2.PositionOdoo()
            newPosition.odoo.odoo_id = position_odoo.id
            newPosition.odoo.odoo_created_on = int(time.time())
            newPosition.odoo.odoo_synced_on = int(time.time())

            newPosition.position.NameEnglish = vals["name"]
            newPosition.position.active = True

            try:
              result = stub.AddPosition(newPosition, metadata=authorization)
              _logger.info("Added position on Weladee : %s" % result.id)
            except Exception as e:
              _logger.error("Error while add position on Weladee : %s" % e)
        else:
          _logger.error("Error while add position on Weladee : No authroized")

    def _update_in_weladee(self, position_odoo, vals):
        '''
        create new record in weladee
        '''
        authorization, __, __ = weladee_employee.get_api_key(self)      
        
        if authorization:


            newPosition = odoo_pb2.PositionOdoo()
            newPosition.odoo.odoo_id = position_odoo.id
            newPosition.odoo.odoo_created_on = int(time.time())
            newPosition.odoo.odoo_synced_on = int(time.time())

            newPosition.position.NameEnglish = vals["name"]
            newPosition.position.active = True

            try:
              result = stub.UpdatePosition(newPosition, metadata=authorization)
              _logger.info("updated position on Weladee : %s" % result.id)
            except Exception as e:
              _logger.error("Error while update position on Weladee : %s" % e)
        else:
          _logger.error("Error while update position on Weladee : No authroized")

    @api.multi
    def write(self, vals):
        pid = super(weladee_job, self).write( vals )
        # if don't need to sync when there is weladee-id in vals
        # case we don't need to send to weladee, like just update weladee-id in odoo
        
        # created, updated from odoo, always send
        # when create didn't success sync to weladee
        # next update, try create again
        if not "weladee_id" in vals:
           for each in self:
               if each.weladee_id:
                  each._update_in_weladee(pid, vals)
               else:
                  each._create_in_weladee(pid, vals)

        return pid