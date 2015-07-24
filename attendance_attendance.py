from openerp.osv import fields, osv

class attendance_attendace(osv.osv):
    _name = "attendance.attendance"
    _description = "Attendance"
    
    '''
    This is the main record where all the attendance lines will be attached. It has state field. This state field will
    change to submitted state once all the attendance lines are submitted. It will become pending when any attendace line is reverted back to 
    pending state. 
    
    A project manager or a circle head will be able to create only a single attendance record per day.
    If a circle head takes the attendance for a particular project then the project manager will just be able to view it but not edit it
    For this purpose ir.rule will be added on attendance.line so that project manager can only edit those records that have been made by them
    
    In short-: 
    1. There will only be a single attendance line for each project per day.
    2. There will only be a single attendance.attendance record per project manager and circle head per day
    3. Directors cannot take attendance
    
    '''
    _columns = {
                'user_id':fields.many2one('res.users',string="Created By"),
                'date':fields.date('Creation Date'),
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
        3. This will be the lines that the corporate will see for the attendace report
    '''
    _columns ={
               'employee_id':fields.many2one('hr.employee',"Employee Name"),
               'designation':fields.related('employee_id','job_id',type="many2one",relation="hr.job",string="Designation"),
               'state':fields.state([
                                     ('present','Present'),
                                     ('absent','Absent'),
                                     ('leave','Leave'),
                                     ('terminated','Terminated'),
                                     ('tour',"On Tour"),
                                     ],string = "Status" ),
               'remarks':fields.text('Remarks'),
               }
    
    