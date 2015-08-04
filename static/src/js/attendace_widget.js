openerp.pls = function(instance, local) {
	openerp.pls.quickadd(instance);
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    /*
     * 
     * There will be a main widget that will call two widgets
     * -The many2one field widget
     * -The project for which attendance is taken rendering widget
     *  Both these widgets will be called into the main widget
     *  Display the project for which attendance is taken in a table form with two columns ---> project,attendance taken by 
     *  also display another table for projects for which attendance is not taken\
     *  
     */
    
    // This is the select project widget containing many2one field and the button
    
    local.select_project = instance.Widget.extend({
    	template:"select_project",
        events : {
			"click #select_project":"pop_up_wizard",
        },
    	init:function(parent){
    		this._super(parent);
    	},
    	
    	pop_up_wizard:function(){
    		var self = this
    		var Users = new openerp.Model('res.users')
    		Users.query(['override_time', 'allowed_attendance_time'])
    	     .filter([['id', '=', self.session.uid]])
    	     .limit(1)
    	     .all().then(function (result) {
    	    	 	console.log(result[0].allowed_attendance_time);
    	    	 	var d = new Date();
    	    	 	var n = d.getHours();
    	    	 	var  m = d.getMinutes();
    	    	 	time = n + parseFloat(m/60)
    	    	 	/*
    	    	 	 * Check if the user is allowed to override or the time limit is still left
    	    	 	 */
    	    	 	if (time >= result[0].allowed_attendance_time ){
    	    	 		if (! result[0].override_time){
    	    	 			alert('Sorry time for submitting attendance is over for the day.\n'+"Please request the administrator to extend the time limit")
    	    	 			return 
    	    	 		}
    	    	 	}
    	    	 	project_selected = self.project_m2o.get_value()
    	    	 	if (project_selected){
    	    			var action = {}; 
    	    			var check_line_exist = new openerp.Model('attendance.line').call('check_line_exist',[project_selected],{}).done(function(result){
    	    				if (result){
    	    					action['res_id'] = result[0][0]
    	    					if (!result[1]){
    	    						self.do_notify('Warning','The attendace for this project has already been taken by other manager')
    	    					}
    	    				}
    	    				var view_id = new openerp.Model('ir.model.data').call('get_object_reference',['pls','view_attendace_line_take_attendance']).done(function(result){
    	    					action = _.extend(action,{
    		           	             'type': 'ir.actions.act_window',
    		           	             'view_type': 'form',
    		           	             'view_mode': 'form',
    		           	             'res_model': 'attendance.line',
    		           	             'views': [[result[1], 'form']],
    		           	             'view_id': result[1],
    		           	             'target': 'new',
    		           	             'context':{'project_id':project_selected,'read_access':true,'project_write':true}
    		               			/*
    		               			 * project_selected -: used by button to open the selected project in many2one field while taking attendance
    		               			 * read_access -: this is used to override the employee visibility ir.rule for project managers only while taking attendance
    		               			 * project-write -: used by employee.status.line create() to overwrite the employee current project while taking attendance
    		               			 */
    		               			})
    	    					self.do_action(action);
    	            		});
    	    			});
    	    		}
    	    		else {
    	    			self.do_notify('Invalid Input','Please enter the project')
    	    		}    	     
    	     });
		},
    	
    	start:function(){
    		var self = this;
    		def = self.render_view();
    		return def
    	},

    	render_view:function(){
    		var self=this;
    		return self.createFormWidget();
    	},
    	
    	//query to find the ids for the domain defined in attendance_attendance.py
    	fetch_ids_user:function(){
    		var attendance = new openerp.Model('attendance.attendance');
    		return attendance.call('fetch_ids_user', [],{})
    	},
    	
    	//creates and renders the many2one field and the button
    	createFormWidget: function() { //working
    		var self = this;
    		if (self.dfm)
    			return;
            self.dfm = new instance.web.form.DefaultFieldManager(self);
            self.dfm.extend_field_desc({
                project_id: {
                	string:'Project',
                    relation: "telecom.project",
                },
            });
            var uid = self.session.uid
            domain_ids = self.fetch_ids_user(uid);
            $.when(domain_ids).then(function(domain_ids){
                self.project_m2o = new instance.web.form.FieldMany2One(self.dfm, {
                	attrs: {
                        name: "project_id",
                        type: "many2one",
                        domain: domain_ids,
                        context: {
                        'form_view_ref':'pls.telecom_project_form_view_many2o'
                        },
                        modifiers: '{"required": true}',
                    },
                });
                var $button = $(QWeb.render("button_select_project", {}));
                self.project_m2o.prependTo(self.$el);
                self.$el.first().find('span.oe_form_field').prepend($button);
            });
    	},    	
    });
    
    
    local.attendance_base = instance.Widget.extend({
    	template:"attendance_base",
    	init:function(parent){
    		this._super(parent)
    	},
    	
    	start: function() {
    		var self =this;
        	// Initializing the select project widget
        	var select_project_widget  = new local.select_project(this);
        	select_project_widget.appendTo(self.$el)
        },
        
    });

    instance.web.client_actions.add(
        'local.attendance_base', 'instance.pls.attendance_base');
}