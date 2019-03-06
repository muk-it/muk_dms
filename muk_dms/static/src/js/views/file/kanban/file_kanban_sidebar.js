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

odoo.define('muk_dms.FileSidebar', function (require) {
"use strict";

var core = require('web.core');

var Widget = require('web.Widget');

var _t = core._t;
var QWeb = core.qweb;


var FileSidebar = Widget.extend({
    template: 'muk_dms.FileSiebar',
    events: {
    	'click .mk_file_kanban_sidebar_header a': '_onSectionClick',
    	'click #mk_file_kanban_sidebar_starred li': '_onDirectoryClick',
    	'click #mk_file_kanban_sidebar_directories li': '_onDirectoryClick',
    	'click #mk_file_kanban_sidebar_directories i': '_onDirectoryToggle',
    	'change #mk_file_kanban_sidebar_categories input': '_onCategorySearchChange',
    	'change #mk_file_kanban_sidebar_tags input': '_onTagSearchChange',
    },
    init: function (parent, state) {
    	this._super.apply(this, arguments);
        this.starred = state.starred || [];
        this.directories = state.directories || [];
        this.categories = state.categories || [];
        this.tags = state.tags || [];
        this.activeCategories = [];
        this.activeTags = [];
    },
    start: function () {
        this.$starred = this.$('#mk_file_kanban_sidebar_starred');
    	this.$directories = this.$('#mk_file_kanban_sidebar_directories');
        this.$categories = this.$('#mk_file_kanban_sidebar_categories');
        this.$tags = this.$('#mk_file_kanban_sidebar_tags');
    	return $.when(this._render(), this._super.apply(this, arguments));
    },
    updateState: function (state) {
        this.categories = state.categories || [];
        this.tags = state.tags || [];
        this._renderCategoryList();
    	this._renderTagList();
    },
    _render: function () {
    	this.$('.mk_file_kanban_sidebar_list').renderScrollBar();
    	this._renderStarredList();
    	this._renderDirectoryTree();
    	this._renderCategoryList();
    	this._renderTagList();
    },
    _renderStarredList: function () {
    	var starred = $(QWeb.render('muk_dms.FileSiebarStarred', {
			starred: this.starred,
		}));
        this.$starred.find('.mk_file_kanban_sidebar_list').html(starred);
    },
    _renderDirectoryTree: function () {
    	var directories = $(QWeb.render('muk_dms.FileSiebarDirectories', {
    		directories: this.directories,
		}));
        this.$directories.find('.mk_file_kanban_sidebar_list').html(directories);
    },
    _renderCategoryList: function () {
    	console.log(this.categories);
    	var categories = $(QWeb.render('muk_dms.FileSiebarCategories', {
    		categories: this.categories,
		}));
        this.$categories.find('.mk_file_kanban_sidebar_list').html(categories);
    	this.$categories.find('.mk_file_kanban_sidebar_filter').remove();
        if(this.activeCategories && !_.isEmpty(this.activeCategories)) {
        	this.$categories.find('.mk_file_kanban_sidebar_header a').append(
        		$('<i/>', {class: "mk_file_kanban_sidebar_filter fa fa-filter"})
        	);
        	_.each(this.activeCategories, function(id) {
        		this.$categories.find('li[data-id=' + id + '] input').prop("checked", true);
        	}.bind(this));
        }
    },
    _renderTagList: function () {
    	var tags = $(QWeb.render('muk_dms.FileSiebarTags', {
			tags: this.tags,
		}));
        this.$tags.find('.mk_file_kanban_sidebar_list').html(tags);
    	this.$tags.find('.mk_file_kanban_sidebar_filter').remove();
        if(this.activeTags && !_.isEmpty(this.activeTags)) {
        	this.$tags.find('.mk_file_kanban_sidebar_header a').append(
        		$('<i/>', {class: "mk_file_kanban_sidebar_filter fa fa-filter"})
        	);
        	_.each(this.activeTags, function(id) {
        		this.$tags.find('li[data-id=' + id + '] input').prop("checked", true);
        	}.bind(this));
        }
    },
    _onSectionClick: function (event) {
    	this.$('.mk_file_kanban_sidebar_section').removeClass("show");
        this.$($(event.currentTarget).attr("href")).addClass("show");
        event.stopPropagation();
        event.preventDefault();
    },
    _onDirectoryClick: function(event) {
    	var $item = $(event.currentTarget);
    	var active = $item.hasClass("active");
    	this.$starred.find('.active').removeClass("active");
    	this.$directories.find('.active').removeClass("active");
    	if (active) {
        	this.trigger_up('directory_selected', {
        		directory: false,
        	});
    	} else {
        	this.trigger_up('directory_selected', {
        		directory: $item.data('id'),
        	});
        	$item.addClass("active");
    	} 
    	
    },
    _onDirectoryToggle: function(event) {
        var $target = $(ev.currentTarget);
        if (!$target.hasClass('o_foldable')) {
            $target = $target.closest('.o_foldable');
        }
        var folded = !$target.find('.list-group:first').hasClass('o_folded');
        var id = $target.data('id');
        if ($target.hasClass('o_documents_selector_folder')) {
            this.openedFolders[id] = !folded;
        } else if ($target.hasClass('o_documents_selector_facet')) {
            this.foldedFacets[id] = folded;
        }
        this._updateFoldableElements();
    	event.stopPropagation();
    	event.preventDefault(); 
    },
    _onCategorySearchChange: function(event) {
    	var $checkbox = $(event.currentTarget);
    	var checked = $checkbox.prop("checked");
    	var category = $checkbox.closest('li').data('id');
    	if (!checked) {
    		this.activeCategories = _.without(this.activeCategories, category);
    	} else {
    		this.activeCategories.push(category);
    	}
    	this.trigger_up('search_changed', {
    		activeCategories: this.activeCategories,
    		activeTags: this.activeTags,
    	});
    },
    _onTagSearchChange: function(event) {
    	var $checkbox = $(event.currentTarget);
    	var checked = $checkbox.prop("checked");
    	var tag = $checkbox.closest('li').data('id');
    	if (!checked) {
    		this.activeTags = _.without(this.activeTags, tag);
    	} else {
    		this.activeTags.push(tag);
    	}
    	this.trigger_up('search_changed', {
    		activeCategories: this.activeCategories,
    		activeTags: this.activeTags,
    	});
    },
});

return FileSidebar;

});