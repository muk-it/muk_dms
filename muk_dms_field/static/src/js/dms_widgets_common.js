/**********************************************************************************
* 
*    Copyright (C) 2017 MuK IT GmbH
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Affero General Public License as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Affero General Public License for more details.
*
*    You should have received a copy of the GNU Affero General Public License
*    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_dms_field_widgets.common', function(require) {
"use strict";

var core = require('web.core');
var data = require('web.data');
var utils = require('web.utils');
var pyeval = require('web.pyeval');
var session = require('web.session');
var framework = require('web.framework');
var data_manager = require('web.data_manager');
var form_common = require('web.form_common');

var Widget = require('web.Widget');
var Model = require("web.Model");
var Dialog = require('web.Dialog');
var ListView = require('web.ListView');
var SearchView = require('web.SearchView');

var Directory = new Model('muk_dms.directory', session.user_context);

var _t = core._t;
var QWeb = core.qweb;

var FolderCompletionFieldMixin = {
    get_search_result: function(search_val) {
        var self = this;
        this.last_query = search_val;
        return Directory.query(['name'])
        .filter([['name', 'ilike', search_val]])
        .limit(10)
        .all().then(function (directories) {
        	self.last_search = directories;
            var values = _.map(directories, function(x) {
                return {
                    label: _.str.escapeHTML(x.name.trim()) || data.noDisplayContent,
                    value: x.name,
                    name: x.name,
                    id: x.id,
                };
            });
            if (values.length > 10) {
                values = values.slice(0, self.limit);
                values.push({
                    label: _t("Search More..."),
                    action: function() {
                    	Directory.query(['id'])
                        .filter([['name', 'ilike', search_val]])
                        .limit(200)
                        .all().then(function (directories) {
                        	self._search_create_popup("search", directories);
                        });
                    },
                    classname: 'o_m2o_dropdown_option'
                });
            }
            var name_result = _.map(directories, function(x) {return x.name;});
            if (search_val.length > 0 && !_.include(name_result, search_val)) {
                values.push({
                    label: _.str.sprintf(_t('Create "<strong>%s</strong>"'),
                        $('<span />').text(search_val).html()),
                    action: function() {
                        self._create(search_val);
                    },
                    classname: 'o_m2o_dropdown_option'
                });
            }

            return values;
        });
    },
    _create: function(name) {
        this._search_create_popup("form", undefined, this._create_context(name));
  
    },
    _search_create_popup: function(view, directories, context) {
        var self = this;
        new form_common.SelectCreateDialog(this, _.extend({}, (this.options || {}), {
            res_model: 'muk_dms.directory',
            domain: self.build_domain(),
            context: new data.CompoundContext(self.build_context(), context || {}),
            title: (view === 'search' ? _t("Search: ") : _t("Create: ")) + this.string,
            initial_ids: _.map(directories, function(x) {return x.id;}),
            initial_view: view,
            disable_multiple_selection: true,
            on_selected: function(element_ids) {
                self.directory_selected(element_ids[0]);
                self.focus();
            }
        })).open();
    },
    _create_context: function(name) {
        return {"default_name": name};
    },
    directory_selected: function(id) {},
};

var FolderSearchDialog = Dialog.extend({
	init: function(parent, options) {
		var self = this;
		_.defaults(options || {}, {
            title:  _t("Search: Directory"), 
            subtitle: '',
            size: 'large',
            $content: QWeb.render("FolderSearchDialog", {}),
            buttons: [
                {text: _t("Select"), classes: "btn-primary o_formdialog_save", click: function() {
                	self.select();
                }},
            	{text: _t("Close"), classes: "btn-default o_form_button_cancel", close: true}
			],
        });
		this.directories = false;
    	this.selected_directory = false;
        this._super(parent, options);
    },
    init_data: function() {
        var self = this;
        Directory.query(['name', 'parent_directory']).all().then(function(directories) {
        	var data = [];
        	_.each(directories, function(value, key, list) {	        		
        		data.push({
        			id: value.id,
        			parent: (value.parent_id ? value.parent_id[0] : "#"),
        			text: value.name,
        		});
        	});
        	self.directories = directories;
        	self.$('.dir_tree').jstree({ 
	        	core: {
	        		animation: 150,
	        		multiple: false,
	        	    check_callback: true,
	        	    themes: { "stripes": true },
	        		data: data
	        	},
	        	plugins: [
	        	    "unique", "contextmenu", "search", "wholerow"
	            ],
	            contextmenu: {
	                items: {
	                	create: {
	    					separator_before: false,
	    					separator_after: false,
	    					_disabled: false,
	    					icon: "fa fa-plus-circle",
	    					label: _t("Create"),
	    					action: function (data) {
	    						var inst = $.jstree.reference(data.reference);
	    						var	obj = inst.get_node(data.reference);
	    						inst.create_node(obj, {}, "last", function (new_node) {
    								inst.edit(new_node, _t("New"), function(node) {
    									Directory.call("create", [{name: node.text, parent_directory: obj.id}])
    				    				.done(function (result) {
	    									self.$('.dir_tree').jstree(true).set_id(node, result);
    				    				})
    				    				.fail(function(xhr, status, text) {
    				    					self.do_warn(_t("Create..."), _t("An error occurred during create!"));
    				    				});
    								});
	    						});
	    					}
	    				},
	                }
	            },
	        }).bind('loaded.jstree', function (e, data) {
        	    var depth = 3;
        	    data.instance.get_container().find('li').each(function (i) {
        	        if (data.instance.get_path($(this)).length <= depth) {
        	        	data.instance.open_node($(this));
        	        }
        	    }); 
        	});
        	self.$('.dir_tree').on('changed.jstree', function (e, data) {
        		self.selected_directory = [data.node.id, data.node.text];
        	});
        	var timeout = false;
        	self.$('.muk_dialog_document_search_input').keyup(function() {
        	    if(timeout) {
        	    	clearTimeout(timeout); 
        	    }
        	    timeout = setTimeout(function() {
        	    	var v = self.$('.muk_dialog_document_search_input').val();
        	    	self.$('.dir_tree').jstree(true).search(v);
        	    }, 250);
    	   });
		});
    },
    open: function() {
        this._super();
        this.init_data();
        return this;
    },
    renderElement: function() {
        this._super();
    },
    select: function() {
    	this.trigger('directory_selected', this.selected_directory);
        this.close();
    }
});

return {
	FolderCompletionFieldMixin: FolderCompletionFieldMixin,
	FolderSearchDialog: FolderSearchDialog,
}

});