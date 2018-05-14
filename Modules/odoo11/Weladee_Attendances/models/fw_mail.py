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
# send email function
# KPO 11/04/2012
# KPO 11/06/2013 migration to openerp 7.0

import logging
logger = logging.getLogger('fw_mail')
import re

#purpose : Return a list of the email addresses
#parameters : text
#return : a list of the email addresses  
#remarks : 
#2013-11-07 KPO add comments
def to_email(text):
    """Return a list of the email addresses found in ``text``"""
    if not text: return []
    return re.findall(r'([^ ,<@]+@[^> ,]+)', text)
    
#purpose : send email with template
#parameters : 
#-resid : resource id to link email
#-templatename : template name
#-templateid : templateid
#-htmlyn : html mode?
#return : none  
#remarks : 
#2013-11-07 KPO add comments
def fw_send_mail(self,cr,uid,resid,templatename=False,context=None,templateid=False,htmlyn=True):
    try:
        logger.info('sending...')     
        #loading template                   
        mail_templates = self.pool.get('email.template')
        if templatename:        
           try:
               temp1 = mail_templates.search(cr,uid,[('name','=',templatename)])[0]
           except:
               pass
        else:
           temp1 = templateid 
        logger.info('sending with template id= %s' % temp1)              
        #get template         
        mail = mail_templates.generate_email(cr, uid, temp1, resid, context=context)                 
        logger.info('create new mail..%s' % mail)
        mail_message = self.pool.get('mail.mail')
        references = False
        headers = {}
        newmail = mail_message.create(cr, uid, mail, context=context)
        mail_message.send(cr, uid, [newmail], context=context)
        
        logger.info('sent new mail..id=%s' % newmail)
    except Exception as e:
        logger.info('error send email:%s' % e)


