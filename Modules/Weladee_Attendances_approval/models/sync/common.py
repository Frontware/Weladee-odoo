# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

_CREATE = 0 # Create new relation
_UPDATE = 1 # Update relation
_CLEAR = 5 # Clear relation
_SET = 6 # Clear and then select relation

lang_dict = {
    'en_US':'english',
    'th_TH':'thai',
}

def add_translation(identifiers, model_id, translation_req, req, lang='en_US'):
    if not translation_req:
        return

    if lang not in lang_dict:
        return

    if isinstance(identifiers, int):
        identifiers = [identifiers]

    prefix = lang_dict[lang] + '_'
    for field in filter(lambda f: f.startswith(prefix), translation_req):
        field_name = field[len(prefix):]
        name = ','.join([model_id, field_name])
        value = translation_req[field]
        req.translation_obj._set_ids(name, 'model', lang, identifiers, value)
