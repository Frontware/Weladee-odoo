# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

_logger = logging.getLogger(__name__)

import pytz
from datetime import datetime

from odoo import osv
from odoo import models, fields, api, _

from odoo.addons.Weladee_Attendances.models.sync.weladee_base import renew_connection, sync_loginfo, sync_logerror, sync_logdebug, sync_logwarn, sync_stop, sync_has_error
from odoo.addons.Weladee_Attendances_skill.models.sync.weladee_skill_type import sync_skill_type, delete_skill_type
from odoo.addons.Weladee_Attendances_skill.models.sync.weladee_skill_level import sync_skill_level, delete_skill_level
from odoo.addons.Weladee_Attendances_skill.models.sync.weladee_skill import sync_skill, delete_skill
from odoo.addons.Weladee_Attendances_skill.models.sync.weladee_skill_employee import sync_skill_employee

class weladee_attendance_skill(models.TransientModel):
    _inherit="weladee_attendance.synchronous"

    def init_param(self):
        r = super(weladee_attendance_skill, self).init_param()

        # for skill
        r.skill_type_obj = False
        r.skill_level_obj = False
        r.skill_obj = False
        r.skill_employee_obj = False
        r.translation_obj = False

        return r    

    def do_sync_options(self, req):
        super(weladee_attendance_skill, self).do_sync_options(req)

        if req.config.sync_skill and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync, "Start sync...Skill Type")

            req.skill_type_obj = self.env['hr.skill.type']
            req.translation_obj = self.env['ir.translation']

            sync_skill_type(req)

        if req.config.sync_skill and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync, "Start sync...Skill Level")

            req.skill_type_obj = self.env['hr.skill.type']
            req.skill_level_obj = self.env['hr.skill.level']
            req.translation_obj = self.env['ir.translation']

            sync_skill_level(req)

        if req.config.sync_skill and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync, "Start sync...Skill")

            req.skill_type_obj = self.env['hr.skill.type']
            req.skill_obj = self.env['hr.skill']
            req.translation_obj = self.env['ir.translation']

            sync_skill(req)

        if req.config.sync_skill and not sync_has_error(req.context_sync):
            sync_logdebug(req.context_sync, "Start sync...Skill Employee")

            req.skill_type_obj = self.env['hr.skill.type']
            req.skill_level_obj = self.env['hr.skill.level']
            req.skill_obj = self.env['hr.skill']
            req.skill_employee_obj = self.env['hr.employee.skill']

            sync_skill_employee(req)

    def do_delete_options(self, req):
        if req.config.sync_skill:
            delete_skill(req)
            delete_skill_level(req)
            delete_skill_type(req)

        super(weladee_attendance_skill, self).do_delete_options(req)
