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
    _order = 'expire_date desc'

    name = fields.Char(string='Name')
    position_id = fields.Many2one('hr.job',string='Position')
    publish_date = fields.Date('Publish date')
    expire_date = fields.Date('Expire date')
    location = fields.Text('Location')
    description = fields.Text('Description')
    skills = fields.Text('Skill')
    weladee_id = fields.Char(string="Weladee ID",copy=False)
    weladee_url = fields.Char('Weladee URL',copy=False)

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
        
    def open_weladee_jobads(self):
        if self.weladee_id:
            return {
                'name': self.name,
                'type': 'ir.actions.act_url',
                'url': self.weladee_url,
                'target': 'new'
            }

    def action_jobads_live(self):
        return {
            'type': 'ir.actions.act_url',
            'name': "Live",
            'target': 'new',
            'url': 'https://job.weladee.com/c/%s' % self.env['weladee_attendance.synchronous.setting'].get_company(),
        }