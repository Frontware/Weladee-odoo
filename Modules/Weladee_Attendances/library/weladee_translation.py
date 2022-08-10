# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tools.translate import _

def allocate_holiday_tag(): return _(' employee tag %s')#4


def add_value_translation(rec, irobj, model, field, eng, thai):
    # Check if record could be created
    id = '%s,%s' % (model, field)
    if rec.id:
       irobj._set_ids(id,'model','en_US', [rec.id], eng or '')
       irobj._set_ids(id,'model','th_TH', [rec.id], thai or '')
