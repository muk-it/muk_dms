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

odoo.define('muk_dms_view.DocumentsModel', function(require) {
"use strict";

var ajax = require('web.ajax');
var core = require('web.core');
var mixins = require('web.mixins');
var config = require('web.config');
var session = require('web.session');
var field_utils = require('web.field_utils');

var mimetype = require('muk_web_utils.mimetype');

var Class = require('web.Class');
var Domain = require('web.Domain');
var ServicesMixin = require('web.ServicesMixin');
var EventDispatcherMixin = mixins.EventDispatcherMixin;

var _t = core._t;
var QWeb = core.qweb;

var DocumentsModel = Class.extend(EventDispatcherMixin, ServicesMixin, {
	init: function (parent, params) {
        EventDispatcherMixin.init.call(this);
        this.setParent(parent);
        this.setParams(params);
    },
    setParams: function(params) {
        this.params = $.extend(true, {}, {
        	storage: {
            	domain: [['is_hidden', '=', false]],
            	context: session.user_context,
            	show: true,
            }, 
            directory: {
            	domain: [],
            	context: session.user_context,
            }, 
            file: {
            	domain: [],
            	context: session.user_context,
            	show: true,
            },
            initial: undefined,
        }, params || {});
    },
    load: function(node, params) {
    	var args = this._buildArgs(params);
    	if(!node || node.id === "#") {
    		if(args.initial) {
    			return $.when(args.initial);
    		}
    		return this._loadInitialData(args);
    	}
    	return this._loadNode(node, args);
    },
    massload: function(nodes, params) {
    	var args = this._buildArgs(params);
    	return this._loadNodes(nodes, args);
    },
    search: function(val, node, params) {
    	var args = this._buildArgs(params);
    	return this._searchNodes(val, node, args);
    },
    _buildArgs: function(args) {
    	return $.extend(true, {
    		search: {
    			operator: "ilike",
    		}
    	}, this.params, args || {});
    },
    _buildDomain: function(base, domain) {
    	var result = new Domain(base);
    	result._addSubdomain(domain || []);
    	return result.toArray();
    },
    _loadStorages: function(args) {
    	return this._rpc({
            fields: _.union(args.storage.fields || [], [
            	'name', 'count_storage_directories'
            ]),
            domain: args.storage.domain || [['is_hidden', '=', false]],
            context: args.storage.context || session.user_context,
            model: 'muk_dms.storage',
            method: 'search_read',
        });
    },
    _loadDirectories: function(operator, value, args) {
    	return this._rpc({
            model: 'muk_dms.directory',
            method: 'search_read_parents',
            kwargs: {
                fields: _.union(args.directory.fields || [], [
                	'permission_read', 'permission_create',
    			  	'permission_write', 'permission_unlink',
    			  	'count_directories', 'count_files',
                	'name', 'parent_directory', '__last_update', 
    			]),
                domain: this._buildDomain(
                	[['storage', operator, value]],
                	args.directory.domain
                ), 
                context: args.directory.context || session.user_context,
            },
        });
    },
    _loadDirectoriesSingle: function(storage_id, args) {
    	return this._loadDirectories('=', storage_id, args);
    },
    _loadDirectoriesMulti: function(storage_ids, args) {
    	return this._loadDirectories('in', storage_ids, args);
    },
    _loadSubdirectories: function(operator, value, args) {
    	return this._rpc({
    		model: 'muk_dms.directory',
            method: 'search_read',
            fields: _.union(args.directory.fields || [], [
            	'permission_read', 'permission_create',
			  	'permission_write', 'permission_unlink',
			  	'count_directories', 'count_files',
            	'name', 'parent_directory', '__last_update', 
			]),
            domain: this._buildDomain(
            	[['parent_directory', operator, value]],
            	args.directory.domain
            ),
            context: args.file.context || session.user_context,
        });
    },
    _loadSubdirectoriesSingle: function(directory_id, args) {
    	return this._loadSubdirectories('=', directory_id, args);
    },
    _loadSubdirectoriesMulti: function(directory_ids, args) {
    	return this._loadSubdirectories('in', directory_ids, args);
    },
    _loadFiles: function(operator, value, args) {
    	return this._rpc({
            model: 'muk_dms.file',
            method: 'search_read',
            fields: _.union(args.file.fields || [], [
            	'permission_read', 'permission_create', 
            	'permission_write', 'permission_unlink',
            	'name', 'mimetype', 'directory', 'size',
            	'is_locked', 'is_lock_editor', 'extension', 
            	'actions', 'actions_multi', '__last_update', 
			]),
            domain: this._buildDomain(
            	[['directory', operator, value]],
            	args.file.domain
            ),
            context: args.file.context || session.user_context,
        }).then(function (records) {
        	var actions_ids = _.flatten(_.pluck(records, 'actions'));
        	var actions_multi_ids = _.flatten(_.pluck(records, 'actions_multi'));
            return this._rpc({
                model: 'muk_dms_actions.action',
                method: 'name_get',
                args: [_.union(actions_ids, actions_multi_ids)],
                context: session.user_context,
            }).then(function (names) {
                _.each(records, function (record) {
                	record.actions = _.map(record.actions, function (action) {
                		return _.find(names, function (name) {
                            return name[0] === action;
                        });
                	});
                	record.actions_multi = _.map(record.actions_multi, function (action) {
                		return _.find(names, function (name) {
                            return name[0] === action;
                        });
                	});
                });
                return records;
            });
        }.bind(this));
    },
    _loadFilesSingle: function(directory_id, args) {
    	return this._loadFiles('=', directory_id, args);
    },
    _loadFilesMulti: function(directory_ids, args) {
    	return this._loadFiles('in', directory_ids, args);
    },
    _searchDirectories: function(directory_id, value, args) {
    	return this._rpc({
			model: 'muk_dms.directory',
            method: 'name_search',
            kwargs: {
                name: value,
                limit: false,
                args: this._buildDomain(
                		[['parent_directory', 'child_of', directory_id]],
                		args.directory.domain
                ),
                operator: args.search.operator || "ilike",
                context: args.directory.context || session.user_context,
            },
        });
    },
    _searchFiles: function(directory_id, value, args) {
    	var result = $.Deferred();
    	this._rpc({
			model: 'muk_dms.directory',
            method: 'search',
            kwargs: {
            	args: [['parent_directory', 'child_of', directory_id]], 
            	context: args.directory.context || session.user_context,
            },
        }).then(function(ids) {
        	this._rpc({
                model: 'muk_dms.file',
                method: 'search_read',
        		fields: ['directory'],
                domain: this._buildDomain([
            		['directory', 'in', ids],
            		['name', args.search.operator || "ilike", value]
                ], args.file.domain),
            	context: args.directory.context || session.user_context,
            }).then(function(files) {
            	var directories = _.map(files, function(file) {
            		return "directory_" + file.directory[0];
            	});
            	result.resolve(directories);
            }); 
        }.bind(this));
    	return result;
    },
    _loadInitialData: function(args) {
    	var data_loaded = $.Deferred();
    	this._loadStorages(args).then(function(storages) {
        	var loading_data_parts = [];
    		_.each(storages, function(storage, index, storages) {
        		if(storage.count_storage_directories > 0) {
        			var directory_loaded = $.Deferred();
        			loading_data_parts.push(directory_loaded);
        			this._loadDirectoriesSingle(storage.id, args).then(function(directories) {
        				storages[index].directories = directories;
        				directory_loaded.resolve();
        			});
        		}
    		}.bind(this));
    		$.when.apply($, loading_data_parts).then(function() {
    			if(args.storage.show) {
	    			var result = _.chain(storages).map(function (storage) {
	    				var children = _.map(storage.directories, function (directory) {
    						return this._makeNodeDirectory(directory, args.file.show);
    					}.bind(this));
	    				return this._makeNodeStorage(storage, children);
	    			}.bind(this)).filter(function(node) {
						return node.children && node.children.length > 0;
					}.bind(this)).value();
	    			data_loaded.resolve(result);
    			} else {
    				var nodes = [];
    				_.each(storages, function(storage) {
    					_.each(storages.directories, function(directory) {
    						nodes.push(this._makeNodeDirectory(directory, args.file.show));
    					}.bind(this));
    				}.bind(this));
    				data_loaded.resolve(nodes);
    			}
    		}.bind(this));
    	}.bind(this));
        return data_loaded;
    },
    _loadNode: function(node, args) {
    	var result = $.Deferred();
    	if(node.data && node.data.odoo_model === "muk_dms.storage") {
    		this._loadDirectoriesSingle(node.data.odoo_id, args).then(function(directories) {
    			var directory_nodes = _.map(directories, function (directory) {
					return this._makeNodeDirectory(directory, args.file.show);
				}.bind(this));		
    			result.resolve(directory_nodes);
            }.bind(this));
    	} else if(node.data && node.data.odoo_model === "muk_dms.directory") {
    		var files_loaded = $.Deferred();
    		var directories_loaded = $.Deferred();
    		this._loadSubdirectoriesSingle(node.data.odoo_id, args).then(function(directories) {
    			var directory_nodes = _.map(directories, function (directory) {
					return this._makeNodeDirectory(directory, args.file.show);
				}.bind(this));		
            	directories_loaded.resolve(directory_nodes);
            }.bind(this));
    		if(args.file.show) {
    			this._loadFilesSingle(node.data.odoo_id, args).then(function(files) {
        			var file_nodes = _.map(files, function (file) {
						return this._makeNodeFile(file);
					}.bind(this));
    				files_loaded.resolve(file_nodes);
                }.bind(this));
    		} else {
    			files_loaded.resolve([]);
    		}
    		$.when(directories_loaded, files_loaded).then(function(directories, files) {
    			result.resolve(directories.concat(files));
    		});
    	} else {
    		result.resolve([]);
    	}
    	return result;
    },
    _loadNodes: function(nodes, args) {
    	var result = $.Deferred();
		var storages_loaded = $.Deferred();
		var directories_loaded = $.Deferred();
    	var storage_ids = _.chain(nodes).filter(function(node) {
    		return node.split("_")[0] === "storage";
    	}).map(function(node, i) { 
    		 return parseInt(node.split("_")[1]);
    	}).value();
    	var directory_ids = _.chain(nodes).filter(function(node) {
     		return node.split("_")[0] === "directory";
    	}).map(function(node, i) { 
    		 return parseInt(node.split("_")[1]);
    	}).value();
    	if(storage_ids.length > 0) {
    		this._loadDirectoriesMulti(storage_ids, args).then(function(directories) {
    			var directory_nodes = _.map(directories, function (directory) {
					return this._makeNodeDirectory(directory, args.file.show);
				}.bind(this));		
    			storages_loaded.resolve(directory_nodes);
            }.bind(this));
    	} else {
    		storages_loaded.resolve([]);
    	}
    	if(directory_ids.length > 0) {
    		var files_loaded = $.Deferred();
    		var subdirectories_loaded = $.Deferred();
    		this._loadSubdirectoriesMulti(directory_ids, args).then(function(directories) {
    			var directory_nodes = _.map(directories, function (directory) {
					return this._makeNodeDirectory(directory, args.file.show);
				}.bind(this));		
            	subdirectories_loaded.resolve(directory_nodes);
            }.bind(this));
    		if(args.file.show) {
    			this._loadFilesMulti(directory_ids, args).then(function(files) {
        			var file_nodes = _.map(files, function (file) {
						return this._makeNodeFile(file);
					}.bind(this));
    				files_loaded.resolve(file_nodes);
                }.bind(this));
    		} else {
    			files_loaded.resolve([]);
    		}
    		$.when(subdirectories_loaded, files_loaded).then(function(directories, files) {
    			directories_loaded.resolve((_.union(directories, files)));
    		});
    	} else {
    		directories_loaded.resolve([])
    	}
    	$.when(storages_loaded, directories_loaded).then(function(storages, directories) {
			var tree = _.groupBy(_.union(storages, directories), function(item) {
				return item.data.parent;
			});
			result.resolve(tree);
		});
    	return result;
    },
    _searchNodes: function(val, node, args) {
    	var result = $.Deferred();
		var files_loaded = $.Deferred();
    	var directories_loaded = $.Deferred();
    	this._searchDirectories(node.data.odoo_id, val, args).then(function(directories) {
    		var directories = _.map(directories, function (directory) {
    			return "directory_" + directory.id;
			}.bind(this));		
        	directories_loaded.resolve(directories);
        }.bind(this));
		if(args.directoriesOnly) {
			files_loaded.resolve([]);
		} else {
			this._searchFiles(node.data.odoo_id, val, args).then(function(files) {
				files_loaded.resolve(files);
            }.bind(this));
		}
		$.when(directories_loaded, files_loaded).then(function(directories, files) {
			result.resolve(_.union(directories, files));
		});
    	return result;
    },
    _makeNodeStorage: function(storage, children) {
		return {
			id: "storage_" + storage.id,
			text: storage.name,
			icon: "fa fa-database",
			type: "storage",
			data: {
				odoo_id: storage.id,
				odoo_model: "muk_dms.storage",
				odoo_record: storage,
			},
			children: children,
		};
    },
    _makeNodeDirectory: function(directory, showFiles) {
    	var directoryNode = {
			id: "directory_" + directory.id,
			text: directory.name,
			icon: "fa fa-folder-o",
			type: "directory",
			data: {
				odoo_id: directory.id,
				odoo_model: "muk_dms.directory",
				odoo_record: directory,
				name: directory.name,
				perm_read: directory.permission_read,
				perm_create: directory.permission_create,
				perm_write: directory.permission_write,
				perm_unlink: directory.permission_unlink,
				parent: directory.parent_directory ? "directory_" + directory.parent_directory[0] : "#",
				thumbnail_link: session.url('/web/image', {
		    		model: "muk_dms.directory",
		    		field: 'thumbnail_medium', 
		    		unique: directory.__last_update.replace(/[^0-9]/g, ''),
		    		id: directory.id, 
		    	}),
			},
		};
    	if(showFiles) {
    		directoryNode.children = (
    			directory.count_directories + 
    			directory.count_files
    		) > 0 ? true : false;
		} else {
			directoryNode.children = directory.count_directories > 0 ? true : false;
		}
    	return directoryNode;
    },
    _makeNodeFile: function(file) {
    	return {
			id: "file_" + file.id,
			text: file.name,
			icon: mimetype.mimetype2fa(file.mimetype, {prefix: "fa fa-"}),
			type: "file",
			data: {
				odoo_id: file.id,
				odoo_model: "muk_dms.file",
				odoo_record: file,
				name: file.name,
				filename: file.name,
				locked: file.is_locked,
				mimetype: file.mimetype,
				extension: file.extension,
				size: field_utils.format.binary_size(file.size),
				perm_read: file.permission_read,
				perm_create: file.permission_create && (!file.is_locked || file.is_lock_editor),
				perm_write: file.permission_write && (!file.is_locked || file.is_lock_editor),
				perm_unlink: file.permission_unlink && (!file.is_locked || file.is_lock_editor),
				parent: "directory_" + file.directory[0],
				actions_multi: file.actions_multi || [],
				actions: file.actions || [],
				thumbnail_link: session.url('/web/image', {
		    		model: "muk_dms.file",
		    		field: 'thumbnail_medium', 
		    		unique: file.__last_update.replace(/[^0-9]/g, ''),
		    		id: file.id, 
		    	}),
			},
		};
    },
});

return DocumentsModel;

});