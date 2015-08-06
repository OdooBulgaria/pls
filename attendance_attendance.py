from openerp.osv import fields, osv
from lxml import  etree
from openerp.osv.orm import setup_modifiers
from openerp import SUPERUSER_ID
from openerp import workflow
from openerp.tools.translate import _
import time
from datetime import datetime
from pytz import timezone

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

    def submits_all_lines(self,cr,uid):
        '''
            Submits all the attendance.line created today and return their ID's
        '''
        #search for all the attendance.line that were created and left in pending state today
        line_ids = self.pool.get('attendance.line').search(cr,uid,[('state','=','pending'),('date','=',(time.strftime('%Y-%m-%d')))], offset=0, limit=200, order=None, context=None, count=False)
        for line in line_ids: 
            workflow.trg_validate(SUPERUSER_ID, 'attendance.line', line, 'change_pending_done', cr)
        return line_ids

    def log_complaint(self,cr,uid,emp_id,complaint,context=None):
        obj = self.pool.get('mail.message')
        id = obj.create(cr,uid,{
                                 'employee_id':emp_id,
                                 'complaint':complaint,
                                 },context)
        obj.log_complaint(cr,uid,[id],context)
        return id
        
    def create_message_cron(self,cr,uid,cron_id,message_id,field,context=None):
        '''
            Takes in the cron report id,message and the field to which the message has to be logged in the cron report
            and then attaches the message to the appropriate field in cron report
            
        '''
        self.pool.get('cron.report').write(cr,uid,cron_id,{
                                                           field:[(4,message_id)]
                                                           },context)
        
    def submit_all_attendance(self,cr,uid):
        '''
            Submits all the attendance.attendance created today and returns their ID's
        '''
        
        #search for all the attendance.attendance that were created and left in pending state today
        attendance_ids = self.pool.get('attendance.attendance').search(cr,uid,[('state','=','pending'),('date','=',(time.strftime('%Y-%m-%d')))], offset=0, limit=200, order=None, context=None, count=False)
        ids_passed,ids_failed = [],[]
        
        for attendance in attendance_ids: 
            try:
                workflow.trg_validate(SUPERUSER_ID, 'attendance.attendance', attendance, 'change_pending_done', cr)
                ids_passed.append(attendance)
            except:
                ids_failed.append(attendance)
                
        return [ids_passed,ids_failed]
    
    def _get_unattended_project(self,cr,uid):
        '''
        This module returns the projects for which the attendance was not taken or False if all the attendances were
        '''
        
        line_obj = self.pool.get('attendance.line')
        project = self.pool.get('telecom.project')
        #all wip projects
        
        all_project_ids = project.search(cr,uid,[('state','=','wip')], offset=0, limit=200, order=None, context=None, count=False)
        
        #all projects for which attendance was taken
        attendance_taken = line_obj.search(cr,uid,[('date','=',(time.strftime('%Y-%m-%d')))], offset=0, limit=200, order=None, context=None, count=False)
        project_ids = []
        if attendance_taken:
            project_ids = line_obj.read(cr,uid,attendance_taken,['project_id'],context=None)
        attendance_taken = map(lambda x:x.get('project_id')[0],project_ids)
        if not (set(all_project_ids) == set(attendance_taken)):
            diff = set(all_project_ids) - set(attendance_taken)
            return diff
        else:
            return False
        
    def run_cron(self,cr,uid,ids=None,context=None):
        line_obj = self.pool.get('attendance.line')
        attendance_obj  = self.pool.get('attendance.attendance')
        cron_obj = self.pool.get('cron.report')
        project_obj = self.pool.get('telecom.project')
        
        #Create a cron report
        cron_id = cron_obj.create(cr,uid,{},context)
        # Submits all the attendance.line created today
        line_ids = self.submits_all_lines(cr,uid)
        if line_ids:
            #Create a notification that the attendance.line was not submitted in the Cron report
            #Log a complaint for the project manager who created this attendance.line
            line_brw = line_obj.browse(cr,uid,line_ids,context)
            for brw in line_brw:
#                 self.create_message_cron(cr,uid)
                complaint = "The attendance for the project "+brw.project_id.name+ " was created by the manager "+brw.manager_id.name+ " but not submitted. It was submitted by cron job"
                message_id = self.log_complaint(cr,uid,brw.manager_id.emp_id.id,complaint,context={'default_subtype_complaint':True})
                self.create_message_cron(cr,uid,cron_id,message_id,'unclear_attendance_lines',context)
        
        #Submits all the attendance.attendance 
        attendance_ids = self.submit_all_attendance(cr,uid)
        #Check the one's that were closed successfully
        if attendance_ids[0]:
            attendacne_passed = attendance_obj.browse(cr,uid,attendance_ids[0],context)
            for brw in attendacne_passed:
                complaint = "The attendance record created by " + brw.user_id.name + " was successfully closed by the cron job and not by the manager."
                message_id = self.log_complaint(cr,uid,brw.user_id.emp_id.id,complaint,context={'default_subtype_complaint':True})
                self.create_message_cron(cr,uid,cron_id,message_id,'unclear_attendance_records_passed',context)
        #Check the one's that were not closed successfully                
        if attendance_ids[1]:
            attendacne_failed = attendance_obj.browse(cr,uid,attendance_ids[0],context)
            for brw in attendacne_passed:
                complaint = "The attendance record created by " + brw.user_id.name + " was not closed by the manager.This implies that there are project for which the  manager either did not create the attendance or submit it\n The cron job also failed to close the attendance record due to some reason"
                message_id = self.log_complaint(cr,uid,brw.user_id.emp_id.id,complaint,context={'default_subtype_complaint':True})
                self.create_message_cron(cr,uid,cron_id,message_id,'unclear_attendance_records_failed',context)                            
        
        # Look for the projects for which the attendance was not taken and create a cron report log and complaint for project manager
        project_ids = self._get_unattended_project(cr,uid)    
        if project_ids:
            project_ids = list(project_ids) #those project for which attendance was not taken
            cron_obj.write(cr,uid,cron_id,{
                                           'project_ids':[(6,0,project_ids)]
                                           })
            for project in project_obj.browse(cr,uid,project_ids,context):
                for manager in project.project_manager:
                    complaint = "The project manager "+ manager.name + " did not submit the attendance for the project " + project.name  
                    message_id = self.log_complaint(cr,uid,manager.id,complaint,context={'default_subtype_complaint':True})                
        return True
    
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
        corporate_ids = self.pool.get('attendance.attendance')._get_user_ids_group(cr,uid,'pls','telecom_corporate')
        if uid in corporate_ids:
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
        
    def _get_user_ids_group(self,cr,uid,module,group_xml_id):
        '''
        This method takes in the module and xml_id of the group and return the list of users present in that group
        '''
        groups = self.pool.get('ir.model.data').get_object_reference(cr, uid, module, group_xml_id)[1]
        user_group=self.pool.get('res.groups').browse(cr,uid,groups)
        user_ids=map(int,user_group.users or [])
        return user_ids                    
    
    
    # The date field is only accessible by the corporate account
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res=super(attendance_attendance,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        if view_type =="form":
            user_ids=self._get_user_ids_group(cr,SUPERUSER_ID,'pls','telecom_corporate')      
            if not(uid in user_ids):
                doc = etree.XML(res['arch'])
                for node in doc.xpath("//field[@name='date']"):
                    node.set('readonly','1')
                    setup_modifiers(node, res['fields']['date'])
                    res['arch'] = etree.tostring(doc)
        return res
    
    _defaults = {
                 'date':datetime.now(timezone('Asia/Kolkata')),
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
    
    def create(self,cr,uid,vals,context=None):
        if vals.get('date',False) and vals.get('emploee_status_line',False) :
            employee_status_line = []
            for line in vals.get('emploee_status_line',False):
                line[2]['date'] = vals.get('date',False)
                employee_status_line.append(line)
            vals['emploee_status_line'] = employee_status_line
        return super(attendace_line,self).create(cr,uid,vals,context)
    
    def write(self,cr,uid,ids,vals,context=None):
        for id in ids:
            line_obj = self.pool.get('employee.status.line')
            if vals.get('date',False):
                lines = line_obj.search(cr,SUPERUSER_ID,[('line_id','=',id)], offset=0, limit=1000, order=None, context=None, count=False)
                line_obj.write(cr,uid,lines,{'date':vals.get('date',False)},context)
        return super(attendace_line,self).write(cr,uid,ids,vals,context)
        
    def _check_project_exist(self,cr,uid,project_id):
        '''
            return the id, of the attendance line if taken today
        '''
        id = self.search(cr,SUPERUSER_ID,[('project_id','=',project_id),('date','=',(time.strftime('%Y-%m-%d')))], offset=0, limit=1, order=None, context=None, count=False)
        return id
    
    #called from javascript while takiing attendance
    def check_line_exist(self,cr,uid,project_id,context=None):
        '''
        It checks whether the project for which attendance is being taken,whether attendance for that project has already been taken or not
        * If the attendance for that project is already taken it then checks of the same project manager has taken the attendance.
            - if the same project manager has taken the attendance then  it returns [attendance_line id ,True]
            - if the same project manager has not taken the attendance then  it returns [attendance_line id , False]
        * If the attendance for the project is not taken then it return False simply
        '''
        
        line_id = self._check_project_exist(cr,uid,project_id)
        if line_id:
            manager_id = self.read(cr,SUPERUSER_ID,line_id[0],['manager_id'],context)
            if manager_id and manager_id.get('manager_id',False) and manager_id.get('manager_id',False)[0] == uid :return [line_id,True]
            else :return [line_id,False]
        else: return False
    
    def _check_attendance_record_created(self,cr,uid):
        id = self.pool.get('attendance.attendance').search(cr,SUPERUSER_ID,[('user_id','=',uid),('date','=',(time.strftime('%Y-%m-%d')))], offset=0, limit=1, order=None, context=None, count=False)
        return id
    
    def save_attendance_line(self,cr,uid,ids,context=None):
        '''
            if attendance record exists then just attach the line to the existing attendance record else create a attendance record and then attach the line
        '''
        # ids --> [1]
        corporate_ids = self.pool.get('attendance.attendance')._get_user_ids_group(cr,uid,'pls','telecom_corporate')
        if uid not in corporate_ids:
            info = self.pool.get('res.users').read(cr,SUPERUSER_ID,uid,['override_time','allowed_attendance_time'],context)
            if not info.get('override_time',False): # if the overriding power is not allowed check the time
                current_time = datetime.now(timezone('Asia/Kolkata'))
                hours = current_time.hour 
                minutes = float(current_time.minute)/float(60)
                time = hours+minutes
                if time >= info.get('allowed_attendance_time',0):
                    raise osv.except_osv(_('Sorry!'), _('Time to submit attendance is over'))
        assert len(ids) == 1,'This option should only be used for a single id at a time'
        user_id = self.read(cr,uid,ids[0],['manager_id'],context)
        attendance_created = self._check_attendance_record_created(cr,user_id.get('manager_id',False)[0])
        attendance_obj = self.pool.get('attendance.attendance')
        if attendance_created:
            self.write(cr,SUPERUSER_ID,ids,{'attendance_id':attendance_created[0]},context)
        else:
            attendance_obj.pool.get('attendance.attendance').create(cr,SUPERUSER_ID,{
                                                                  'user_id':user_id.get('manager_id',False)[0],
                                                                  'date':datetime.now(timezone('Asia/Kolkata')),
                                                                  'attendance_line':[(6,0,ids)]
                                                                  },context)
        return True
    
    def _get_employee_id(self,cr,uid,context=None):
        '''
            takes in a single user id and returns a employee_id
        '''
        cr.execute('''
            select id from hr_employee where resource_id = (select id from resource_resource where user_id = %s) 
        ''' %(uid))
        user_id = cr.fetchone()
        return user_id and user_id[0] or False
    
    def close_attendance_record(self,cr,uid,context=None):
        '''

            - This method takes the uid and searches for all the project related to that uid
            - Then it looks for all the attendace.line which were created today,state=submitted and were related to the uid 
            - If the length of both is same then it closes the attendance record created by the uid
            - If all the project attendance are taken then it will close the attendance record otherwise will send a list of all the project
            - for which either attendance is not taken or not submitted
            
            - In case of cron job ---> First all the attendance.line will be submitted and their corresponding attendance.attendance will be closed if the project manager has taken all his attendance
            - To close the attendance records this function will be called
            - Thus this functional will now return the list of all the projects for which the project manager did not create the attendance
            - This will all be logged as a complaint
            - All the unsubmitted attendance.lines will also be logged as complaints
            
        '''
        
        employee_id = self._get_employee_id(cr, uid, context)
        if employee_id:
            cr.execute('''
                select project_id from telecom_project_hr_employee_rel as rel left join telecom_project as project on rel.project_id = project.id where rel.manager_id = %s and project.state = 'wip' 
            ''' %(employee_id))
            all_project_ids = map(lambda x: x[0],cr.fetchall()) # All the project in which the manager is involved
            if all_project_ids:
                project_lines_taken = self.search(cr,SUPERUSER_ID,[('state','=','submitted'),('project_id.project_manager','in',[employee_id]),('date','=',(time.strftime('%Y-%m-%d')))], offset=0, limit=200, order=None, context=None, count=False)
                if project_lines_taken:
                    project_ids_taken = map(lambda x: x.project_id.id,self.browse(cr,uid,project_lines_taken,context))
                    if set(project_ids_taken) == set(all_project_ids):
                        attendance_id = self._check_attendance_record_created(cr, uid)
                        if attendance_id:
                            workflow.trg_validate(SUPERUSER_ID, 'attendance.attendance', attendance_id[0], 'change_pending_done', cr)
                            return True
                    else:
                        return set(all_project_ids) - set(project_ids_taken)  
        else:
            return False # This indicates that there is no employee attached to the uid and should be logged in the cron report
        
        
    def change_pending_done(self,cr,uid,ids,context=None):
        corporate_ids = self.pool.get('attendance.attendance')._get_user_ids_group(cr,uid,'pls','telecom_corporate')
        self.save_attendance_line(cr,uid,ids,context)
        self.write(cr,SUPERUSER_ID,ids,{'state':'submitted','submitted_by':uid},context)
        if uid not in corporate_ids: # This will allow the admin to be able to submit anyone's project attendance line
            self.close_attendance_record(cr,uid,context)
        else:
            # it is a corporate user
            # check all the project lines are submitted
            # This ensures that when cron job is run the no log is created for super user id becasue first all the attendance.line are closed
            # and in the process the admin attendance record is closed
            attendance_id = self._check_attendance_record_created(cr, uid)
            if attendance_id:
                project_ids_pending = self.search(cr,SUPERUSER_ID,[('state','=','pending'),('attendance_id','in',attendance_id),('date','=',(time.strftime('%Y-%m-%d')))], offset=0, limit=200, order=None, context=None, count=False)
                if not project_ids_pending:
                    return workflow.trg_validate(SUPERUSER_ID,'attendance.attendance',attendance_id[0],"change_pending_done",cr)
        return True
    
    def change_done_pending(self,cr,uid,ids,context=None):
        self.write(cr,SUPERUSER_ID,ids,{'state':'pending','submitted_by':False},context)
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
    
    #context passed from javascript
    def _get_project_id(self,cr,uid,context):
        if context.get('project_id',False):
            return context.get('project_id',False)
        else:
            return False
        
    #Automatically populate the all the employees in this project on create
    def _get_employee_status_line(self,cr,uid,context):
        project_id = context.get('project_id',False)
        list_return = []
        if project_id:
            cr.execute('''
                select id,job_id,parent_id from hr_employee where current_project = %s 
            ''' %(project_id))
            employee_id = cr.fetchall()
            for id in employee_id:
                list_return.append((0,0,{
                                         'date':datetime.now(timezone('Asia/Kolkata')),
                                         'employee_id':id[0],
                                         'designation':id[1],
                                         'manager_id':id[2]
                                         }))
            return list_return
        else: return False
        
    def _get_manager_employee_id(self,cr,uid,context=None):
        context = {}
        context.update({'read_access':True})
        emp_id = self.pool.get('res.users').read(cr,uid,uid,['emp_id'],context)
        if emp_id.get('emp_id',False):
            return emp_id.get('emp_id',False)[0]
        else:return False
        
    _defaults = {
                 'state':'pending',
                 'date':datetime.now(timezone('Asia/Kolkata')),
                 'manager_id':lambda self,cr,uid,context:uid,
                 'project_id':_get_project_id,
                 'emploee_status_line':_get_employee_status_line,
                 'manager_employee_id':_get_manager_employee_id,
                 }
    
    '''
    1. This is basically attendance record of a project.
    2. Will be created only one per project per day
    3. Will be shared between the circle head and project manager but will only editted superly by circle user 
    '''
    
    _columns = {
                'date':fields.date('Date',states={'submitted':[('readonly',True)]},required=True),
                'manager_id':fields.many2one('res.users','Created By',states={'submitted':[('readonly',True)]},required=True),
                'submitted_by':fields.many2one('res.users',"Submitted By"),
                'manager_employee_id':fields.many2one('hr.employee'), #this field is required to set domain on employee_id field in xml view
                'project_id':fields.many2one('telecom.project',"Project",states={'submitted':[('readonly',True)]},required=True),
                'attendance_id':fields.many2one('attendance.attendance',"Attendance Record",states={'submitted':[('readonly',True)]},required =True,ondelete="cascade",select=True),
                'state':fields.selection([
                                          ('pending','Pending'),
                                          ('submitted','Submitted')
                                          ],string = "State",states={'submitted':[('readonly',True)]}),
                'emploee_status_line':fields.one2many('employee.status.line','line_id','Employee Attendance',states={'submitted':[('readonly',True)]}),
                }

class employee_status_line(osv.osv):
    _name = "employee.status.line" 
    _description = "Employee Status Line"
    
    def create(self,cr,uid,vals,context=None):
        '''
        Make sure that the project from which attendance is taken,the employee status line is overwritten on employee current project
        '''
        # vals = {'line_id': 16, u'state': u'present', u'employee_id': 3, u'manager_id': 2, u'designation': 1}
        if context.get('project_write',False):
            project_id = self.pool.get('attendance.line').browse(cr,SUPERUSER_ID,vals.get('line_id'),context).project_id.id
            # write it in the current_project field of the employee
            self.pool.get('hr.employee').write(cr,SUPERUSER_ID,vals.get('employee_id',False),{'current_project':project_id},context)
        return super(employee_status_line,self).create(cr,uid,vals,context)
    
    _sql_constraints = [
        ('restrict_one_employee_perday', 'unique(employee_id,date)', 'An employee can only have single attendance/day!'),
    ]
    
    '''
        In this the employee today's attendance will be taken
        1. Only one employee status line per day.
        2. If attendance already taken and then the employee is transferred to another project then the existing attendace line
        will be deleted and a new employee.status.line will be created for that day
        3. This will be the lines that the corporate will see for the attendance report
    '''
    
    def onchange_employee_id(self,cr,uid,id,employee_id,project_id,context=None):
        info = self.pool.get('hr.employee').read(cr,uid,employee_id,['job_id','parent_id','current_project'],context)
        warning = {}
        if info and info.get('current_project',False) and info.get('current_project',False)[0]:
            if project_id != info.get('current_project',False)[0]:
                warning.update({
                                'title':"Employee Project",
                                'message':"This employee currently belongs to %s project. If you continue then the project of the employee will change" %(info.get('current_project',False)[1])
                                })
        return {
                    'value':{
                             'designation':info and info.get('job_id',False) and info.get('job_id',False)[0] or False,
                             'manager_id':info and info.get('parent_id',False) and info.get('parent_id',False)[0] or False,
                             },
                    'warning':warning,
                }
    
    _defaults = {
                 'date':datetime.now(timezone('Asia/Kolkata')),
                 }
    _rec_name = 'employee_id'
    
    _columns ={
               'employee_id':fields.many2one('hr.employee',"Employee Name",required=True),
               'manager_id':fields.many2one('hr.employee',"Reporting Manager"),
               'current_project':fields.many2one('telecom.project',"Current Project"),
               'date':fields.date('Date',required = True),
               'designation':fields.many2one("hr.job",string="Designation"),
               'state':fields.selection([
                                     ('present','Present'),
                                     ('absent','Absent'),
                                     ('leave','Leave'),
                                     ('terminated','Terminated'),
                                     ('tour',"On Tour"),
                                     ],string = "Status",required=True ),
               'remarks':fields.text('Remarks'),
               'line_id':fields.many2one('attendance.line',ondelete='cascade',select=True),
               }
    
    