from openerp.osv import fields, osv

class telecom_project(osv.osv):
    _name="telecom.project"
    
    
    #attendance will only be considered for the wip state
    _defaults = {
                 'state':'draft'
                 }

    def list_project(self, cr, uid, context=None):
        result = []
        list_ids = self.pool.get('attendance.attendance').fetch_ids_user(cr,uid,context)
        if list_ids:
            print "================employee",list_ids
            ng = dict(self.pool.get('telecom.project').name_search(cr,uid,'',[('id','in',list_ids[0][2])]))
        else:
            list_ids = self.pool.get("telecom.project").search(cr,uid,[], offset=0, limit=200, order=None, context=None, count=False)
            print "==========================",list_ids 
            ng = dict(self.pool.get('telecom.project').name_search(cr,uid,'',[('id','in',list_ids)]))            
        if ng:
            ids = ng.keys()
            for project in self.pool.get('telecom.project').browse(cr, uid, ids, context=context):
                result.append((project.id,ng[project.id]))
        print "=====================result==================",result
        return result

    
    _columns={
              'name':fields.char(string='Project Name',required =True),
              'project_manager':fields.many2many('hr.employee','telecom_project_hr_employee_rel','project_id','manager_id',string='Project Manager / Project Coordinator',help="Project Coordinator"),
              'circle':fields.many2one("telecom.circle",string="Circle"),
              'customer':fields.many2one("res.partner",string="Customer"),
              'start_date':fields.date(string="Start Date"),
              'end_date':fields.date(string="End Date"),
              'image':fields.binary("Bianry field"),
              'contact_no':fields.related('customer','phone',type="char",string="Contact No"),
              'line_id':fields.one2many('project.description.line','project_id',string="Work Description"),
              'state':fields.selection([
                                    ('draft','Draft'),('wip','WIP'),('close','Close')
                                    ],help = "Attendance will only be considered for the WIP state"),
              }
class project_description_line(osv.osv):
    _name="project.description.line"  
    
    def setof_associated_activities(self,cr,uid,ids,description_id,context=None):
        description=self.pool.get('work.description').browse(cr, uid, description_id,context)
        values=[]
        for i in description.activity_ids:
            values.append((0,0,{'activity_id':i.id}))
        return {
                'value':{'activity_ids':values}
                 
               }
    _columns={
              'description_id':fields.many2one('work.description',string="Work Description"),
              'activity_ids':fields.one2many('activity.line','activity_line',string="Activities"),
              'project_id':fields.many2one('telecom.project')
              }
class activity_line(osv.osv):
    _name='activity.line'
    _rec_name='activity_id'
    _columns={
              'activity_line':fields.many2one('project.description.line'),
              'activity_id':fields.many2one('activity.activity',string = "Activity Name"),
              'cost':fields.float(string='Customer Cost'),
              'vendor_cost':fields.float(string="Vendor Cost"),
              'project_id':fields.related('activity_line','project_id',relation = "telecom.project",type="many2one",store=True,string="Project",readonly=True),
              'vendor_id':fields.many2one('res.partner',string = "Vendor",domain = [('supplier','=',True)]),
              }
      
class telecom_circle(osv.osv):
    _name='telecom.circle'
    _columns={'name':fields.char(string='Circle Name',required=True),
              'project_name':fields.one2many('telecom.project','circle',string='Projects'),
              'circle_head':fields.many2one('res.users',string="Circle Head / Regional Manager"),
              }
    
class work_description(osv.osv):  
    _name="work.description"
      
    _columns={'name':fields.char(string='Work Description',required = True),
              'activity_ids':fields.many2many('activity.activity',"work_description_activity_activity_rel",'description_id','activity_id',string='Activities'),
              }
    
class activity_activity(osv.osv):
    _name = "activity.activity"
    _columns = {
                'name':fields.char('Activity Name',required = True),
                }