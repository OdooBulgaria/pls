from openerp.osv import fields, osv

class telecom_project(osv.osv):
    _name="telecom.project"
    #attendance will only be considered for the wip state
    _defaults = {
                 'state':'draft'
                 }
    
    def _get_user_ids_group(self,cr,uid,module,group_xml_id):
        '''
        This method takes in the module and xml_id of the group and return the list of users present in that group
        '''
        groups = self.pool.get('ir.model.data').get_object_reference(cr, uid, module, group_xml_id)[1]
        user_group=self.pool.get('res.groups').browse(cr,uid,groups)
        user_ids=map(int,user_group.users or [])
        return user_ids                    
        
    def list_project(self, cr, uid, context=None):
        result = []
        list_ids = self.pool.get('attendance.attendance').fetch_ids_user(cr,uid,context)
        if list_ids:
            ng = dict(self.pool.get('telecom.project').name_search(cr,uid,'',[('id','in',list_ids[0][2])]))
        else:
            list_ids = self.pool.get("telecom.project").search(cr,uid,[], offset=0, limit=None, order=None, context=None, count=False)
            ng = dict(self.pool.get('telecom.project').name_search(cr,uid,'',[('id','in',list_ids)]))            
        if ng:
            ids = ng.keys()
            for project in self.pool.get('telecom.project').browse(cr, uid, ids, context=context):
                result.append((project.id,ng[project.id]))
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
              'site_id':fields.many2many('project.site','telecom_project_project_site_rel','project_id','site_id',string="Project Sites"),
              'activity_tracker_ids':fields.one2many('activity.line.line','project_id',string="Activity Trackers")
              }
class project_description_line(osv.osv):
    _name="project.description.line"  
    _rec_name = "description_id"
    
    def setof_associated_activities(self,cr,uid,ids,description_id,site_id,context=None):
        description=self.pool.get('work.description').browse(cr, uid, description_id,context)
        values=[]
        print "parent.site_id---------------------------------",site_id
        if len(site_id[0][2])!=0 :
            for i in description.activity_ids:
                for j in site_id[0][2]:
                    values.append((0,0,{'activity_id':i.id,
                                    'site_id':j
                                    }))
        else:
            for i in description.activity_ids:
                values.append((0,0,{'activity_id':i.id,
                                    'site_id':False}))
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
              'activity_id':fields.many2one('activity.activity',string = "Activity Name",required=True),
              'cost':fields.float(string='Customer Cost'),
              'project_id':fields.related('activity_line','project_id',relation = "telecom.project",type="many2one",store=True,string="Project",readonly=True),
              'site_id':fields.many2one('project.site',string = "Site ID"),
              'activity_line_line':fields.one2many('activity.line.line','line_id',string='Activity-Line Items'),
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
class activity_line_line(osv.osv):
    _name='activity.line.line'
    _inherits = {'project.tracker': 'tracker_line_id'}
    
    def create(self,cr,uid,vals,context=None):
        line_item_id=vals.get('line_id',False)
        activity_line_obj=self.pool.get('activity.line').browse(cr,uid,line_item_id,context)
        tracker_id=self.pool.get('project.tracker').create(cr,uid,{
              'work_description_id':activity_line_obj.activity_line.description_id.id,
              'IPR_no':False,
              'IPR_date':False,
              'site_id': vals.get('site_id',False),
              'site_name':vasl.get('site_id',False) and self.pool.get('project.site').browse(cr,uid,vals.get('site_id'),context) or False,
              'po_status':False,
              'activity_planned':vals.get('line_id'),
              'per_unit_Price':0.0,
              'subvendor_rate':0.0,
              'advance_paid_to_vendor':0.0,
              'balance_payment3':0.0,
              'done_by':False,
              'activity_start_date':False,
              'activity_end_date':False,
              'wcc_sign_off_status':False,
              'wcc_sign_off_date':False,
              'quality_document_uploaded_on_P6':False,
              'quality_document_uploaded_date':False,
              'cql_approval_status':False,
              'pd_approval_status':False,
              })
        print "---------------------------tracker_id ~~~~",tracker_id
        vals.update({'tracker_line_id':tracker_id})
        print "---------------------------vals",vals
        return super(activity_line_line,self).create(cr,uid,vals,context)
        
    _columns={
              'line_id':fields.many2one('activity.line',string='Activity Line'),
              'site_id':fields.related('line_id','site_id',relation = "project.site",type="many2one",string="Site ID"),
              'vendor_id':fields.many2one('res.partner',string="Vendor",domain=[('supplier','=',True)]),
              'type':fields.selection(selection=[('inhouse','Inhouse'),('vendor','Vendor')],required=True,string="Activity Type"),
              'cost':fields.float(string='Vendor Cost'),
              'tracker_line_id':fields.many2one('project.tracker',string='Tracker Line',ondelete="cascade"),
              'project_id':fields.related('line_id','activity_line','project_id',relation='telecom.project',type="many2one",string="Project",store=True)
              }

class project_site(osv.osv):
    _name = 'project.site'
    
    _columns={
              'name':fields.char(string="Site Name"),
              'site_id':fields.char(string="Site ID"),
              'address':fields.text(string='Site Address'),
              'project_id':fields.many2many('telecom.project','telecom_project_project_site_rel','site_id','project_id',string="Projects")
              }