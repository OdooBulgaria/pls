from openerp.osv import fields, osv

class telecom_project(osv.osv):
    _name="telecom.project"
    
    _columns={'name':fields.char(string='Project Name'),
              'project_manager':fields.many2many('res.users','project_manager_rel','project_id','manager_id',string='Project Manager / Project Coordinator',help="Project Coordinator"),
              'circle':fields.many2one("telecom.circle",string="Circle"),
              'customer':fields.many2one("res.partner",string="Customer"),
              "start_date":fields.date(string="Start Date"),
              "end_date":fields.date(string="End Date"),
              'image':fields.binary("Bianry field"),
              'project_activities':fields.one2many('work.description','description_id',string="Work Description"),
               'contact_no':fields.related('customer','phone',type="char",string="Contact No")
              }
class telecom_circle(osv.osv):
    _name='telecom.circle'
    _columns={'name':fields.char(string='Circle Name'),
              'project_name':fields.one2many('telecom.project','circle',string='Projects'),
              'circle_head':fields.many2one('res.users',string="Circle Head / Regional Manager"),
              }
    
class work_description(osv.osv):  # do not make all the objects in one file. You should have created a separate file for it
    _name="work.description"
    _columns={'name':fields.char(string='Work Description'),
              'activity_line':fields.one2many('workdescription.line',"activity_id",string='Activity'),
              'description_id':fields.many2one("telecom.project") #always make many2one field as some id ...in this case description_id
              }
    
class workdescription_line(osv.osv):
    _name='workdescription.line'
    _columns={'name':fields.char(string='Activity Name'),
              'cost':fields.float(string="Cost"),
              #'time_to_complete':fields.datetime()
              'activity_id':fields.many2one('work.description',string="Activities"),
              }
