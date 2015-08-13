from openerp.osv import fields, osv
from datetime import datetime
from openerp import SUPERUSER_ID
from pytz import timezone
from lxml import  etree
from openerp.osv.orm import setup_modifiers

class attendance_summary(osv.osv_memory):
    _name = "attendance.summary"
    _description = "Print Attednance Summary"
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res=super(attendance_summary,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        corporate_ids = self.pool.get('attendance.attendance')._get_user_ids_group(cr,uid,'pls','telecom_corporate')
        if uid not in corporate_ids:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//field[@name='project_ids']"):
                node.set('domain',"[('project_manager.user_id','in',[uid])]")
                setup_modifiers(node, res['fields']['project_ids'])
                res['arch'] = etree.tostring(doc)
        return res
        
    def print_attendance(self,cr,uid,ids,context=None):
        assert len(ids) == 1 , "This option is supposed to be used for single id"
        cr.execute('''
            select employee_id from attendance_summary_hr_employee_rel where summary_id = %s
        ''' %(ids[0]))
        employee_ids = map(lambda x:x[0],cr.fetchall())
        cr.execute('''
            select project_id from attendnance_summary_telecom_project_rel where summary_id = %s
        ''' %(ids[0]))        
        project_ids = map(lambda x:x[0],cr.fetchall())
        info = self.read(cr,uid,ids[0],['from','to','print_summary'],context)
#         {'to': '2015-08-08', 'from': '2015-08-07', 'id': 5, 'print_summary': True}
        emp_obj = self.pool.get('employee.status.line')
        domain = [
                   ('employee_id','in',employee_ids),
                   ('line_id.project_id','in',project_ids),
                   ('date','>=',info.get('from',datetime.now(timezone('Asia/Kolkata')))),
                   ('date','<=',info.get('to',False))
               ]
        search_ids = emp_obj.search(cr,uid,domain, offset=0, limit=None, order=None, context=None, count=False)
        datas = {
             'ids': search_ids,
             'model': 'employee.status.line',
             'form': info
                 }
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name': 'attendance_dashboard_aeroo',
                    'datas': datas,
                    'context':context
                }    
    _defaults = {
                 "from":datetime.now(timezone('Asia/Kolkata')),
                 "to":datetime.now(timezone('Asia/Kolkata'))
                 }
    _columns ={
               'employee_ids':fields.many2many('hr.employee','attendance_summary_hr_employee_rel','summary_id','employee_id',string = "Employees"),
               'project_ids':fields.many2many('telecom.project','attendnance_summary_telecom_project_rel','summary_id','project_id',string = "Projects"),
               'from':fields.date('From',required=True),
               'to':fields.date('To',required=True),
               }
    