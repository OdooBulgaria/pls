    	createFormWidget: function() { //working
    		var self = this;
		    var create_form_fields = self.create_form_fields;
		    var create_form_fields_arr = [];
		    for (var key in create_form_fields)
		        if (create_form_fields.hasOwnProperty(key))
		            create_form_fields_arr.push(create_form_fields[key]);
		    create_form_fields_arr.sort(function(a, b){ return b.index - a.index });
		    console.log(create_form_fields_arr);
		    // field_manager
		    var dataset = new instance.web.DataSet(this, "telecom.project", self.context);
		    dataset.ids = [];
		    dataset.arch = {
		        attrs: { string: "Attendace", version: "7.0", class: "oe_form_container" },
		        children: [],
		        tag: "form"
		    };
		    var field_manager = new instance.web.FormView (
		        this, dataset, false, {
		            initial_mode: 'edit',
		            disable_autofocus: false,
		            $buttons: $(),
		            $pager: $()
		    });
		    field_manager.load_form(dataset);
		
		    // fields default properties
		    var Default_field = function() {
		        this.context = {};
		        this.domain = [];
		        this.help = "";
		        this.readonly = false;
		        this.required = true;
		        this.selectable = true;
		        this.states = {};
		        this.views = {};
		    };
		    var Default_node = function(field_name) {
		        this.tag = "field";
		        this.children = [];
		        this.required = true;
		        this.attrs = {
		            invisible: "False",
		            modifiers: '{"required":true}',
		            name: field_name,
		            nolabel: 'True',
		        };
		    };
		    // Append fields to the field_manager
		    field_manager.fields_view.fields = {};
		    for (var i=0; i<create_form_fields_arr.length; i++) {
		        field_manager.fields_view.fields[create_form_fields_arr[i].id] = _.extend(new Default_field(), create_form_fields_arr[i].field_properties);
		    }
		    // generate the create "form"
		    var create_form = [];
		    for (var i=0; i<create_form_fields_arr.length; i++) {
		    	var field_data = create_form_fields_arr[i];
                // create widgets
                var node = new Default_node(field_data.id);
                if (! field_data.required) node.attrs.modifiers = "";
                var field = new field_data.constructor(field_manager, node);
                self[field_data.id+"_field"] = field;
                create_form.push(field);
                // on update : change the last created line
                field.corresponding_property = field_data.corresponding_property;
    
                // append to DOM
                var $field_container = $(QWeb.render("form_create_field", {id: field_data.id, label: field_data.label}));
                field.appendTo($field_container.find("td"));
                self.$el.prepend($field_container);
                // now that widget's dom has been created (appendTo does that), bind events and adds tabindex
                if (field_data.field_properties.type != "many2one") {
                    // Triggers change:value TODO : moche bind ?
                    field.$el.find("input").keyup(function(e, field){ field.commit_value(); }.bind(null, null, field));
                }
                field.$el.find("input").attr("tabindex", field_data.tabindex);
                }
		    field_manager.do_show();
		    self.field_manager = field_manager;
		    return field_manager;
	    },    	
    });
