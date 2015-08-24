from openerp.osv import fields, osv

class project_site(osv.osv):
    _name = 'project.site'
    
    _columns={
              'name':fields.char(string="Site Name"),
              'site_id':fields.char(string="Site ID"),
              'address':fields.text(string='Site Address'),
#               'project_id':fields.many2many('telecom.project','telecom_project_project_site_rel','site_id','project_id',string="Projects")
              }


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
              'circle':fields.many2one("telecom.circle",string="Circle",required="1"),
              'customer':fields.many2one("res.partner",string="Customer"),
              'start_date':fields.date(string="Start Date"),
              'end_date':fields.date(string="End Date"),
              'image':fields.binary("Bianry field"),
              'contact_no':fields.related('customer','phone',type="char",string="Contact No"),
              'line_id':fields.one2many('project.description.line','project_id',string="Work Description"),
              'state':fields.selection([
                                    ('draft','Draft'),('wip','WIP'),('close','Close')
                                    ],help = "Attendance will only be considered for the WIP state"),
              'activity_tracker_ids':fields.one2many('activity.line.line','project_id',string="Activity Trackers")
              }
class project_description_line(osv.osv):
    _name="project.description.line"  
    _rec_name = "description_id"
    
    def onchange_setof_associated_activities(self,cr,uid,ids,description_id,context=None):
        if ids:
            description=self.pool.get('work.description').browse(cr, uid, description_id,context=None)
            values=[]
            customer_id=self.browse(cr,uid,ids[0],context=None).project_id.customer.id
            
            if description_id:
                for i in description.activity_ids:
                    activity=self.pool.get('customer.contract').search(cr,uid,[('activity_id','=',i.id)],context=None)
                    activity_cost=self.pool.get('customer.contract').read(cr,uid,activity,['cost'],context=None)[0].get('cost',0.0)
                    values.append((0,0,{'activity_id':i.id,
                                        'cost':activity_cost,
                                        }))
            return {
                    'value':{'activity_ids':values}
                   }
        return {}
        
        
    
    _columns={
              'description_id':fields.many2one('work.description',string="Work Description"),
              'activity_ids':fields.one2many('activity.line','activity_line',string="Activities"),
              'project_id':fields.many2one('telecom.project')
              }
    
class activity_line(osv.osv):
    _name='activity.line'
    _rec_name='activity_id'
    
    def onchange_for_activity_cost(self,cr,uid,id,activity_id,context):
        values={}
        activity=self.pool.get('customer.contract').search(cr,uid,[('activity_id','=',activity_id)],context=None)
        activity_cost=self.pool.get('customer.contract').read(cr,uid,activity,['cost'],context=None)[0].get('cost',0.0)

        return {
                'value':{'cost':activity_cost}
               }
        
    _columns={
              'activity_line':fields.many2one('project.description.line'),
              'activity_id':fields.many2one('activity.activity',string = "Activity Name",required=True),
              'cost':fields.float(string='Customer Cost'),
              'project_id':fields.related('activity_line','project_id',relation = "telecom.project",type="many2one",store=True,string="Project",readonly=True),
#               'site_id':fields.many2one('project.site',string = "Site"),
              'activity_line_line':fields.one2many('activity.line.line','line_id',string='Activity-Line Items'),
              }
      
class telecom_circle(osv.osv):
    _name='telecom.circle'
    _columns={'name':fields.char(string='Circle Name',required=True),
              'project_name':fields.one2many('telecom.project','circle',string='Projects'),
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
    
    def _get_balance_payment(self,cr,uid,ids,name,args,context=None):
        res = {}
        records = self.read(cr,uid,ids,['advance_paid_to_vendor','cost'],context)
        for info in records:
            balance_payment = info.get('cost',0) - info.get('advance_paid_to_vendor',0)
            res.update({
                        info.get('id',False):round(balance_payment,3)
                        })
        return res
    
    def _get_total_activities_cost(self,cr,uid,ids,name,args,context=None):
        res = {}
        
    _columns={
              'line_id':fields.many2one('activity.line',string='Activity Line'),
              'work_description':fields.related('line_id','activity_line','description_id',type="many2one",relation="work.description",string = "Work Description"),
              'site_id':fields.many2one("project.site",string="Site Name"),
              'site_code':fields.related('site_id','site_id',type="char",string="Site Code",readonly='1'),
              'vendor_id':fields.many2one('res.partner',string="Sub vendor",domain=[('supplier','=',True)]),
              'type':fields.selection(selection=[
                                                 ('inhouse','Inhouse'),('vendor','Vendor')
                                             ],required=True,string="Activity Type"),
              'cost':fields.float(string='Sub Vendor Rate'),
              
              'project_id':fields.related('line_id','activity_line','project_id',relation='telecom.project',type="many2one",string="Project",store=True),
              'balance_payment':fields.function(_get_balance_payment,string="Balance Payment"),
              'advance_paid_to_vendor':fields.float(string='Advance paid to vendor'),
              }
