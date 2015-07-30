from openerp.osv import fields, osv
from lxml import  etree
from openerp.osv.orm import setup_modifiers
from openerp import SUPERUSER_ID
from openerp import workflow
from openerp.tools.translate import _

class attendance_attendance(osv.osv):
    _name = "attendance.attendance"
    _description = "Attendance"
    _order = "date"
    _rec_name = "date"
    '''
    This is the main record where all the attendance lines will be attached. It has state field. This state field will
    change to submitted state once all the attendance lines are submitted. It will become pending when any attendance line is reverted back to 
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

    def _check_attendance_record_done(self,cr,uid,attendance):
        '''Checks whether attendance record with attendance line 'line' needs to be validated to 'submitted' or not 
        '''
        #find id of line that has state pending.
        cr.execute('''
            select id from attendance_line where attendance_id = %s and state = 'pending'
        ''' %(attendance))
        list_ids = cr.fetchall()
        if  list_ids: #some lines are not submitted
            return False
        else:#All the lines are submitted
            return True
    
    def change_pending_done(self,cr,uid,ids,context=None):
        # First check all the lines are submitted or not
        for attendance in ids:
            if self._check_attendance_record_done(cr,uid,attendance):
                self.write(cr,uid,attendance,{'state':'submitted'},context)
            else:
                raise osv.except_osv(_('Invalid Action!'), _('One of the Project Attendance is taken but not submitted.'))
        return True
    
    def change_done_pending(self,cr,uid,ids,context=None):
        self.write(cr,uid,ids,{'state':'pending'},context)
        for attendance in ids:
            workflow.trg_delete(SUPERUSER_ID, 'attendance.attendance', attendance, cr)
            workflow.trg_create(SUPERUSER_ID, 'attendance.attendance', attendance, cr)
        return True
    
    def name_get(self, cr, uid, ids, context=None):
        res = super(attendance_attendance,self).name_get(cr,uid,ids,context)
        new_list = []
        for i in res:
            record = self.read(cr,uid,i[0],{'user_id'},context)
            new_list.append((i[0],record.get('user_id',False)[1]+'['+i[1]+']'))
        return new_list

    def reset_workflow(self,cr,uid,id,context):
        workflow.trg_delete(SUPERUSER_ID, 'attendance.attendance', id, cr)
        workflow.trg_create(SUPERUSER_ID, 'attendance.attendance', id, cr)
        return True
    
    
    #called from javascript
    def fetch_ids_user(self,cr,uid,context=None):
        list_ids = [] #final projects list
        if uid == SUPERUSER_ID:
            return []
        # Find the employee id of the user
        emp_id = self.pool.get('res.users').read(cr,uid,uid,{'emp_id'},context=context)
        project = self.pool.get('telecom.project')
        if emp_id.get('emp_id',False):
            # Find all the child_of managers of this user
            emp_child_id = self.pool.get('hr.employee').search(cr,uid,[('id','child_of',emp_id.get('emp_id',False)[0])])
            if emp_child_id:
                cr.execute('''
                    select project_id from telecom_project_hr_employee_rel where manager_id in %s
                ''',(tuple(emp_child_id),))
                project_id = cr.fetchall()
                for i in project_id:
                    list_ids.append(i[0])
        return [['id','in',list_ids]]
        
    
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
                'user_id':fields.many2one('res.users',string="Created By",states={'submitted':[('readonly',True)]}),
                'date':fields.date('Creation Date',states={'submitted':[('readonly',True)]}),
                'attendance_line':fields.one2many('attendance.line','attendance_id','Attendance',states={'submitted':[('readonly',True)]}),
                'state':fields.selection([
                                          ('draft','Draft'),
                                          ('pending','Pending'),
                                          ('submitted','Submitted')
                                          ], string = "State",),
                }
    
class attendace_line(osv.osv):
    _name = "attendance.line"
    _description = "Attendance Line"
    
    def change_pending_done(self,cr,uid,ids,context=None):
        self.write(cr,SUPERUSER_ID,ids,{'state':'submitted'},context)
#         for line in self.browse(cr,uid,ids,context):
#             workflow.trg_write(SUPERUSER_ID, 'attendance.attendance',line.attendance_id.id, cr)
        return True
    
    def change_done_pending(self,cr,uid,ids,context=None):
        self.write(cr,SUPERUSER_ID,ids,{'state':'pending'},context)
        attendance = self.pool.get('attendance.attendance')
        for line in self.browse(cr,uid,ids,context):
            workflow.trg_delete(SUPERUSER_ID, 'attendance.line', line.id, cr)
            workflow.trg_create(SUPERUSER_ID, 'attendance.line', line.id, cr)        
            if line.attendance_id.state == "submitted": #if the attendance record workflow is finished then reset it
                attendance.reset_workflow(cr,uid,line.attendance_id.id,context=context)
        return True
    
    
    _sql_constraints = [
        ('restrict_one_attendance_Line_perday', 'unique(date,project_id)', 'Attendance of a project can only be taken once a day !!! The attendance of this project is already taken today'),
    ]
    
    _rec_name = "date"
    
    _defaults = {
                 'state':'pending',
                 'date':fields.datetime.now,
                 'manager_id':lambda self,cr,uid,context:uid,
                 }
    
    '''
    1. This is basically attendance record of a project.
    2. Will be created only one per project per day
    3. Will be shared between the circle head and project manager but will only editted superly by circle user 
    '''
    
    _columns = {
                'date':fields.date('Date',states={'submitted':[('readonly',True)]},required=True),
                'manager_id':fields.many2one('res.users','Created By',states={'submitted':[('readonly',True)]},required=True),
                'project_id':fields.many2one('telecom.project',"Project",states={'submitted':[('readonly',True)]},required=True),
                'attendance_id':fields.many2one('attendance.attendance',"Attendance Record",states={'submitted':[('readonly',True)]},required=True),
                'state':fields.selection([
                                          ('pending','Pending'),
                                          ('submitted','Submitted')
                                          ],string = "State",states={'submitted':[('readonly',True)]}),
                'emploee_status_line':fields.one2many('employee.status.line','line_id','Employee Attendance',states={'submitted':[('readonly',True)]}),
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
    
    