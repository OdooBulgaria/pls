from openerp.osv import fields, osv
from datetime import datetime

class project_tracker(osv.osv):
    _name = 'project.tracker'
    
    _columns={
              'work_description_id_tracker':fields.many2one('work.description',string='Work description'),
              'IPR_no':fields.integer('IPR No'),
              'IPR_date':fields.datetime(string='IPR Date'),
              'site_id_tracker':fields.char(string='Site ID'),
              'site_name_tracker':fields.char(string='Site Name'),
              'po_status':fields.selection(string='PO Status',selection=[('Available','Available'),
                                                                    ('Not Available','Not Available'),
                                                                    ]),
              'activity_planned':fields.many2one('activity.line',string='Activity Planned'),
              'per_unit_Price':fields.float(string='Per unit Price'),
              'subvendor_rate':fields.float(string='Subvendor Rate'),
              'advance_paid_to_vendor':fields.float(string='Advance paid to vendor'),
              'balance_payment3':fields.float(string="Balance Payment3"),
              'done_by':fields.many2one('hr.employee',string='Done By'),
              'activity_start_date':fields.datetime(string='Activity Start Date'),
              'activity_end_date':fields.datetime(string='Activity End Date'),
              'wcc_sign_off_status':fields.selection(string='WCC sign off status',selection=[('Yes','Yes'),('No','No')]),
              'wcc_sign_off_date':fields.datetime(string='WCC Sign off Date'),
              'quality_document_uploaded_on_P6':fields.selection(string='Quality Document uploaded on P6',selection=[('Yes','Yes'),('No','No')]),
              'quality_document_uploaded_date':fields.datetime(sting='Activity End Date'),
              'cql_approval_status':fields.selection(string='IM Approval Status',selection=[('Yes','Yes'),('No','No')]),
              'pd_approval_status':fields.selection(string='PD Approval Status',selection=[('Yes','Yes'),('No','No')]),
              }
