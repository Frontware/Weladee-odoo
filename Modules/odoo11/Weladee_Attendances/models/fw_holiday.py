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
from odoo import models, fields, api

import datetime
import time
import pytz

from . import fw_mail as fw_send_mail

class hr_holidays(models.Model):
    _inherit = 'hr.holidays'
    _description = 'Leave'      
    
    dates = fields.Date(string='Start Date'),
    datee = fields.Date(string='End Date'),
    datesp = fields.Selection([('08:00','Morning'),('13:00','Afternoon')],string='Start time'),
    dateep = fields.Selection([('12:00','Morning'),('17:00','Afternoon')],string='End time')

    #purpose : override check holidays when manager 
    #parameters : openerp standard
    #return : openerp standard
    #remarks : 
    #2013-11-07 KPO add comments              
    def check_holidays(self, cr, uid, ids, context=None):
        #if manager
        if self.check_is_hr_manager_yn(cr, uid, ids): 
           return True
        else:
           return super(hr_holidays, self).check_holidays(cr, uid, ids, context)
        
    #purpose : send email to hr when request submit
    #parameters : openerp standard
    #-templatename 
    #return : none
    #remarks : 
    #2013-11-07 KPO add comments  
    #2014-12-15 KPO add duration            
    def sendmailhr(self, cr, uid, ids, templatename, context=None):
        if not context:
           context={}
        object = self.browse(cr,uid,ids[0])
        context['d-from']=time.strftime('%d/%m/%Y',time.strptime(object.date_from,'%Y-%m-%d %H:%M:%S'))
        context['d-to']=time.strftime('%d/%m/%Y',time.strptime(object.date_to,'%Y-%m-%d %H:%M:%S'))
        context['d-duration']= '%s day(s)' % object.number_of_days_temp 
        fw_send_mail(self, cr, uid, ids[0], templatename=templatename,context=context)
    
    #purpose : when click urgent leave
    #parameters : openerp standard
    #return : openerp standard
    #remarks : 
    #2013-11-07 KPO add comments              
    def urgent_leave(self, cr, uid, ids, *args):
        return self.write(cr, uid, ids, {'state':'validate'})

    #purpose : get holiday date from date + periodname
    #parameters : openerp standard
    #-datename : date enter
    #-periodname : morning,afternoon 
    #-vals : dictonary of form
    #return : openerp standard
    #remarks : 
    #2013-11-07 KPO add comments                      
    def _get_holidaydate(self, cr, uid, datename, periodname, vals):
        msdate=''
        if not vals.has_key(datename):
           return False 
        if not vals[datename]:
           return False
        msdate=vals[datename]
        if vals.has_key(periodname):
           if not vals[periodname]:
              vals[periodname]='00:00' 
           msdate+=' %s:00'%vals[periodname]
        #save UTC in db,
        #calculate timezone
        mytimze = self.pool.get('res.users').browse(cr, uid, uid).tz
        mtime = datetime.datetime.strptime(msdate,'%Y-%m-%d %H:%M:%S')
        if mytimze:
           mlocaltime = pytz.timezone(mytimze)        
           mlocal_dt = mlocaltime.localize(mtime,is_dst=None)
           mutc_dt = mlocal_dt.astimezone(pytz.utc)
        else:
           mutc_dt=mtime
        return mutc_dt

    #purpose : check number of day count 
    #parameters :
    #-datef - date from
    #-datefp - date from period 
    #-datet - date to
    #-datetp - date to period 
    #return : number of days
    #remarks : 
    #2013-11-07 KPO add comments                      
    def _get_holiday_count(self, datef, datefp, datet, datetp):
        if datef==False or datet==False:
           return 0        
        mtimedelta=datet-datef
        mdiff=mtimedelta.days
        if datefp=='08:00' and datetp=='12:00':
           mdiff+=0.5 
        elif datefp=='08:00' and datetp=='17:00':
           mdiff+=1    
        elif datefp=='13:00' and datetp=='17:00':
           mdiff+=0.5    
        elif datefp=='13:00' and datetp=='12:00':
           mdiff+=1               
        return mdiff         
        
    #purpose : when create leave, always has dates + datee
    #     allocate will has not
    #parameters : openerp standard
    #return : openerp standard
    #remarks : 
    #2013-11-07 KPO add comments                      
    def create(self, cr, uid, vals, context=None):
        bleaveyn=False        
        if vals.has_key('dates'):
           vals['date_from']=self._get_holidaydate(cr, uid, 'dates', 'datesp', vals)
           bleaveyn=True
        if vals.has_key('datee'):
           vals['date_to']=self._get_holidaydate(cr, uid, 'datee', 'dateep', vals)
           bleaveyn=True
        if bleaveyn:
           vals['number_of_days_temp']=self._get_holiday_count(\
                                    vals['date_from'],\
                                    vals['datesp'],\
                                    vals['date_to'],\
                                    vals['dateep'])
        else:
           vals['type']='add' 
        
        return super(hr_holidays, self).create(cr, uid, vals)

    #purpose : when update leave, always has dates + datee
    #     allocate will has not
    #parameters : openerp standard
    #return : openerp standard
    #remarks : 
    #2013-11-07 KPO add comments       
    def write(self, cr, uid, ids, vals, context=None):
        mhol=self.browse(cr, uid, ids)[0] 
        if not vals.has_key('datesp'):
           vals['datesp']=mhol.datesp 
        if not vals.has_key('dates'):
           vals['dates']=mhol.dates           
        vals['date_from']=self._get_holidaydate(cr, uid, 'dates', 'datesp', vals)
               
        if not vals.has_key('dateep'):
           vals['dateep']=mhol.dateep           
        if not vals.has_key('datee'):
           vals['datee']=mhol.datee
        vals['date_to']=self._get_holidaydate(cr, uid, 'datee', 'dateep', vals)

        if not vals.has_key('number_of_days_temp'):
           vals['number_of_days_temp']=mhol.number_of_days_temp
        
        if vals['date_from'] and vals['date_to']:
           vals['number_of_days_temp']=self._get_holiday_count(\
                                    vals['date_from'],\
                                    vals['datesp'],\
                                    vals['date_to'],\
                                    vals['dateep'])
        return super(hr_holidays, self).write(cr, uid, ids, vals)

    #purpose : when date from change
    #parameters : openerp standard
    #-date_from - date from
    #-datep_from - date from period 
    #-date_to - date to
    #-datep_to - date to period 
    #return : openerp standard
    #remarks : 
    #2013-11-07 KPO add comments       
    def onchange_datee_from(self, cr, uid, ids, date_to, date_from, datep_to, datep_from):
        result = {}
        if date_to and date_from and datep_to and datep_from:
            vals={}
            vals['dates']=date_from
            vals['datee']=date_to
            vals['datesp']=datep_from
            vals['dateep']=datep_to
            diff_day = self._get_holiday_count(self._get_holidaydate(cr, uid, 'dates', 'datesp', vals),\
                                               datep_from,\
                                               self._get_holidaydate(cr, uid, 'datee', 'dateep', vals),datep_to)
            result['value'] = {
                'number_of_days_temp': diff_day
            }
            return result
        result['value'] = {
            'number_of_days_temp': 0,
        }
        return result

    #purpose : show error of holiday
    #parameters : openerp standard
    #-msg : message want to show
    #return : none
    #remarks : 
    #2013-11-07 KPO add comments      
    def alert_holidays(self, cr, uid, ids, smsg):
        raise osv.except_osv('Warning!',smsg)
        return True

    #purpose : check current user is hr manager ?
    #parameters : openerp standard
    #return : true if current user is hr manager
    #remarks : 
    #2013-11-07 KPO add comments        
    def check_is_hr_manager_yn(self, cr, uid, ids):
        user_pool = self.pool.get('res.users')
        user_browse = user_pool.browse(cr,uid,[uid])
        bis_hr_manageryn = False  
        for group in user_browse[0].groups_id:
            print('group= %s' %str(group.name) )
            appname=''
            if group.category_id:
               appname=group.category_id.name
            print('app = %s' %str(appname) )
            if group.name == "Manager" and appname=='Human Resources':
               bis_hr_manageryn = True
               print('this user is manager')
               break
        return bis_hr_manageryn 

    #purpose : check number of days from now and current date from
    #parameters : openerp standard
    #return : number of days
    #remarks : 
    #2013-11-07 KPO add comments  
    def check_days_holidays(self, cr, uid, ids):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        for record in self.browse(cr, uid, ids):
            if record.date_from != False:
                from_dt = datetime.datetime.strptime(record.date_from, DATETIME_FORMAT)
                timedelta = datetime.datetime.now() - from_dt
                diff_day = abs(timedelta.days)
                print(from_dt)
                print(diff_day)
                return diff_day
            else:
                return 7 
                 
hr_holidays()