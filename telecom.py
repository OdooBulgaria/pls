from openerp.osv import fields, osv

class telecom_project(osv.osv):
    _name="telecom.project"
    
    _columns={'name':fields.char(string='Project Name'),
              'project_manager':fields.many2many('res.users','project_manager_rel','project_id','manager_id',string='Project Manager / Project Coordinator',help="Project Coordinator"),
              'circle':fields.many2one("telecom.circle",string="Circle"),
              'customer':fields.many2one("res.partner",string="Customer"),
              'start_date':fields.date(string="Start Date"),
              'end_date':fields.date(string="End Date"),
              'image':fields.binary("Bianry field"),
              'contact_no':fields.related('customer','phone',type="char",string="Contact No")
              }
    
class telecom_circle(osv.osv):
    _name='telecom.circle'
    _columns={'name':fields.char(string='Circle Name'),
              'project_name':fields.one2many('telecom.project','circle',string='Projects'),
              'circle_head':fields.many2one('res.users',string="Circle Head / Regional Manager"),
              }
    
class work_description(osv.osv):  
    _name="work.description"
    _columns={'name':fields.char(string='Work Description'),
              'activity_ids':fields.many2many('activity.activity',"work_description_activity_activity_rel",'description_id','activity_id',string='Activities'),
              }
    
class activity_activity(osv.osv):
    _name = "activity.activity"
    _columns = {
                'name':fields.char('Activity Name'),
                }