from openerp.osv import fields, osv
from datetime import datetime
from pytz import timezone

class cron_report(osv.osv):
    _name = "cron.report"
    _rec_name = "date"
    _defaults = {
                 'date':datetime.now(timezone('Asia/Kolkata'))
                 }
    _columns = {
                    'date':fields.date('Date'),
                    'unclear_attendance_lines':fields.many2many('mail.message','cron_report_mail_message_rel_attendance_line','report_id','message_id','Unsubmitted Project Attendance'),
                    'unclear_attendance_records_passed':fields.many2many('mail.message','cron_report_mail_message_rel_attendance_attendance_passed','report_id','message_id','Uncleared Attendances(Successfully Closed)'),
                    'unclear_attendance_records_failed':fields.many2many('mail.message','cron_report_mail_message_rel_attendance_attendance_failed','report_id','message_id','Uncleared Attendances(Not Closed Successfully)'),
                    'project_ids':fields.many2many('telecom.project','cron_report_telcom_project_rel','report_id','project_id','WIP projects for which attendance was not taken')
                }
                