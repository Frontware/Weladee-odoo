# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)
import time

from odoo import osv
from odoo import models, fields, api, _
from datetime import datetime,date, timedelta
from odoo import exceptions

class weladee_job_ads(models.Model):
    _name = 'weladee_job_ads'

    name = fields.Char(string='Name')
    position_id = fields.Many2one('hr.job',string='Position')
    publish_date = fields.Date('Publish date')
    expire_date = fields.Date('Expire date')
    location = fields.Text('Location')
    description = fields.Text('Description')
    skills = fields.Text('Skill')
    weladee_id = fields.Char(string="Weladee ID",copy=False)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', "Name can't duplicate !"),
    ]

    @api.model
    def create(self, vals):
        if not vals.get('position_id', False):
           # create new position
           jobob = self.env['hr.job']
           ji = jobob.search([('name','=', vals['name'])])
           if ji and ji.id:
              pass
           else:
              ji = jobob.create({
                  'name': vals['name'],
                  'weladee_id': -1
              }) 

           vals['position_id']  = ji.id
        ret = super(weladee_job_ads, self).create(vals)
        
        return ret