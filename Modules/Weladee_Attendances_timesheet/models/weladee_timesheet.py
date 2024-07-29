# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
_logger = logging.getLogger(__name__)

from odoo import osv
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class weladee_account_analytic_line(models.Model):
    _inherit = 'account.analytic.line'

    weladee_id = fields.Char(string="Weladee ID",copy=False)
    is_weladee = fields.Boolean(compute='_compute_from_weladee', copy=False, readonly=True, store=True)
    work_type_id = fields.Many2one('mail.activity.type', string='Work type')
    weladee_cost = fields.Float(string="Weladee cost",digits=(12,2))
    time_to_charge  = fields.Float(string="Time to charge",digits=(12,2))

    def open_weladee_timesheet(self):
      '''
      open weladee timesheet url
      '''
      if self.weladee_id:
        return {
              'name': _("Weladee Timesheet"),
              'type': 'ir.actions.act_url',
              'target': 'new'
          }
      else:
        raise UserError(_("This employee doesn't have weladee url."))

    def unlink(self):
        self.env['weladee_attendance.synchronous'].check_weladee_id(self, {})
        return super(weladee_account_analytic_line, self).unlink()

    def write(self, vals):
        self.env['weladee_attendance.synchronous'].check_weladee_id(self, {})
        return super(weladee_account_analytic_line, self).write(vals)

    @api.depends('weladee_id')
    def _compute_from_weladee(self):
        for record in self:
            if record.weladee_id:
                record.is_weladee = True
            else:
                record.is_weladee = False

    def write(self, vals):
        if not self.env.context.get('updateLang'):
           for each in self:
               cansave = True
               if each.weladee_id: cansave = 'weladee_id' in vals

               if not cansave and self.env.context.get('validate_weladee_id', True):
                  raise UserError('You cannot change this record from weladee') 
        
        r = False
        try:            
           r = super(weladee_account_analytic_line, self).write(vals)
        except Exception as e:
           r = self.forceupdate(super(weladee_account_analytic_line, self).write, vals, e)
        return r    

    @api.model_create_multi
    def create(self, vals_list):
        r = False
        try:
           r = super().create(vals_list)
        except Exception as e:
           r = self.forceupdate(super().create, vals_list, e)
        return r     

    def forceupdate(self, fn, vals_list, e):
        r = False
        estr = ('%s' % e)
        forceupdate = False
        if 'Timesheets must be created with an active employee' in estr:
            forceupdate = True
        elif 'You cannot set an archived employee to the existing timesheets' in estr:
            forceupdate = True
            
        if forceupdate:   
            if not self.env.context.get('validate_weladee_id',True):
                eid = False
                if type(vals_list) is list:
                   eid = vals_list[0]['employee_id']
                else:
                   eid = vals_list['employee_id']
                # set employee active = True
                self.env['hr.employee'].browse(eid).write({'active':True})
                r = fn(vals_list)
                self.env['hr.employee'].browse(eid).write({'active':False})
        else:
            raise e
        
        return r