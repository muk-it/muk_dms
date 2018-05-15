
openerp.muk_dms = function (instance) {


 
var Widget = instance.Widget;
var Dialog = instance.web.Dialog;
var Model = instance.web.Model;

openerp.med_dms_preview_file_PreviewHelper(instance);
var PreviewHelper =  new instance.web.PreviewHelper();




var FormView = instance.web.FormView;
var ListView = instance.web.ListView;
var KanbanView = instance.web_kanban.KanbanView;





var _t = instance.web._t,
   _lt = instance.web._lt;
var QWeb = instance.web.qweb;


var Directories =new instance.web.Model("muk_dms.directory");
var Files =new instance.web.Model("muk_dms.file");





var open = function(self, model, id) {
    self.do_action({
        type: 'ir.actions.act_window',
        res_model: model,
        res_id: id,
        views: [[false, 'form']],
        target: 'current',
        context: self.session.user_context,
    });
}

var edit = function(self, model, id) {
    self.do_action({
        type: 'ir.actions.act_window',
        res_model: model,
        res_id: id,
        views: [[false, 'form']],
        target: 'current',
        flags: {'initial_mode': 'edit'},
        context: self.session.user_context,
    });
}

var create = function(self, model, parent) {
    var context = {};
    if(model == "muk_dms.file") {
        context = $.extend(self.session.user_context, {
            default_directory: parent
        });
    } else if(model == "muk_dms.directory") {
        context = $.extend(self.session.user_context, {
            default_parent_directory: parent
        });
    }
    self.do_action({
        type: 'ir.actions.act_window',
        res_model: model,
        views: [[false, 'form']],
        target: 'current',
        context: context,
    });
}

var context_menu_items = function(node, cp) {
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
                var obj = inst.get_node(data.reference);
                open(inst.settings.widget, obj.data.odoo_model, obj.data.odoo_id);
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
                var obj = inst.get_node(data.reference);
                edit(inst.settings.widget, obj.data.odoo_model, obj.data.odoo_id);
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
                var obj = inst.get_node(data.reference);
                $.ajax({
                    url: obj.data.download_link,
                    type: "GET",
                    dataType: "binary",
                    processData: false,
                    beforeSend: function(xhr, settings) {
                        // framework.blockUI();
                        instance.web.blockUI();
                    },
                    success: function(data, status, xhr){
                        saveAs(data, obj.data.filename);
                    },
                    error:function(xhr, status, text) {
                        self.do_warn(_t("Download..."), _t("An error occurred during download!"));
                    },
                    complete: function(xhr, status) {
                        // framework.unblockUI();
                        instance.web.blockUI();
                    },
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
                        var obj = inst.get_node(data.reference);
                        create(inst.settings.widget, "muk_dms.directory", obj.data.odoo_id);
                    }
                },
                file : {
                    separator_before: false,
                    separator_after: false,
                    label: _t("File"),
                    icon: "fa fa-file",
                    action: function(data) {
                        var inst = $.jstree.reference(data.reference);
                        var obj = inst.get_node(data.reference);
                        create(inst.settings.widget, "muk_dms.file", obj.data.odoo_id);
                    }
                },
            }
        };
    }
    return items;
}


instance.muk_dms.DocumentTreeView = Widget.extend({

    template: 'DMSTreeView',
    events: {
        "click button.refresh": "refresh",
        "click button.show_preview": "show_preview",
        "click button.hide_preview": "hide_preview",
        "click button.open": "open",
        "click button.edit": "edit",
        "click button.create_file": "create_file",
        "click button.create_directory": "create_directory",
    },
    init: function(parent) {
        this._super(parent);
        this.name = 'Documents';
        this.splitter = false;

    },
    start: function () {
        this.$('[data-toggle="tooltip"]').tooltip();
        this.load_view();
    },
    refresh: function() {
        var self = this;
        $.when(self.load_directories(self)).done(function (directories, directory_ids) {
            $.when(self.load_files(self, directory_ids)).done(function (files) {
                var data = directories.concat(files);
                self.$el.find('.oe_document_tree').jstree(true).settings.core.data = data;
                self.$el.find('.oe_document_tree').jstree(true).refresh();
            });
        });
    },
    show_preview: function(ev) {
        this.show_preview_active = true;
        if(!this.$el.find('.show_preview').hasClass("active")) {
            this.$el.find('.show_preview').addClass("active");
            this.$el.find('.hide_preview').removeClass("active");
            this.$el.find('.oe_document_col_preview').show();
            this.splitter = this.$el.find('.oe_document_row').split({
                orientation: 'vertical',
                limit: 100,
                position: '60%'
            });
        }
    },
    hide_preview: function(ev) {
        this.show_preview_active = false;
        if(!this.$el.find('.hide_preview').hasClass("active")) {
            this.$el.find('.hide_preview').addClass("active");
            this.$el.find('.show_preview').removeClass("active");
            this.$el.find('.oe_document_col_preview').hide();
            this.$el.find('.oe_document_col_tree').width('100%');
            if(this.splitter) {
                this.splitter.destroy();
            }
            this.splitter = false;
        }
    },
    load_directories: function(self) {
        var directories_query = $.Deferred();   


        //self.model_bank_statement_line.call("get_move_lines_for_reconciliation_by_statement_line_id",
        // [self.st_line.id, excluded_ids, self.filter, offset, limit], {context:self.session.user_context})
        //var Directories = new Model('muk_dms.directory', session.user_context);
        Directories.query(['name', 'parent_directory', 'perm_read', 'perm_create',
                           'perm_write', 'perm_unlink']).all().then(function(directories) {
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
            directories_query.resolve(data, directory_ids);
        });
        return directories_query;
    },
    add_container_directory: function(self, directory_id, directory_name) {
        return {
            id: "directory_" + directory_id,
            parent: "#",
            text: directory_name,
            icon: "fa fa-folder-o",
            type: "directory",
            data: {
                container: true,
                odoo_id: directory_id,
                odoo_parent_directory: false,
                odoo_model: "muk_dms.directory",
                perm_read: false,
                perm_create: false,
                perm_write: false,
                perm_unlink: false,
            }
        };
    },
    load_files: function(self, directory_ids) {
        var files_query = $.Deferred();
        Files.query(['name', 'mimetype', 'extension', 'directory',
                     'size', 'perm_read','perm_create', 'perm_write',
                     'perm_unlink']).all().then(function(files) {
            var data = [];
            _.each(files, function(value, key, list) {
                if(!($.inArray(value.directory[0], directory_ids) !== -1)) {
                    directory_ids.push(value.directory[0]);
                    data.push(self.add_container_directory(self, value.directory[0], value.directory[1]));
                }
                data.push({
                    id: "file," + value.id,
                    parent: "directory_" + value.directory[0],
                    text: value.name,
                    icon: mimetype2fa(value.mimetype, {prefix: "fa fa-"}),
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
            files_query.resolve(data);
        });
        return files_query;
    },
    load_view: function() {
        var self = this;
        $.when(self.load_directories(self)).done(function (directories, directory_ids) {
            $.when(self.load_files(self, directory_ids)).done(function (files) {
                var data = directories.concat(files);
                self.$el.find('.oe_document_tree').jstree({
                    'widget': self,
                    'core': {
                        'animation': 0,
                        'multiple': false,
                        'check_callback': true,
                        'themes': { "stripes": true },
                        'data': data
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
                        items: context_menu_items
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
                        self.$el.find('button.open').prop('disabled', !self.selected_node.data.perm_read);
                        self.$el.find('button.edit').prop('disabled', !self.selected_node.data.perm_write);
                        self.$el.find('button.create_file').prop('disabled',
                                self.selected_node.data.odoo_model != "muk_dms.directory" || !self.selected_node.data.perm_create);
                        self.$el.find('button.create_directory').prop('disabled',
                                self.selected_node.data.odoo_model != "muk_dms.directory" || !self.selected_node.data.perm_create);
                        $("#menuContinenti").prop('disabled', function (_, val) { return ! val; });
                        if(self.show_preview_active && data.node.data.odoo_model == "muk_dms.file") {
                            
                            PreviewHelper.createFilePreviewContent(data.node.data.odoo_id)
                            .then(function($content) {
                                self.$el.find('.oe_document_preview').html($content);
                            });             
                        }
                    }
                });
                var timeout = false;
                self.$el.find('#tree_search').keyup(function() {
                    if(timeout) {
                        clearTimeout(timeout); 
                    }
                    timeout = setTimeout(function() {
                        var v = self.$el.find('#tree_search').val();
                        self.$('.oe_document_tree').jstree(true).search(v);
                    }, 250);
               });
            });
        });
    },
    open: function() {
        if(this.selected_node) {
            open(this, this.selected_node.data.odoo_model, this.selected_node.data.odoo_id);
        }
    },
    edit: function() {
        if(this.selected_node) {
            edit(this, this.selected_node.data.odoo_model, this.selected_node.data.odoo_id);
        }
    },
    create_file: function() {
        if(this.selected_node) {
            if(this.selected_node.data.odoo_model == "muk_dms.directory") {
                create(this, "muk_dms.file", this.selected_node.data.odoo_id);
            } else {
                create(this, "muk_dms.file", this.selected_node.data.odoo_id);
            }
        }
    },
    create_directory: function() {
        if(this.selected_node) {
            if(this.selected_node.data.odoo_model == "muk_dms.directory") {
                create(this, "muk_dms.directory", this.selected_node.data.odoo_parent_directory);
            } else {
                create(this, "muk_dms.file", this.selected_node.data.odoo_parent_directory);
            }
        }
    }



});
instance.web.client_actions.add('med_dms_views.documents', 'iinstance.muk_dms.DocumentTreeView');




//---------------------


$.fn.textWidth = function(text, font) {
    if (!$.fn.textWidth.fakeEl) $.fn.textWidth.fakeEl = $('<span>').hide().appendTo(document.body);
    $.fn.textWidth.fakeEl.text(text || this.val() || this.text()).css('font', font || this.css('font'));
    return $.fn.textWidth.fakeEl.width();
};



instance.web.form.widgets.add('dms_path','instance.web.PathFormWidget');
instance.web.PathFormWidget = instance.web.form.FieldChar.extend({
    render_value: function() {
        if (this.$input) {
            this._super();
        } else {
            var show_value = this.format_value(this.get('value'), '');
            var max_width = this.options.width || 500;
            var text_witdh = $.fn.textWidth(show_value);
            if(text_witdh >= max_width) {
                var ratio_start = (1 - (max_width / text_witdh)) * show_value.length;
                show_value = ".." +  show_value.substring(ratio_start, show_value.length);
            }

            this.$el.text(show_value);
        }
    },
});




instance.web.form.widgets.add('dms_relpath', 'instance.web.RelationalPathFormWidget');
instance.web.RelationalPathFormWidget = instance.web.form.FieldText.extend({

    template: 'FieldRelationalPath',
    events : {
        'click a' : 'node_clicked',
    },
    render_value: function() {
        var self = this;
        var value = this.get('value');
        if (this.get("effective_readonly")) {
            var path = JSON.parse(value || "[]");
            var max_width = this.options.width || 500;
            var text = "";
            this.$el.empty();
            $.each(_.clone(path).reverse(), function(index, element) {
                text += element.name + "/";
                if($.fn.textWidth(text) >= max_width) {
                    self.$el.prepend($('<span/>').text(".."));
                } else {
                    if (index == 0) {
                        if(element.model == 'muk_dms.directory') {
                            self.$el.prepend($('<span/>').text(self.options.seperator || "/"));
                        }
                        self.$el.prepend($('<span/>').text(element.name));
                        self.$el.prepend($('<span/>').text(self.options.seperator || "/"));
                    } else {
                        var node = $('<a/>');
                        node.addClass("oe_form_uri");
                        node.data('model', element.model);
                        node.data('id', element.id);
                        node.attr('href', "javascript:void(0);");
                        node.text(element.name);
                        self.$el.prepend(node);
                        self.$el.prepend($('<span/>').text(self.options.seperator || "/"));
                    }
                }
                return ($.fn.textWidth(text) < max_width);
            });
        } else {
            this._super();
        }
    },
    node_clicked : function(event) {
        this.do_action({
            type : 'ir.actions.act_window',
            res_model : $(event.currentTarget).data('model'),
            res_id : $(event.currentTarget).data('id'),
            views : [[ false, 'form' ]],
            target : 'current',
            context : {},
        });
    }
});



FormView.include({
    load_record: function(record) {
        this._super.apply(this, arguments);
        if (this.$buttons && this.model === "muk_dms.file") {
            if(!this.datarecord.perm_create) {
                this.$buttons.find('.o_form_button_create').hide();
            }
            if(!this.datarecord.perm_write) {
                this.$buttons.find('.o_form_button_edit').hide();
            }
            if(!this.datarecord.editor &&
                    this.datarecord.locked &&
                    this.datarecord.locked instanceof Array) {
                var $edit = this.$buttons.find('.o_form_button_edit');
                $edit.prop("disabled", true);
                $edit.text(_t("Locked!"));
            }
        }
    }
});

ListView.include({
    compute_decoration_classnames: function (record) {
        var classnames = this._super.apply(this, arguments);
        if(this.model === "muk_dms.file" && 
                record.attributes.locked && 
                record.attributes.locked instanceof Array) {
            classnames = $.grep([classnames, "locked"], Boolean).join(" ");
        }
        if(this.model === "muk_dms.file" && 
                !record.attributes.perm_unlink) {
            classnames = $.grep([classnames, "no_unlink"], Boolean).join(" ");
        }
        return classnames;
    }
});




openerp.web_kanban.KanbanRecord.include({
        start: function() {
            var self = this;
            this._super.apply(this, arguments);
            if (this.view.dataset.model === 'muk_dms.file') {
                   
                this.$(".muk_image").click(function(e) {
                    e.stopPropagation();
                     PreviewHelper.createFilePreviewDialog($(e.currentTarget).data('id'), self);
                });
                this.$(".muk_filename").click(function(e) {
                    e.stopPropagation();
                    self.do_action_open();
                });
            } 
        },
    });


function format_size(bytes, si) {
    var thresh = si ? 1000 : 1024;
    if(Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }
    var units = si
        ? ['kB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var u = -1;
    do {
        bytes /= thresh;
        ++u;
    } while(Math.abs(bytes) >= thresh && u < units.length - 1);
    return bytes.toFixed(1) + ' ' + units[u];
}


instance.web.form.widgets.add('dms_size','instance.web.SizeFormWidget');

instance.web.SizeFormWidget = instance.web.form.FieldFloat.extend({
    render_value: function() {
        var show_value = this.format_value(this.get('value'), '');
        if (this.$input) {
            this._super();
        } else {
            this.$el.text(format_size(show_value, this.options.si));
        }
    },
});
instance.web.form.widgets.add('field.dms_size','instance.web.SizeColumnWidget');

instance.web.SizeColumnWidget = instance.web.list.Column.extend({
    _format: function (row_data, options) {
        var value = row_data[this.id].value;
        return format_size(value, false);
    }
});




}

