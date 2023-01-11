# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

base_url = 'https://www.weladee.com/skill/type/'

lang_dict = {
    'en_US':'english',
    'th_TH':'thai',
}

def add_translation(obj, translation_req, lang='en_US'):
    if not obj:
        return

    if not translation_req:
        return
    
    if lang not in lang_dict:
        return
        
    prefix = lang_dict[lang] + '_'
    for field in filter(lambda f: f.startswith(prefix), translation_req):
        value = translation_req[field]
        obj.with_context(lang=lang).name = value
