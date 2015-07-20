from openerp.osv import fields, osv
from openerp import tools

ACCESS_TYPE_SELECTION = [
                          ('employee','Employee'),
                          ('manager',"Manager"),
                          ('circle',"Circle Head"),
                          ('corporate','Corporate'),
                        ]     
    
class telecom_employee(osv.osv):
    _name='telecom.employee'
    
    _defaults = {
                 'state':'employee',
                 }
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
    
    def onchange_company_name(self,cr,uid,ids,emp_type,context=None):
        return {
                'value':{'company_name':False}
                }
     

    _columns = {
        #we need a related field in order to be able to sort the employee by name
        'name':fields.char(string ="Employee Name"),
        'user_id':fields.many2one('res.users',string="Related User"),
        'joining_date':fields.date(string='Date Of Joining'),
        'emp_type':fields.selection([('inhouse','Inhouse'),('vendor','Vendor')],string="Employee Type"),
        'company_name':fields.many2one('res.partner',string='Vendor Company'),
        'current_project':fields.many2one('telecom.project',string='Current Project'),
        'country_id': fields.many2one('res.country', 'Nationality'),
        'birthday': fields.date("Date of Birth"),
        'ssnid': fields.char('SSN No', help='Social Security Number'),
        'sinid': fields.char('SIN No', help="Social Insurance Number"),
        'identification_id': fields.char('Identification No'),
        'otherid': fields.char('Other Id'),
        'gender': fields.selection([('male', 'Male'), ('female', 'Female')], 'Gender'),
        'marital': fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'bank_account_id': fields.many2one('res.partner.bank', 'Bank Account Number', domain="[('partner_id','=',address_home_id)]", help="Employee bank salary account"),
        'work_phone': fields.char('Work Phone', readonly=False),
        'mobile_phone': fields.char('Work Mobile', readonly=False),
        'work_email': fields.char('Work Email', size=240),
        'base_location': fields.char('Base Location'), #rename to Base Location
        'notes': fields.text('Notes'),
        'parent_id': fields.many2one('telecom.employee', 'Reporting To'),
        'child_ids': fields.one2many('telecom.employee', 'parent_id', 'Subordinates'),
        'job_id': fields.many2one('hr.job', 'Job Title'),
        'access_group':fields.related('job_id','access_type',type='selection', selection=ACCESS_TYPE_SELECTION,string="Access Group"),
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Photo",
            help="This field holds the image used as photo for the employee, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized photo", type="binary", multi="_get_image",
            store = {
                'telecom.employee': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized photo of the employee. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized photo", type="binary", multi="_get_image",
            store = {
                'telecom.employee': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized photo of the employee. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'passport_id': fields.char('Passport No'),
        'color': fields.integer('Color Index'),
        'city': fields.char( string='City'),
        'login': fields.related('user_id', 'login', type='char', string='Login', readonly=1),
        'last_login': fields.related('user_id', 'date', type='datetime', string='Latest Connection', readonly=1),
    }
    
    
class hr_job(osv.Model):


    def _get_nbr_employees(self, cr, uid, ids, name, args, context=None):
        res = {}
        for job in self.browse(cr, uid, ids, context=context):
            nb_employees = len(job.employee_ids or [])
            res[job.id] = {
                'no_of_employee': nb_employees,
                'expected_employees': nb_employees + job.no_of_recruitment,
            }
        return res

    def _get_job_position(self, cr, uid, ids, context=None):
        res = []
        for employee in self.pool.get('telecom.employee').browse(cr, uid, ids, context=context):
            if employee.job_id:
                res.append(employee.job_id.id)
        return res

    _name = "hr.job"
    _description = "Job Position"
    _columns = {
        'name': fields.char('Job Name', required=True, select=True),
        'access_type':fields.selection(ACCESS_TYPE_SELECTION,string = "Access"),
        'expected_employees': fields.function(_get_nbr_employees, string='Total Forecasted Employees',
            help='Expected number of employees for this job position after new recruitment.',
            store = {
                'hr.job': (lambda self,cr,uid,ids,c=None: ids, ['no_of_recruitment'], 10),
                'telecom.employee': (_get_job_position, ['job_id'], 10),
            }, type='integer',
            multi='_get_nbr_employees'),
        'no_of_employee': fields.function(_get_nbr_employees, string="Current Number of Employees",
            help='Number of employees currently occupying this job position.',
            store = {
                'telecom.employee': (_get_job_position, ['job_id'], 10),
            }, type='integer',
            multi='_get_nbr_employees'),
        'no_of_recruitment': fields.integer('Expected New Employees', copy=False,
                                            help='Number of new employees you expect to recruit.'),
        'no_of_hired_employee': fields.integer('Hired Employees', copy=False,
                                               help='Number of hired employees for this job position during recruitment phase.'),
        'employee_ids': fields.one2many('telecom.employee', 'job_id', 'Employees', groups='base.group_user'),
        'description': fields.text('Job Description'),
        'requirements': fields.text('Requirements'),
        'department_id': fields.many2one('hr.department', 'Department'),
        'company_id': fields.many2one('res.company', 'Company'),
        'state': fields.selection([('open', 'Recruitment Closed'), ('recruit', 'Recruitment in Progress')],
                                  string='Status', readonly=True, required=True,
                                  track_visibility='always', copy=False,
                                  help="By default 'Closed', set it to 'In Recruitment' if recruitment process is going on for this job position."),
        'write_date': fields.datetime('Update Date', readonly=True),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, ctx=None: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.job', context=ctx),
        'state': 'open',
    }

    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id, department_id)', 'The name of the job position must be unique per department in company!'),
        ('hired_employee_check', "CHECK ( no_of_hired_employee <= no_of_recruitment )", "Number of hired employee must be less than expected number of employee in recruitment."),
    ]

    def set_recruit(self, cr, uid, ids, context=None):
        for job in self.browse(cr, uid, ids, context=context):
            no_of_recruitment = job.no_of_recruitment == 0 and 1 or job.no_of_recruitment
            self.write(cr, uid, [job.id], {'state': 'recruit', 'no_of_recruitment': no_of_recruitment}, context=context)
        return True

    def set_open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'open',
            'no_of_recruitment': 0,
            'no_of_hired_employee': 0
        }, context=context)
        return True

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        if 'name' not in default:
            job = self.browse(cr, uid, id, context=context)
            default['name'] = _("%s (copy)") % (job.name)
        return super(hr_job, self).copy(cr, uid, id, default=default, context=context)
    
    
    
    
class hr_department(osv.osv):

    def _dept_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    _name = "hr.department"
    _columns = {
        'name': fields.char('Department Name', required=True),
        'complete_name': fields.function(_dept_name_get_fnc, type="char", string='Name'),
        'company_id': fields.many2one('res.company', 'Company', select=True, required=False),
        'parent_id': fields.many2one('hr.department', 'Parent Department', select=True),
        'child_ids': fields.one2many('hr.department', 'parent_id', 'Child Departments'),
        'manager_id': fields.many2one('telecom.employee', 'Manager'),
        'member_ids': fields.one2many('telecom.employee', 'department_id', 'Members', readonly=True),
        'jobs_ids': fields.one2many('hr.job', 'department_id', 'Jobs'),
        'note': fields.text('Note'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'hr.department', context=c),
    }

    def _check_recursion(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        level = 100
        while len(ids):
            cr.execute('select distinct parent_id from hr_department where id IN %s',(tuple(ids),))
            ids = filter(None, map(lambda x:x[0], cr.fetchall()))
            if not level:
                return False
            level -= 1
        return True

    _constraints = [
        (_check_recursion, 'Error! You cannot create recursive departments.', ['parent_id'])
    ]

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

