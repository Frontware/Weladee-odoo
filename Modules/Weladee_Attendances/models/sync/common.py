# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

base_url = 'https://www.weladee.com/skill/type/'

_CREATE = 0 # Create new relation
_UPDATE = 1 # Update relation
_CLEAR = 5 # Clear relation
_SET = 6 # Clear and then select relation

lang_dict = {
    'en_US':'english',
    'th_TH':'thai',
}

def add_translation(rec, translation_req, lang='en_US'):
    if not translation_req:
        return
    
    if lang not in lang_dict:
        return
       
    prefix = lang_dict[lang] + '_'
    for field in filter(lambda f: f.startswith(prefix), translation_req):
        field_name = field[len(prefix):]
        value = translation_req[field]
        rec.with_context({'lg':lang,'updateLang':True}).write({field_name: value})
