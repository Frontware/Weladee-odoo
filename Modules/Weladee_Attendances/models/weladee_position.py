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
from . import weladee_settings
from .sync.weladee_base import stub, myrequest, sync_clean_up, sync_message_log

class weladee_job(models.Model):
    _inherit = 'hr.job'

    weladee_id = fields.Char(string="Weladee ID",copy=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', "Name can't duplicate !"),
    ]

    @api.model
    def create(self, vals) :
        odoovals = sync_clean_up(vals)
        pid = super(weladee_job,self).create( odoovals )

        # only when user create from odoo, always send
        # record from sync will not send to weladee again
        if not "weladee_id" in vals:
            self._create_in_weladee(pid, vals)

        return pid

    def _create_in_weladee(self, position_odoo, vals):
        '''
        create new record in weladee
        '''
        authorization, __, __ = weladee_settings.get_api_key(self)      
        
        if authorization:
            newPosition = odoo_pb2.PositionOdoo()
            newPosition.odoo.odoo_id = position_odoo.id
            newPosition.odoo.odoo_created_on = int(time.time())
            newPosition.odoo.odoo_synced_on = int(time.time())

            newPosition.position.NameEnglish = vals["name"]
            newPosition.position.active = True

            try:
              result = stub.AddPosition(newPosition, metadata=authorization)
              position_odoo.write({'weladee_id':result.ID,'send2-weladee':False})
              _logger.info("Added position on Weladee : %s %s" % (result, type(result)))
            except Exception as e:
              _logger.error("odoo > %s" % vals)
              _logger.error("weladee > %s" % result)
              _logger.error("Error while add position on Weladee : %s" % e)
              position_odoo._message_log(body=_('<font color="red">Error!</b> there is error while update this record in weladee: %s') % str(e))              
        else:
          _logger.error("Error while add position on Weladee : No authroized")

    def _update_in_weladee(self, position_odoo, vals):
        '''
        create new record in weladee
        '''
        authorization, __, __ = weladee_settings.get_api_key(self)      
        
        if authorization:
            newPosition = False
            newPosition_mode = 'create'
            odooRequest = odoo_pb2.OdooRequest()
            odooRequest.ID = int(position_odoo.weladee_id or '0')
            for weladee_position in stub.GetPositions(odooRequest, metadata=authorization):
                if weladee_position and weladee_position.position and weladee_position.position.ID == int(position_odoo.weladee_id or '0'):
                   newPosition = weladee_position
                   newPosition_mode = 'update'                    

            if not newPosition:
               newPosition = odoo_pb2.PositionOdoo()  

            newPosition.odoo.odoo_id = position_odoo.id
            newPosition.odoo.odoo_created_on = int(time.time())
            newPosition.odoo.odoo_synced_on = int(time.time())

            if 'name' in vals:
                newPosition.position.NameEnglish = vals["name"]
            else:
                newPosition.position.NameEnglish = position_odoo.name
            
            if newPosition_mode == 'create':
                try:
                    newPosition.position.active = True
                    result = stub.AddPosition(newPosition, metadata=authorization)
                    _logger.info("created position on Weladee : %s" % result)
                except Exception as e:
                    _logger.debug("[position] odoo > %s" % vals)
                    _logger.error("Error while create position on Weladee : %s" % e)
                    sync_message_log(position_odoo, 'when hr.position is created', e)

            elif newPosition_mode == 'update':
                _logger.warning("No update position available from odoo -> Weladee")
                sync_message_log(position_odoo, 'hr.position will not update to weladee', False)
        else:
          _logger.error("Error while update position on Weladee : No authroized")

    def write(self, vals):
        odoovals = sync_clean_up(vals)
        ret = super(weladee_job, self).write( odoovals )
        # if don't need to sync when there is weladee-id in vals
        # case we don't need to send to weladee, like just update weladee-id in odoo
        
        # created, updated from odoo, always send
        # when create didn't success sync to weladeec
        # next update, try create again
        if vals.get('send2-weladee',True):
           for each in self:
               if each.weladee_id:
                  # no update back from odoo -> weladee                  
                  _logger.warning("No update position available from odoo -> Weladee")
               else:
                  self._update_in_weladee(each, vals)

        return ret