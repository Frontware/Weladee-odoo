# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tools.translate import _

def allocate_holiday_tag(): return _(' employee tag %s')#4


def add_value_translation(rec, field, eng, thai):
    # Check if record could be created
    if rec.id:
       rec.with_context({'lang':'en_US','updateLang':True}).name = eng
       rec.with_context({'lang':'th_TH','updateLang':True}).name = thai