# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
import pytz

def _convert_to_tz_time(self, date_string_with_time):
    '''
    convert user datetime to UTC
    '''
    date_v = datetime.datetime.strptime(date_string_with_time,'%Y-%m-%d %H:%M:%S')
    user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
    date_tz = user_tz.localize(date_v)  # Add "+hh:mm" timezone
    return date_tz.astimezone(pytz.utc)  # Convert to UTC

