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

odoo.define('muk_dms_views.documents', function(require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var session = require('web.session');
var web_client = require('web.web_client');
var framework = require('web.framework');
var crash_manager = require('web.crash_manager');

var dms_utils = require('muk_dms.utils');

var ControlPanelMixin = require('web.ControlPanelMixin');
var PreviewHelper = require('muk_dms_preview_file.PreviewHelper');

var Widget = require('web.Widget');
var Dialog = require('web.Dialog');

var _t = core._t;
var QWeb = core.qweb;

var DocumentTreeView = Widget.extend(ControlPanelMixin, {
	cssLibs: [
        '/muk_dms/static/lib/jquery-splitter/css/jquery.splitter.css',
        '/muk_dms/static/lib/jsTree/themes/default/style.css',
    ],
    jsLibs: [
        '/muk_dms/static/lib/jquery-splitter/js/jquery.splitter.js',
        '/muk_dms/static/lib/jsTree/jstree.js',
    ],
	template: 'muk_dms.DocumentTreeView',
	events: {
        "click button.refresh": "refresh",
        "click button.show_preview": "show_preview",
        "click button.hide_preview": "hide_preview",
    },
	init: function(parent, context) {
        this._super(parent, context);
        this.splitter = false;
    },
    willStart: function() {
    	 var self = this;
         return $.when(ajax.loadLibs(this), this._super()).then(function() {
             return self._load_data();
         });
    },
    start: function() {
        var self = this;
        return this._super().then(function() {
            self.update_cp();
            self.render();
        	self.$('[data-toggle="tooltip"]').tooltip();
            self.$el.parent().addClass('oe_background_grey');
        });
    },
    refresh: function() {
        var self = this;
    	this._load_data().then(function(data) {
    		self.$el.find('.oe_document_tree').jstree(true).settings.core.data = data;
        	self.$el.find('.oe_document_tree').jstree(true).refresh();
    	});
    },
    on_reverse_breadcrumb: function() {
        web_client.do_push_state({});
        this.update_cp();
    },
    render: function() {
        var self = this;
    	self.$el.find('.oe_document_tree').jstree({
			'widget': self,
        	'core': {
        		'animation': 0,
        		'multiple': false,
        	    'check_callback': true,
        	    'themes': { "stripes": true },
        		'data': self.data
        	},
        	'plugins': [
        	    "contextmenu", "search", "sort", "state", "wholerow", "types"
            ],
        	'search': {
        	    'case_insensitive': false,
        	    'show_only_matches': true,
        	    'search_callback': function (str, node) {
        	    	try {
        	    		return node.text.match(new RegExp(str)); 
        	    	} catch(ex) {
        	    		return false; 
        	    	} 
        	    }
        	},
        	'contextmenu': {
                items: self.context_menu
            },
    	}).on('open_node.jstree', function (e, data) {
    		data.instance.set_icon(data.node, "fa fa-folder-open-o"); 
    	}).on('close_node.jstree', function (e, data) { 
    		data.instance.set_icon(data.node, "fa fa-folder-o"); 
    	}).bind('loaded.jstree', function(e, data) {
    		self.show_preview();
    	}).on('changed.jstree', function (e, data) {
    		if(data.node) {
    			self.selected_node = data.node;
    			self.$buttons.find('button.open').prop('disabled', !self.selected_node.data.perm_read);
    			self.$buttons.find('button.edit').prop('disabled', !self.selected_node.data.perm_write);
    			$("#menuContinenti").prop('disabled', function (_, val) { return ! val; });
    			if(self.show_preview_active && data.node.data.odoo_model == "muk_dms.file") {
    				PreviewHelper.createFilePreviewContent(data.node.data.odoo_id, self).then(function($content) {
    					self.$el.find('.oe_document_preview').html($content);
    				});       		
        		}
    		}
    	});
		var timeout = false;
		self.$searchview.find('#tree_search').keyup(function() {
    	    if(timeout) {
    	    	clearTimeout(timeout); 
    	    }
    	    timeout = setTimeout(function() {
    	    	var v = self.$searchview.find('#tree_search').val();
    	    	self.$('.oe_document_tree').jstree(true).search(v);
    	    }, 250);
	   });
    },
    update_cp: function() {
    	if (!this.$buttons) {
            this.$buttons = $(QWeb.render('muk_dms.DocumentTreeViewButtons', {
                widget: this,
            }));
            this.$buttons.find('.open').on('click', _.bind(this.open, this));
            this.$buttons.find('.edit').on('click', _.bind(this.edit, this));
        }
    	if (!this.$pager) {
            this.$pager = $(QWeb.render('muk_dms.DocumentTreeViewActions', {
                widget: this,
            }));
            this.$pager.find('.refresh').on('click', _.bind(this.refresh, this));
        }
    	if (!this.$switch_buttons) {
            this.$switch_buttons = $(QWeb.render('muk_dms.DocumentTreeViewOptions', {
                widget: this,
            }));
        }
    	if (!this.$searchview) {
            this.$searchview = $(QWeb.render('muk_dms.DocumentTreeViewSearch', {
                widget: this,
            }));
        }
        this.update_control_panel({
            cp_content: {
                $buttons: this.$buttons,
                $pager: this.$pager,
                $searchview: this.$searchview,
                $switch_buttons: this.$switch_buttons,
            },
            breadcrumbs: this.getParent().get_breadcrumbs(),
        });
        this.$switch_buttons.parent().find('.show_preview').on('click', _.bind(this.show_preview, this));
        this.$switch_buttons.parent().find('.hide_preview').on('click', _.bind(this.hide_preview, this));
    },
    show_preview: function() {
		this.show_preview_active = true;
    	if(!this.$switch_buttons.parent().find('.show_preview').hasClass("active")) {
        	this.$switch_buttons.parent().find('.show_preview').addClass("active");
        	this.$switch_buttons.parent().find('.hide_preview').removeClass("active");
    		this.$el.find('.oe_document_col_preview').show();
        	this.splitter = this.$el.find('.oe_document_row').split({
        	    orientation: 'vertical',
        	    limit: 100,
        	    position: '60%'
        	});
    	}
    },
    hide_preview: function() {
		this.show_preview_active = false;
    	if(!this.$switch_buttons.parent().find('.hide_preview').hasClass("active")) {
    		this.$switch_buttons.parent().find('.hide_preview').addClass("active");
    		this.$switch_buttons.parent().find('.show_preview').removeClass("active");
    		this.$el.find('.oe_document_col_preview').hide();
    		this.$el.find('.oe_document_col_tree').width('100%');
    		if(this.splitter) {
    			this.splitter.destroy();
    		}
    		this.splitter = false;
    	}
    },
    _load_data: function() {
    	var self = this;
    	var output = $.Deferred();	
    	this._load_directories().then(function(directories, ids) {
    		self._load_files(ids).then(function(files) {
    			self.data = directories.concat(files);
    			output.resolve(self.data);
        	});
    	});
    	return output;
    },
    _load_directories: function() {
    	var output = $.Deferred();	
    	var fields = ['name', 'parent_directory',
    				  'perm_read', 'perm_create',
    				  'perm_write', 'perm_unlink'];
    	this._rpc({
            fields: fields,
            model: 'muk_dms.directory',
            method: 'search_read',
            context: session.user_context,
        }).then(function(directories) {
        	var data = [];
    		var directory_ids = _.map(directories, function(directory, index) { 
    			return directory.id; 
    		});
    		_.each(directories, function(value, key, list) {
        		data.push({
        			id: "directory_" + value.id,
        			parent: (value.parent_directory &&
        					$.inArray(value.parent_directory[0], directory_ids) !== -1 ?
        							"directory_" + value.parent_directory[0] : "#"),
        			text: value.name,
        			icon: "fa fa-folder-o",
        			type: "directory",
        			data: {
        				container: false,
        				odoo_id: value.id,
        				odoo_parent_directory: value.parent_directory[0],
        				odoo_model: "muk_dms.directory",
        				perm_read: value.perm_read,
        				perm_create: value.perm_create,
        				perm_write: value.perm_write,
        				perm_unlink: value.perm_unlink,
        			}
        		});
        	});
    		output.resolve(data, directory_ids);
		});
    	return output;
    },
    _load_files: function(directory_ids) {
    	var output = $.Deferred();	
    	var fields = ['name', 'mimetype', 'extension', 
    				  'directory', 'size', 'perm_read',
    				  'perm_create', 'perm_write', 
    				  'perm_unlink'];
    	this._rpc({
            fields: fields,
            model: 'muk_dms.file',
            method: 'search_read',
            context: session.user_context,
        }).then(function(files) {
    		var data = [];
    		_.each(files, function(value, key, list) {
    			if(!($.inArray(value.directory[0], directory_ids) !== -1)) {
    				directory_ids.push(value.directory[0]);
    				data.push({
    					id: "directory_" + value.directory[0],
    					parent: "#",
    					text: value.directory[1],
    					icon: "fa fa-folder-o",
    					type: "directory",
    					data: {
    						container: true,
    						odoo_id: value.directory[0],
    						odoo_parent_directory: false,
    						odoo_model: "muk_dms.directory",
    						perm_read: false,
    						perm_create: false,
    						perm_write: false,
    						perm_unlink: false,
    					}
    				});
    			}
        		data.push({
        			id: "file," + value.id,
        			parent: "directory_" + value.directory[0],
        			text: value.name,
        			icon: dms_utils.mimetype2fa(value.mimetype, {prefix: "fa fa-"}),
        			type: "file",
        			data: {
	        			odoo_id: value.id,
        				odoo_parent_directory: value.directory[0],
	        			odoo_model: "muk_dms.file",
        				filename: value.name,
        				file_size: value.file_size,
        				preview_link: value.link_preview,
        				download_link: value.link_download,
        				file_extension: value.file_extension,
        				mime_type: value.mime_type,
        				perm_read: value.perm_read,
        				perm_create: value.perm_create,
        				perm_write: value.perm_write,
        				perm_unlink: value.perm_unlink,
        			}
        		});
        	});
    		output.resolve(data);
    	});
    	return output;
    },
    on_reverse_breadcrumb: function() {
    	web_client.do_push_state({});
        this.update_cp();
    },
    open: function() {
    	this.do_action({
            type: 'ir.actions.act_window',
            res_model: this.selected_node.data.odoo_model,
            res_id: this.selected_node.data.odoo_id,
            views: [[false, 'form']],
            target: 'current',
            context: session.user_context,
        }, {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb
        });
    },
    edit: function() {
    	this.do_action({
    		type: 'ir.actions.act_window',
            res_model: this.selected_node.data.odoo_model,
            res_id: this.selected_node.data.odoo_id,
            views: [[false, 'form']],
            target: 'current',
            flags: {'initial_mode': 'edit'},
            context: session.user_context,
        }, {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb
        });
    },
    create: function(model, parent) {
    	var context = {};
    	if(model == "muk_dms.file") {
    		context = $.extend(session.user_context, {
    			default_directory: parent
            });
    	} else if(model == "muk_dms.directory") {
    		context = $.extend(session.user_context, {
    			default_parent_directory: parent
            });
    	}
    	this.do_action({
    		type: 'ir.actions.act_window',
            res_model: model,
            views: [[false, 'form']],
            target: 'current',
            context: context,
        }, {
            on_reverse_breadcrumb: this.on_reverse_breadcrumb
        });
    },
    context_menu: function(node, cp) {
    	var items = {}
    	if(node.data.perm_read) {
    		items.open = {
    			separator_before: false,
    			separator_after: false,
    			_disabled: false,
    			icon: "fa fa-external-link-square",
    			label: _t("Open"),
    			action: function(data) {
    				var inst = $.jstree.reference(data.reference);
    				inst.settings.widget.open();
    			}
    		};
    	}
    	if(node.data.perm_write) {
    		items.edit = {
    			separator_before: false,
    			separator_after: false,
    			_disabled: false,
    			icon: "fa fa-pencil",
    			label: _t("Edit"),
    			action: function(data) {
    				var inst = $.jstree.reference(data.reference);
    				inst.settings.widget.edit();
    			}
    		};
    	}
    	if(node.data.odoo_model == "muk_dms.file" && node.data.perm_read) {
    		items.download = {
    			separator_before: false,
    			separator_after: false,
    			_disabled: false,
    			icon: "fa fa-download",
    			label: _t("Download"),
    			action: function(data) {
    				var inst = $.jstree.reference(data.reference);
    				var	obj = inst.get_node(data.reference);
					framework.blockUI();
					session.get_file({
					    'url': '/web/content',
					    'data': {
					        'id': obj.data.odoo_id,
					        'download': true,
					        'field': 'content',
					        'model': 'muk_dms.file',
					        'filename_field': 'name',
					        'filename': obj.data.filename
					    },
					    'complete': framework.unblockUI,
					    'error': crash_manager.rpc_error.bind(crash_manager)
					});
    			}
    		};
    	} else if(node.data.odoo_model == "muk_dms.directory" && node.data.perm_create) {
    		items.create = {
    			separator_before: false,
    			icon: "fa fa-plus-circle",
    			separator_after: false,
    			label: _t("Create"),
    			action: false,
    			submenu: {
    				directory: {
    					separator_before: false,
    					separator_after: false,
    					label: _t("Directory"),
    					icon: "fa fa-folder",
    					action: function(data) {
    						var inst = $.jstree.reference(data.reference);
    						var	obj = inst.get_node(data.reference);
    						inst.settings.widget.create("muk_dms.directory", obj.data.odoo_id);
    					}
    				},
    				file : {
    					separator_before: false,
    					separator_after: false,
    					label: _t("File"),
    					icon: "fa fa-file",
    					action: function(data) {
    						var inst = $.jstree.reference(data.reference);
    						var	obj = inst.get_node(data.reference);
    						inst.settings.widget.create("muk_dms.file", obj.data.odoo_id);
    					}
    				},
    			}
    		};
    	}
    	return items;
    }
});

core.action_registry.add('muk_dms_views.documents', DocumentTreeView);

return DocumentTreeView

});