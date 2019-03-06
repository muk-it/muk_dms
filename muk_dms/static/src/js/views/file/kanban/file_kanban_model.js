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

odoo.define('muk_dms.FileKanbanModel', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var Domain = require('web.Domain');
var KanbanModel = require('web.KanbanModel');

var _t = core._t;
var QWeb = core.qweb;

var FileKanbanModel = KanbanModel.extend({
	get: function (dataPointID) {
        var result = this._super.apply(this, arguments);
        if (result && result.type === 'list') {
            _.extend(result, _.pick(this.localData[dataPointID],
            	'directories', 'starred', 'categories', 'tags',
            ));
        }
        return result;
    },
	load: function (params) {
        return this._super.apply(this, arguments).then(function (dataPointID) {
        	return this._fetchSidebarData(params, dataPointID).then(function () {
                return dataPointID;
        	});
        }.bind(this));
    },
    reload: function (id, options) {
        var dataPoint = this.localData[id];
        if (dataPoint.isRootPoint) {
        	if (options && options.selectedDirectory) {
            	options.domain = options.domain || [];
        		options.domain = this._updateDirectoryDomain(options);
        		options.domain = this._updateSidebarDomainDomain(options);
        	} else {
        		options.domain = options.domain || [];
        		options.domain = this._updateSidebarDomainDomain(options);
        	}
        	return this._super.apply(this, arguments).then(function (dataPointID) {
        		if (options.directoryChanged) {
        			return this._reloadSidebarData(dataPointID).then(function () {
                        return dataPointID;
                	});
        		} else {
        			return dataPointID;
        		}
            }.bind(this));
        	
        } else {
        	return this._super.apply(this, arguments);
        }
    },
    _updateDirectoryDomain: function (options) {
    	var directory = options.selectedDirectory;
    	var domain = _.filter(options.domain, function(arg) {
    		return (!(_.isArray(arg)) || arg[0] !== "directory");
    	});
    	var updatedDomain = new Domain([['directory', '=', directory]]);
    	updatedDomain._addSubdomain(domain || []);
    	return updatedDomain.toArray();
    },
    _updateSidebarDomainDomain: function (options) {
    	if (!options.directoryChanged && !_.isEmpty(options.sidebarDomain)) {
    		var updatedDomain = new Domain(options.sidebarDomain);
    		updatedDomain._addSubdomain(options.domain);
    		return updatedDomain.toArray();
    	} else {
    		return options.domain;
    	}
    },
    _convertContext: function (context) {
    	var extraFetchParams = {};
    	if (context && context.active_id) {
    		if (context.active_model === "muk_dms.directory") {
    			extraFetchParams.directory = context.active_id;
    		} else if (context.active_model === "muk_dms.storage") {
    			extraFetchParams.storage = context.active_id;
    		}
        }
    	return extraFetchParams;
    },
    _fetchSidebarData: function (params, dataPointID) {
    	var dataPoint = this.localData[dataPointID];
    	var args = this._convertContext(params.context);
    	var defs = [
			this._fetchDirectories(args),
			this._fetchStarredDirectories(args),
			this._fetchCategories(dataPoint.res_ids),
			this._fetchTags(dataPoint.res_ids),
		];
    	return $.when.apply($, defs).then(function () {
    		return _.extend(dataPoint, {
    			search: params.domain || [],
    			directories: arguments[0],
    			starred: arguments[1],
    			categories: arguments[2],
    			tags: arguments[3],
    			isRootPoint: true,
    		});
    	});
    },
    _reloadSidebarData: function (dataPointID) {
    	var dataPoint = this.localData[dataPointID];
    	var defs = [
			this._fetchCategories(dataPoint.res_ids),
			this._fetchTags(dataPoint.res_ids),
		];
    	return $.when.apply($, defs).then(function () {
    		return _.extend(dataPoint, {
    			categories: arguments[0],
    			tags: arguments[1],
    		});
    	});
    },
    _fetchDirectories: function (args) {
        var domain = [];
    	if (args.storage) {
    		domain.push(['storage', '=', args.storage]);
    	}
    	if (args.directory) {
    		return this._rpc({
                model: 'muk_dms.directory',
                method: 'search_read_childs',
                kwargs: {
                	fields: [
    		    		'name',
    		    		'count_directories',
                	],
                	domain: domain,
                	parent_id: args.directory,
                },
            }).then(function (directories) {
            	return directories;
            });
    	} else {
    		return this._rpc({
                model: 'muk_dms.directory',
                method: 'search_read_parents',
                kwargs: {
                	fields: [
    		    		'name',
    		    		'count_directories',
                	],
                	domain: domain,
                },
            }).then(function (directories) {
            	return directories;
            });
    	}
    },
    _fetchStarredDirectories: function (args) {
    	var domain = [['starred', '=', true]];
     	if (args.storage) {
     		domain.push(['storage', '=', args.storage]);
     	}
     	if (args.directory) {
     		domain.push(['parent_directory', 'child_of', args.directory]);
     	}
        return this._rpc({
            model: 'muk_dms.directory',
            method: 'search_read',
            domain: domain,
            fields: ['name'],
        }).then(function (directories) {
            return directories;
        });
    },
    _fetchCategories: function (file_ids) {
        return this._rpc({
            model: 'muk_dms.category',
            method: 'search_read',
            fields: ['name',],
            domain: [['files', 'in', file_ids]],
        }).then(function (categories) {
        	return categories;
        }.bind(this));
    },
    _fetchTags: function (file_ids) {
        return this._rpc({
            model: 'muk_dms.tag',
            method: 'search_read',
            fields: ['name', 'color'],
            domain: [['files', 'in', file_ids]],
        }).then(function (tags) {
            return tags;
        });
    },
});

return FileKanbanModel;

});
