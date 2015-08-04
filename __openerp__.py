# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'PLS',
    'version': '0.1',
    'category': 'telecom management',
    'sequence':1,
    'summary': 'telecom',
    'description': """
    PLS Project Management
    """,
    'author': 'J & G Infosystems',
    'website': 'www.jginfosystems.com',
    'depends': ['base','hr','complaint_system'],
    'data': [
             'pls_data.xml',
             'security/pls_security.xml',
             'telecom_view.xml',
             'work_description.xml',
             'hr_view.xml',
             'res_partner_view.xml',
             'security/ir.model.access.csv',
             'res_users_view.xml',
             'pls.xml',
             'attendance_attendance_view.xml',
             'attendance_workflow.xml',
             'res_config_view.xml'
             ],
    'demo': [],
    'test': [],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: