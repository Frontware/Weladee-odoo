##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-Now Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields
from openerp.osv import osv
from datetime import datetime,date, timedelta
import grpc
import logging
import weladee_pb2
import weladee_pb2_grpc
import base64
import requests

class weladee_employee(osv.osv):
  _name="weladee_attendance.synchronous"
  _description="synchronous Employee, Department, Holiday and attences"
  _inherit = 'hr.employee'

  _columns = {
    'sync' : fields.date('sync_date')
  }

