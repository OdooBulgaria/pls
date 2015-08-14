openerp.pls.quickadd = function(instance) {
    var _t = instance.web._t,
        _lt = instance.web._lt;
    var QWeb = instance.web.qweb;
    
    instance.web.pls = instance.web.pls || {}
    
    instance.web.complaint_system.filter_view_message.include({
    	start:function(){
    		var self = this;
    		var defs = [];
			var tmp = this._super.apply(self, arguments); 
    		if ('render_javascript' in self.dataset.context){
    			if ('subtype' in self.dataset.context){
    				if (self.dataset.context['subtype'] == 'attendance_override'){
                		var view_id = new openerp.Model('ir.model.data');
                        defs.push(view_id.call("get_object_reference", ['pls','mt_comment_attendance_override']).then(function(result) {
                        		self.subtype = result[1]
                        }));                        	                    		    					
    				}
    			}
    		}
    		return $.when(tmp,defs);
		},
    });
    
    // Attendance Dashboard
    instance.web.views.add('tree_attendance_dashboard', 'instance.web.pls.filter_view_attendance');
    instance.web.pls.filter_view_attendance = instance.web.ListView.extend({
    	init:function(){
            this._super.apply(this, arguments);
            var self = this;
            self.date = null;
            self.current_project= null
            self.project = null;
		},
    	start:function(){
    		var self = this;
    		var defs = []
            self.date = (new Date()).format("Y-m-d");
    		self.d = $.Deferred();
            return this._super.apply(this, arguments).then(function(){
            	self.$el.parent().prepend(QWeb.render("attendance_dashboard", {widget: this}));
                self.$el.parent().find('.oe_select').change(function() {
                		self.current_project = this.value === '' ? null : parseInt(this.value);
    	                self.do_search(self.last_domain, self.last_context, self.last_group_by);
    	            });            	
            	
                self.$el.parent().find("input#from").change(function(){
                	if (this.value !== "") 
                		self.date = this.value;
            		else self.date = null
                	self.do_search(self.last_domain, self.last_context, self.last_group_by);
                });               
                
            	var mod = new instance.web.Model("telecom.project", self.dataset.context, self.dataset.domain);
                defs.push(mod.call("list_project", []).then(function(result) {
                	self.project = result
                	self.d.resolve();
                }));
                return $.when(defs)
            });  		
    	},
    	
    	do_search:function(domain, context, group_by){
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            self.project_list_sorted = []
            var o;
            self.$el.parent().find('.oe_select').children().remove().end();
            self.$el.parent().find('.oe_select').append(new Option('', ''));
            $.when(self.d).then(function(){
                if (self.project){
                    for (var i = 0;i < self.project.length;i++){
                    	self.project_list_sorted.push(self.project[i][0]);
                    	o = new Option(self.project[i][1], self.project[i][0]);
                        self.$el.parent().find('.oe_select').append(o);
                    }            	
                    self.$el.parent().find('.oe_select')[0].value = self.current_project;
                }                        	
            });
            return self.search_by_project_id();    		
    	},
    	
    	search_by_project_id: function() {
            var self = this;
            var domain = [];
            
            /*
             * Check if the user is a Project Manager,Circle Head of Corporate
             *  - If Project Manager then show all attendances for the project in which the project manager is 
             *  - Corporate Head is able to see attendance of all his projects and the project managers under him 
             *  - Corporate is able to see all
             */
            
            if (self.current_project!== null) domain.push(["line_id.project_id", "=", self.current_project]);
            else{
            	domain.push(["line_id.project_id", "in", self.project_list_sorted]);
            }
            if (self.date ) {
            	domain.push(['date','=',self.date])
            }
            self.last_context["project_id"] = self.current_project === null ? false : self.current_project;
            var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);            	
        },            	
    });

    // Activity Dashboard
    instance.web.views.add('tree_activity_dashboard', 'instance.web.pls.filter_view_activities');
    instance.web.pls.filter_view_activities = instance.web.ListView.extend({
    	init:function(){
            this._super.apply(this, arguments);
            var self = this;
            self.date_from = null;
            self.date_to = null;
            self.project_id = null;
            self.circle_id = null;
            self.employee_id = null;
            self.state = "wip";
            self.defs = [];
            self.info = null;
            self.d = $.Deferred();
            self.project_list = [];
            self.circle_list = [];
            self.employee_list = [];
            self.state = null;
            self.render_element = $("");
    	},
    	start:function(){
    		var self = this;
            today_date = (new Date()).format("Y-m-d");
            return this._super.apply(this, arguments).then(function(){
            	var mod = new instance.web.Model("employee.activity.line", self.dataset.context, self.dataset.domain);
                self.defs.push(mod.call("list_caption", []).then(function(result) {
                	self.info = result
                	self.d.resolve();
                }));
            });  		
    	},
    	
    	do_search:function(domain, context, group_by){
            var self = this;
            this.last_domain = domain;
            this.last_context = context;
            this.last_group_by = group_by;
            this.old_search = _.bind(this._super, this);
            var o;
            return $.when(self.d).done(function(){
            	self.$el.parent().find("div.oe_account_quickadd.ui-toolbar").remove();
            	self.render_element = 	$(QWeb.render("activity_dashboard", {info: self.info}))
            	$.when(self.$el.parent().prepend(self.render_element)).then(function(){
            			//onchange project,circle,employee
            			self.$el.parent().find('select.clear_group,select.oe_select_selection').change(function() {
                        		self[$(this)[0].id] = this.value === '' ? null : parseInt(this.value) || this.value
                				return self.search_employee_activity_lines();
            	            });
            			//onchange from and to dates
	                      self.$el.parent().find("input.oe_datepicker_pls").change(function(){
	                    	if (this.value !== "") 
	                    		self[$(this)[0].id] = this.value;
	                		else self[$(this)[0].id] = null;
	                    	return self.search_employee_activity_lines();
	                      });
            			//onchange selection fields
	                      
            				self.$el.parent().find('.clear_group').children().remove().end();
	    	                self.$el.parent().find('.clear_group').append(new Option('', ''));
	    	            	// rendering projects
	    	                if (self.info.project){
	    	                    for (var i = 0;i < self.info.project.length;i++){
	    	                    	self.project_list.push(self.info.project[i][0])
	    	                    	o = new Option(self.info.project[i][1], self.info.project[i][0]);
	    	                        self.$el.parent().find('.oe_select_project').append(o);
	    	                    }            	
	    	                    self.$el.parent().find('.oe_select_project')[0].value = self.project_id;
	    	                }
	    	                //render circles
	    	                if (self.info.circle){
	    	                    for (var i = 0;i < self.info.circle.length;i++){
	    	                    	self.circle_list.push(self.info.circle[i][0])
	    	                    	console.log(self.circle_list)
	    	                    	o = new Option(self.info.circle[i][1], self.info.circle[i][0]);
	    	                        self.$el.parent().find('.oe_select_circle').append(o);
	    	                    }            	
	    	                    self.$el.parent().find('.oe_select_circle')[0].value = self.circle_id;
	    	                }	    	     
	    	                //rendering employees
	    	                if (self.info.employee){
	    	                    for (var i = 0;i < self.info.employee.length;i++){
	    	                    	self.employee_list.push(self.info.employee[i][0])
	    	                    	o = new Option(self.info.employee[i][1], self.info.employee[i][0]);
	    	                        self.$el.parent().find('.oe_select_employee_name').append(o);
	    	                    }            	
	    	                    self.$el.parent().find('.oe_select_employee_name')[0].value = self.employee_id;
	    	                }	    	                	    	                
	    	            });            			
            		});
    		},

    		search_employee_activity_lines: function() {
            var self = this;
            var domain = [];
            if (self.info.project){
                if (self.project_id !== null) domain.push(["project_id", "=", self.project_id]);
                else{
                	domain.push(["project_id", "in", self.project_list]);
            	}            	
            }
            if (self.info.circle){
                if (self.circle_id !== null) domain.push(["project_id.circle", "=", self.circle_id]);
                else{
                	domain.push(["project_id.circle", "in", self.circle_list]);
            	}                        	
            }
            if (self.info.employee){
                if (self.employee_id !== null) domain.push(["employee_id", "=", self.employee_id]);
                else{
                	domain.push(["employee_id", "in", self.employee_list]);
            	}                        	
            }
            if (self.state !== null ) domain.push(['state','=',self.state]);
            else{
            	domain.push(['state','in',['completed','uncompleted','wip','unattempted']])
            }
            domain.push(['date','>=',self.date_from || today_date ]);
        	domain.push(['date','<=',self.date_to || today_date ]);
        	var compound_domain = new instance.web.CompoundDomain(self.last_domain, domain);
            self.dataset.domain = compound_domain.eval();
            return self.old_search(compound_domain, self.last_context, self.last_group_by);            	
        },            	
    });
    
    
}