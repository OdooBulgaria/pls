from openerp.osv import fields, osv
from lxml import  etree
from openerp.osv.orm import setup_modifiers

class attendance_attendance(osv.osv):
    _name = "attendance.attendance"
    _description = "Attendance"
    _order = "date"
    
    '''
    This is the main record where all the attendance lines will be attached. It has state field. This state field will
    change to submitted state once all the attendance lines are submitted. It will become pending when any attendace line is reverted back to 
    pending state. 
    
    A project manager or a circle head will be able to create only a single attendance record per day.
    If a circle head takes the attendance for a particular project then the project manager will just be able to view it but not edit it
    For this purpose ir.rule will be added on attendance.line so that project manager can only edit those records that have been made by them
    
    In short-: 
    
    1. There will only be a single attendance line for each project per day.
    2. There will only be a single attendance.attendance record per user per day
    3. Directors cannot take attendance
    4. The attendance.attendace field will only be accessible by the corporate account
    5. Search View --> filter by date,group by user_id only for corporate users and circle heads
    '''

    _sql_constraints = [
        ('restrict_one_attendance_peruser', 'unique(user_id,date)', 'A user can create a single attendance record/day!'),
    ]

    #called from javascript
    def fetch_ids_user(self,cr,uid,context=None):
        emp_id = self.pool.get('res.users').read(cr,uid,uid,{'emp_id'},context=context)
        if emp_id:
            print "========================================",emp_id
            return 1
        cr.execute('''
            
        ''')
        return 1
        
    
    # The date field is only accessible by the corporate account
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res=super(attendance_attendance,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type =="form":
            groups = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'pls', 'telecom_corporate')[1]
            user_group=self.pool.get('res.groups').browse(cr,uid,groups)
            user_ids=map(int,user_group.users or [])            
            if not(uid in user_ids):
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//field[@name='date']"):
                    node.set('readonly','1')
                    setup_modifiers(node, res['fields']['date'])
                    res['arch'] = etree.tostring(doc)
        return res
    
    _defaults = {
                 'date':fields.datetime.now,
                 'user_id':lambda self,cr,uid,context:uid,
                 'state':"draft"
                 }
    
    _columns = {
                'user_id':fields.many2one('res.users',string="Created By"),
                'date':fields.date('Creation Date',read=['telecom_circle_head','telecom_project_manager']),
                'attendance_line':fields.one2many('attendance.line','attendance_id','Attendance'),
                'state':fields.selection([
                                          ('draft','Draft'),
                                          ('pending','Pending'),
                                          ('submitted','Submitted')
                                          ], string = "State")
                }
    
class attendace_line(osv.osv):
    _name = "attendance.line"
    _description = "Attendance Line"
    
    '''
    1. This is basically attendance record of a project.
    2. Will be created only one per project per day
    3. Will be shared between the circle head and project manager but will only editted superly by circle user 
    '''
    
    _columns = {
                'date':fields.date('Date'),
                'manager_id':fields.many2one('res.users','Created By'),
                'project_id':fields.many2one('telecom.project',"Project"),
                'attendance_id':fields.many2one('attendance.attendance',"Attendance Record"),
                'state':fields.selection([
                                          ('draft','Draft'),
                                          ('pending','Pending'),
                                          ('submitted','Submitted')
                                          ],string = "State"),
                'emploee_status_line':fields.one2many('employee.status.line','line_id','Employee Attendance'),
                }

class employee_status_line(osv.osv):
    _name = "employee.status.line" 
    _description = "Employee Status Line"
    
    '''
        In this the employee today's attendance will be taken
        1. Only one employee status line per day.
        2. If attendance already taken and then the employee is transferred to another project then the existing attendace line
        will be deleted and a new employee.status.line will be created for that day
        3. This will be the lines that the corporate will see for the attendance report
    '''
    _columns ={
               'employee_id':fields.many2one('hr.employee',"Employee Name"),
               'designation':fields.related('employee_id','job_id',type="many2one",relation="hr.job",string="Designation"),
               'state':fields.selection([
                                     ('present','Present'),
                                     ('absent','Absent'),
                                     ('leave','Leave'),
                                     ('terminated','Terminated'),
                                     ('tour',"On Tour"),
                                     ],string = "Status" ),
               'remarks':fields.text('Remarks'),
               'line_id':fields.many2one('attendance.line'),
               }
    
    