/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Documents View 
*    (see https://mukit.at).
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Lesser General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Lesser General Public License for more details.
*
*    You should have received a copy of the GNU Lesser General Public License
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_dms_view.DocumentsController', function(require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var mixins = require('web.mixins');
var config = require('web.config');
var session = require('web.session');
var framework = require('web.framework');
var web_client = require('web.web_client');
var crash_manager = require('web.crash_manager');

var files = require('muk_web_utils.files');
var async = require('muk_web_utils.async');
var mimetype = require('muk_web_utils.mimetype');

var Widget = require('web.Widget');

var FileUpload = require('muk_dms_mixins.FileUpload');
var DocumentDropFileDialog = require('muk_dms_dialogs.DocumentDropFileDialog');
var DocumentDropFilesDialog = require('muk_dms_dialogs.DocumentDropFilesDialog');
var DocumentFileInfoDialog = require('muk_dms_dialogs.DocumentFileInfoDialog');
var DocumentDirectoryInfoDialog = require('muk_dms_dialogs.DocumentDirectoryInfoDialog');

var _t = core._t;
var QWeb = core.qweb;

var DocumentsController = Widget.extend(FileUpload, {
    custom_events: _.extend({}, Widget.prototype.custom_events, {
    	drop_items: '_dropItems',
    	tree_changed: '_treeChanged',
    	move_node: '_moveNode',
    	copy_node: '_copyNode',
    	rename_node: '_renameNode',
    	delete_node: '_deleteNode',
    }),
	init: function (parent, model, renderer, params) {
        this._super.apply(this, arguments);
        this.params = params || {};
        this.config = this._buildTreeConfig();
        this.model = new model(this, _.extend({}, params.model, {}));
        this.renderer = new renderer(this, _.extend({}, params.render, {
        	dnd: params.dnd,
        	config: this.config,
        }));
        this.FileReaderAPI = window.File && window.FileReader && window.FileList && window.Blob;
        this.searchTester = new RegExp(/\%|\_/);
    },
    start: function () {
        return $.when(
            this._super.apply(this, arguments),
            this.renderer.appendTo(this.$el)
        );
    },
    reload: function(message) {
    	this.refresh(message);
    },
    refresh: function(message) {
    	var jstree = this.renderer.$tree.jstree(true);
    	if(message && message.ids && message.model && !message.create) {
    		var nodes = _.each(_.keys(_.chain(message.ids).map(function(id) {
	    		return jstree.get_parent(message.model.split(".")[1] + "_" + id);
	    	}).filter(function(parent) {
	    		return !!parent;
	    	}).groupBy(function(parent) {
	    		return parent;
	    	}).value()), function(node, index, nodes) {
    			jstree.refresh_node(node);
    		});
    	} else if(message && message.ids && message.model && message.create) {
    		var id = message.ids && message.ids.length > 0 ? message.ids[0] : false;
    		if(id && message.model) {
    			var field = message.model === 'muk_dms.directory' ?
    				'parent_directory' : 'directory';
    			this._rpc({
    				 fields: [field],
    				 domain: [['id', '=', id]],
    				 model: message.model,
    				 method: 'search_read',
    				 context: session.user_context,
    			}).then(function(records) {
    				jstree.refresh_node(message.model.split(".")[1] + "_" + records[0][field]);
    			});
    		}
    	} else {
    		jstree.refresh();
    	}
    },
    refreshNode: _.memoizeDebounce(function(node) {
    	this.renderer.$tree.jstree(true).refresh_node(node);
    }, 250),
    refreshParent: _.memoizeDebounce(function(node) {
    	var jstree = this.renderer.$tree.jstree(true);
    	var parent = jstree.get_parent(node);
    	if(parent) {
    		this.renderer.$tree.jstree(true).refresh_node(parent);
    	} else {
    		this.refreshNode(node);
    	}
    }, 250),
    search: function(val, node) {
    	this.renderer.$tree.jstree(true).search(val, false, this.params.show_only_matches || true, node);
    },
    getSelectedItem: function() {
    	var jstree = this.renderer.$tree.jstree(true);
    	var selected = jstree.get_selected();
		return selected.length > 0 ? jstree.get_node(selected[0]) : false;
    },
    getTopSelectedItem: function() {
    	var jstree = this.renderer.$tree.jstree(true);
    	var selected = jstree.get_top_selected();
    	return selected.length > 0 ? jstree.get_node(selected[0]) : false;
    },
    getSelectedDirectory: function() {
    	var jstree = this.renderer.$tree.jstree(true);
    	var selected = jstree.get_top_selected(true);
    	var directories = _.filter(selected, function(node) {
    		return node.data.odoo_model === "muk_dms.directory";
    	});
    	if(directories.length > 0) {
    		return directories[0];
    	} else if(selected.length > 0) {
    		return jstree.get_node(jstree.get_parent(selected[0]));
    	} else {
    		return false;
    	}
    },
    getParentNode: function(node) {
    	var jstree = this.renderer.$tree.jstree(true);
    	return jstree.get_node(jstree.get_parent(node));
    },
    getSelectedItems: function() {
    	return this.renderer.$tree.jstree(true).get_selected(true);
    },
    getTopSelectedItems: function() {
    	return this.renderer.$tree.jstree(true).get_top_selected(true);
    },
    _buildTreeConfig: function() {
		var plugins = this.params.plugins || [
			"conditionalselect", "massload", "wholerow",
			"state", "sort", "search", "types"
		];
		if(this.params.dnd) {
			plugins = _.union(plugins, ["dnd"]);
		}
		if(this.params.contextmenu) {
			plugins = _.union(plugins, ["contextmenu"]);
		}
		var config = {
        	core : {
        		widget: this,
        		animation: this.params.animation || 0,
        		multiple: this.params.disable_multiple ? false : true,
        	    check_callback: this.params.check_callback || this._checkCallback.bind(this),
        		themes: this.params.themes || {
                    name: 'proton',
                    responsive: true
                },
        		data: this._loadData.bind(this),
        	},
        	massload: this._massloadData.bind(this),
        	contextmenu: this.params.contextmenu_items || { 
        		items: this._loadContextMenu.bind(this),
        	},
            search: this.params.search || {
            	ajax: this._searchData.bind(this),
            	show_only_matches: true,
            	search_callback: this._searchCallback.bind(this),
            },
        	state : {
        		key: this.params.key || "documents" 
        	},
        	conditionalselect: this.params.conditionalselect || this._checkSelect.bind(this),
        	dnd: this.params.dnd_options || {
        		touch: false,
        	},
	        plugins: plugins,
    	};
		return config;
    },
    _checkCallback: function (operation, node, parent, position, more) {
    	if(operation === "copy_node" || operation === "move_node") {
    		// prevent moving a root node
    		if(node.parent === "#") {
    			return false;
            }
    		// prevent moving a child above or below the root
    		if(parent.id === "#") {
    			return false;
	        }
    		// prevent moving a child to a settings object
    		if(parent.data && parent.data.odoo_model === "muk_dms.settings") {
    			return false;
            }
    		// prevent moving a child to a file
    		if(parent.data && parent.data.odoo_model === "muk_dms.file") {
    			return false;
            }
    	}
    	if(operation === "move_node") {
    		// prevent duplicate names
    		if(node.data && parent.data) {
    			var names = [];
    			var jstree = this.renderer.$tree.jstree(true);
    			_.each(parent.children, function(child, index, children) {
    				var child_node = jstree.get_node(child);
    				if(child_node.data && child_node.data.odoo_model === parent.data.odoo_model) {
    					names.push(child_node.data.name);
    				}
    			});
    			if(names.indexOf(node.data.name) > -1) {
    				return false;
    			}
            }
        }
    	return true;
    },
    _checkSelect: function(node, event) {
    	if(this.params.filesOnly && node.data.odoo_model !== "muk_dms.file") {
    		return false;
    	}
    	return !(node.parent === '#' && node.data.odoo_model === "muk_dms.settings");
    },
    _treeChanged: function(ev) {
//    	$("#menuContinenti").prop('disabled', function (_, val) { return ! val; });
    },
    _loadData: function (node, callback) {
    	this.model.load(node).then(function(data) {
			callback.call(this, data);
		});
    },
    _massloadData: function (data, callback) {
    	this.model.massload(data).then(function(data) {
			callback.call(this, data);
		});
    },
    _searchData: function(val, callback) {
    	var node = this.getSelectedDirectory();
    	if(node) {
	    	this.model.search(val, node, {
	    		search: {
	    			operator: this.searchTester.test(val) ? "=ilike" : "ilike",
	    		}
	    	}).then(function(data) {
				callback.call(this, data);
			});
    	} else {
    		callback.call(this, []);
    	}
    },
    _searchCallback: function (val, node) {
    	if(this.searchTester.test(val)) {
    		var regex = new RegExp(val.replace(/\%/g, ".*").replace(/\_/g, "."), "i");
        	try {
        		return regex.test(node.text); 
        	} catch(ex) {
        		return false; 
        	} 
    	} else {
    		var lval = val.toLowerCase();
    		var ltext = node.text.toLowerCase();
    		if(lval === ltext || ltext.indexOf(lval) !== -1) {
    			return true;
    		} else {
    			return false;
    		}
    	}
    },
    _dropItems: function(ev) {
    	var node = this.getSelectedDirectory();
		if (node) {
			files.getFileTree(ev.data.items, true).then(
				this._uploadFiles.bind(this, node.data.odoo_id) 
			);
		} else {
			this.do_warn(_t("Upload Error"), _t("No Directory has been selected!"));
		}
    },	
    _openInfo: function(node) {
		if(node.data.odoo_model == "muk_dms.file") {
			new DocumentFileInfoDialog(this, {
				id: node.data.odoo_id,
		    }).open();
    	} else {
    		new DocumentDirectoryInfoDialog(this, {
				id: node.data.odoo_id,
		    }).open();
    	}
    },
	_openNode: function(node) {
		var self = this;
		this.do_action({
    		type: 'ir.actions.act_window',
            res_model: node.data.odoo_model,
            res_id: node.data.odoo_id,
            views: [[false, 'form']],
            target: this.params.action_open_dialog ? 'new' : 'current',
            flags: {'form': {'initial_mode': 'readonly'}},
            context: session.user_context,
        }, {
            on_reverse_breadcrumb: function() {
            	self.trigger_up('reverse_breadcrumb', {});
            }
        });
    },
    _editNode: function(node) {
		var self = this;
    	this.do_action({
    		type: 'ir.actions.act_window',
            res_model: node.data.odoo_model,
            res_id: node.data.odoo_id,
            views: [[false, 'form']],
            target: this.params.action_open_dialog ? 'new' : 'current',
    	    flags: {'form': {'mode': 'edit', 'initial_mode': 'edit'}},
            context: session.user_context,
        }, {
            on_reverse_breadcrumb: function() {
            	self.trigger_up('reverse_breadcrumb', {});
            }
        });
    },
    _createNode: function(node, type) {
		var self = this;
    	var context = {};
    	if(type == "muk_dms.file") {
    		context = $.extend(session.user_context, {
    			default_directory: node.data.odoo_id
            });
    	} else if(type == "muk_dms.directory") {
    		context = $.extend(session.user_context, {
    			default_parent_directory: node.data.odoo_id
            });
    	}
    	this.do_action({
    		type: 'ir.actions.act_window',
            res_model: type,
            views: [[false, 'form']],
            target: this.params.action_open_dialog ? 'new' : 'current',
            flags: {'form': {'mode': 'edit', 'initial_mode': 'edit'}},
            context: session.user_context,
        }, {
            on_reverse_breadcrumb: function() {
            	self.trigger_up('reverse_breadcrumb', {});
            }
        });
    },
    _moveNode: function(ev) {
    	var self = this;
		var vals = {};
    	var node = ev.data.node;
		var parent = this.renderer.$tree.jstree(true).get_node(ev.data.new_parent);
		if(node.data.odoo_model === "muk_dms.file") {
			vals.directory = parent.data.odoo_id;
		} else if(node.data.odoo_model === "muk_dms.directory") {
			vals.parent_directory = parent.data.odoo_id;
		}
		this._rpc({
            model: node.data.odoo_model,
            method: 'write',
            args: [node.data.odoo_id, vals],
            context: session.user_context,
		}).done(function() {
			self.do_notify(node.text + _t(" has been moved!"));
			self.refreshNode(ev.data.new_parent);
			self.refreshNode(ev.data.old_parent);
		}).fail(function() {
			self.do_warn(node.text + _t(" couldn't be moved!"));
			self.refreshNode(ev.data.new_parent);
			self.refreshNode(ev.data.old_parent);
		});
    },
    _deleteNode: function(ev) {
    	var self = this;
    	var node = ev.data.node;
    	var parent = this.renderer.$tree.jstree(true).get_parent(ev.data.node);
		this._rpc({
            model: node.data.odoo_model,
            method: 'unlink',
            args: [node.data.odoo_id],
            context: session.user_context,
		}).done(function() {
			self.do_notify(node.text + _t(" has been deleted!"));
			self.refreshNode(parent);
		}).fail(function() {
			self.refreshNode(parent);
			self.do_warn(node.text + _t(" couldn't be deleted!"));
		});
    },
    _deleteNodes: function(nodes) {
    	var self = this;
    	var data = _.chain(nodes).map(function(node) {
    		return {model: node.data.odoo_model, id: node.data.odoo_id};
    	}).groupBy(function(tuple) {
    		return tuple.model;
    	}).value();
		data = _.mapObject(data, function(values, key) {
    		return _.map(values, function(value) {
    			return value.id;
    		});
    	});
		_.each(_.keys(data), function(key) {
			self._rpc({
	            model: key,
	            method: 'unlink',
	            args: [data[key]],
	            context: session.user_context,
			}).done(function() {
				self.do_notify(_t("The records have been deleted!"));
				self.refresh();
			}).fail(function() {
				self.refresh();
				self.do_warn(_t("The records couldn't be deleted!"));
			});
		});
    },
    _copyNode: function(ev) {
    	var self = this;
		var vals = {};
    	var node = ev.data.node;
    	var original = ev.data.original;
		var parent = this.renderer.$tree.jstree(true).get_node(ev.data.parent);
		if(original.data.odoo_model === "muk_dms.file") {
			vals.directory = parent.data.odoo_id;
		} else if(original.data.odoo_model === "muk_dms.directory") {
			vals.parent_directory = parent.data.odoo_id;
		}
		this._rpc({
            model: original.data.odoo_model,
            method: 'copy',
            args: [original.data.odoo_id, vals],
            context: session.user_context,
		}).done(function(copy_id) {
			node.data = original.data;
			node.id = original.data.odoo_model.split(".") + "_" + copy_id;
			self.do_notify(node.text + _t(" has been copied!"));
			self.refreshNode(parent);
		}).fail(function() {
			self.refreshNode(parent);
			self.do_warn(node.text + _t(" couldn't be copied!"));
		});
    },
    _renameNode: function(ev) {
    	var self = this;
    	var node = ev.data.node;
		this._rpc({
            model: node.data.odoo_model,
            method: 'write',
            args: [node.data.odoo_id, {'name': ev.data.text}],
            context: session.user_context,
		}).done(function() {
			self.do_notify(node.text + _t(" has been renamed!"));
		}).fail(function() {
			self.refresh();
			self.do_warn(node.text + _t(" couldn't be renamed!"));
		});
    },
    _createDirecotry: function(node, name) {
		return this._rpc({
    		route: '/dms/view/tree/create/directory',
    		params: {
    			name: name,
            	parent_directory: node.data.odoo_id,
            	context: _.extend({}, {
                	mail_create_nosubscribe: true,
                	mail_create_nolog: true,
                }, session.user_context),
            },
		});
    },
    _replaceFile: function(node) {
    	var self = this;
    	new DocumentDropFileDialog(this, {
			id: node.data.odoo_id,
			name: node.data.name,
			callback: function() {
				self.refreshParent(node);
			},
	    }).open();
    },
    _uploadFilesDialog: function(node) {
    	var self = this;
    	new DocumentDropFilesDialog(this, {
			id: node.data.odoo_id,
			name: node.data.name,
			callback: function() {
				self.refreshNode(node);
			},
	    }).open();
    },
    _executeOperation: function(node, action_id) {
    	var self = this;
    	this._rpc({
            model: 'muk_dms_actions.action',
            method: 'trigger_actions',
            args: [[action_id], node.data.odoo_id],
        }).then(function (result) {
        	if (_.isObject(result)) {
                return self.do_action(result);
            } else {
                return self.reload();
            }
        });
    },
    _loadContextMenu: function(node, callback) {
    	var menu = {};
    	var jstree = this.renderer.$tree.jstree(true);
    	if(node.data) {
    		if(node.data.odoo_model === "muk_dms.directory") {
    			menu = this._loadContextMenuBasic(jstree, node, menu);
    			menu = this._loadContextMenuDirectory(jstree, node, menu);
    		} else if(node.data.odoo_model === "muk_dms.file") {
    			menu = this._loadContextMenuBasic(jstree, node, menu);
    			menu = this._loadContextMenuFile(jstree, node, menu);
    		}
    	}
    	return menu;
    },
    _loadContextMenuBasic: function($jstree, node, menu) {
    	var self = this;
    	menu.rename = {
			separator_before: false,
			separator_after: false,
			icon: "fa fa-pencil",
			label: _t("Rename"),
			action: function (data) {
				$jstree.edit(node);
			},
			_disabled: function (data) {
    			return !node.data.perm_write;
			},
		};
    	menu.action = {
			separator_before: false,
			separator_after: false,
			icon: "fa fa-bolt",
			label: _t("Actions"),
			action: false,
			submenu: {
				cut: {
					separator_before: false,
					separator_after: false,
					icon: "fa fa-scissors",
					label: _t("Cut"),
					action: function (data) {
						$jstree.cut(node);
					},
				},
				copy: {
					separator_before: false,
					separator_after: false,
					icon: "fa fa-clone",
					label: _t("Copy"),
					action: function (data) {
						$jstree.copy(node);
					},
				},
			},
			_disabled: function (data) {
				return !node.data.perm_read;
			},
		};
    	menu.delete = {
    		separator_before: false,
			separator_after: false,
			icon: "fa fa-trash-o",
			label: _t("Delete"),
			action: function (data) {
				$jstree.delete_node(node);
			},
			_disabled: function (data) {
    			return !node.data.perm_unlink;
			},
		};
    	return menu;
    },
    _loadContextMenuDirectory: function($jstree, node, menu) {
    	var self = this;
    	if(menu.action && menu.action.submenu) {
    		menu.action.submenu.paste = {
    			separator_before: false,
    			separator_after: false,
				icon: "fa fa-clipboard",
    			label: _t("Paste"),
    			action: function (data) {
    				$jstree.paste(node);
    			},
    			_disabled: function (data) {
	    			return !$jstree.can_paste() && !node.data.perm_create;
    			},
    		};
    	}
    	return menu;
    },
    _loadContextMenuFile: function($jstree, node, menu) {
    	var self = this;
    	menu.download = {
			separator_before: false,
			separator_after: false,
			icon: "fa fa-download",
			label: _t("Download"),
			action: function(data) {
				framework.blockUI();
				session.get_file({
				    'url': '/web/content',
				    'data': {
				        'id': node.data.odoo_id,
				        'download': true,
				        'field': 'content',
				        'model': 'muk_dms.file',
				        'filename_field': 'name',
				        'filename': node.data.filename
				    },
				    'complete': framework.unblockUI,
				    'error': crash_manager.rpc_error.bind(crash_manager)
				});
			}
    	};
    	return menu;
    },
});

return DocumentsController;

});