horizon.addInitFunction(function () {
////////////////////////////////
//   Node Templates workflow //
///////////////////////////////

    function create_properties_tab(type) {
        var li_templ = "#create_node_template__set" + type;
        var li_text;
        if (type == "jt") {
            li_text = "Job Tracker properties";
        }
        if (type == "nn") {
            li_text = "Name Node properties";
        }
        if (type == "tt") {
            li_text = "Task Tracker properties";
        }
        if (type == "dn") {
            li_text = "Data Node properties";
        }
        var tab_html = "<li>" +
            "<a href='" + li_templ + "' data-toggle='tab' data-target='" + li_templ + "'>" +
            li_text +
            "</a></li>";

        $("#id_node_type").closest(".modal-body").find("ul").append(tab_html);

        create_tab_content(type);
    }

    function add_options_inputs(type, required, option) {
        last_template_idx += 1;
        var choice_input = '' +
            '<div class="control-group form-field clearfix">' +
            '<div class="' + type + '_opts" style="display:none"></div>';
        if (!required) {
            choice_input += '<span id="remove_template_input_' + last_template_idx + '" class="btn btn-inline pull-right remove-inputs">-</span>';
        }

        var header = "Option:";

        choice_input +=
            '<label for="id_option_' + last_template_idx + '">' + header + '</label>' +
                '<span class="help-block" style="display: none;"></span>';
                if (required) {
                    choice_input += '<span>' + option + '</span>' +
                        '<div class="input"> ' +
                            '<input type="text" class="opts-select" value = "' + option + '" style="display:none"/> ' +
                        '</div>';
                } else {
                    choice_input += '<div class="input">' +
                    '<select name="template_' + last_template_idx + '" id="id_option_'+ last_template_idx +'" class="opts-select">' +
                    $("#id_" + type + "_opts").html() +
                    '</select>' +
                    '</div>';

                }
        choice_input += '</div>';
        var value_input = '' +
            '<div class="control-group form-field clearfix">' +
            '<div class="' + type + '-opt-value" style="display:none"></div>' +
            '<label for="id_opt_' + last_template_idx + '">Value:</label>' +
            '<span class="help-block" style="display: none;"></span>'+
            '<div class="input">'+
            '<input type="text" class="opt-input" id="id_opt_' + last_template_idx + '" data-original-title=""/>'+
            '</div>'+
            '</div><hr/>';
        $("#create_node_template__set" + type).find(".actions").append(choice_input + value_input);
    }

    function add_required_opts(type) {
        $("#id_" + type + "_required_opts").find("option").each(function(idx, option) {
            add_options_inputs(type, true, $(option).text());
        });
    }

    function create_tab_content(type) {
        var tab_html = '<fieldset id="create_node_template__set' + type + '" class="js-tab-pane tab-pane">' +

        '<table class="table-fixed">' +
            '<tbody>' +
                '<tr>' +
                    '<td class="actions">'+
                    '</td>' +
                    '<td class="help_text">' +
                        '<p>Set properties for hadoop node</p>' +
                    '</td>' +
                '</tr>' +
            '</tbody>' +
        '</table>' +
        '<span id="add_option_inputs_btn_' + type + '" class="btn btn-inline">+</span>' +
        '</fieldset>' +
        '<noscript><hr /></noscript>';

        $("#id_node_type").closest(".tab-content").append(tab_html);

        add_required_opts(type);

        //$("#add_option_inputs_btn_" + type).unbind("click");
        $(document).off("click", "#add_option_inputs_btn_" + type);
            $(document).on("click", "#add_option_inputs_btn_" + type, function(evt) {
            add_options_inputs(type, false);
        });
    }


    function update_properties_tabs() {

        $("#id_node_type").closest(".modal-body").find("ul").find("li").each(function(index, element) {
            if (index > 0) {
                element.remove();
            }});
        $("#id_node_type").closest(".tab-content").find("fieldset").each(function(index, element) {
            if (index > 0) {
                element.remove();
            }});

        var val = $("#id_node_type").val();

        if (val.indexOf("JT") != -1) {
            create_properties_tab("jt")
        }
        if (val.indexOf("NN") != -1) {
            create_properties_tab("nn")
        }
        if (val.indexOf("TT") != -1) {
            create_properties_tab("tt")
        }
        if (val.indexOf("DN") != -1) {
            create_properties_tab("dn")
        }
    }


    $(document).on("change", "#id_node_type", function(evt) {
        update_properties_tabs()
    });


    function fillTemplateResultField() {
        var result = {};
        $(["jt", "nn", "tt", "dn"]).each(function (idx, type) {
            console.log("building json for " + type);
            result[type] = {};
            $("." + type + "_opts").each(function (_idx, option) {
                var opt = $(option).parent().find(".opts-select").val();
                var val = $(option).parent().next().find(".opt-input").val();
                console.log("seting option " + opt + ": " + val);
                result[type][opt] = val;
            });
        });
        console.log(JSON.stringify(result));
        return JSON.stringify(result);
    }



////////////////////////////////
// Cluster creation workflow  //
///////////////////////////////

    var last_template_idx = 0;
//

    function addValidationHint(text) {
        $($("#create_cluster__generalconfigurationaction").find("table")[0]).before('<div class="validation-hint"><span class="help-inline label label-important">' + text + '</span><br/><div>');
    }

    function validate() {
        $(".validation-hint").remove();

        var jt_count = 0;
        var nn_count = 0;
        var valid = true;
        $(".templates_select").each(function() {
            var selected = $(this).val().toLowerCase();
            if (selected.indexOf("jt") != -1) {
                jt_count += 1;
            }
            if (selected.indexOf("nn") != -1) {
                nn_count += 1;
            }
        });

        if (jt_count == 0) {
            addValidationHint("Job Tracker is required");
            valid = false;
        }
        if (jt_count > 1) {
            addValidationHint("Too many Job Trackers");
            valid = false;
        }

        if (nn_count == 0) {
            addValidationHint("Name Node is required");
            valid = false;
        }
        if (nn_count > 1) {
            addValidationHint("Too many Name Nodes");
            valid = false;
        }

        if (valid) {
            $("input[type=submit][value='Create & Launch']").prop("disabled", false);
        } else {
            $("input[type=submit][value='Create & Launch']").prop("disabled", true);
        }

        return valid;
    }

    function fillClusterResultField() {
        var result = {};
        $(".templates_select").each(function() {
            var template = $(this).val();
            var id = this.id;
            var block_num = id.replace("id_template_", "");
            var count = $("#id_count_" + block_num).val();
            if (result[template] == null) {
                result[template] = parseInt(count);
            } else {
                result[template] = result[template] + parseInt(count)
            }
        });
        return JSON.stringify(result);
    }

    function update_count_info(block_num, value) {
        $("#count_hint_" + block_num).text(value);
        var header = $("#header_" + block_num);
        if (header.closest(".well").hasClass("well worker_info")) {
            if (value == 1) {
                header.text("Worker Node")
            } else {
                header.text("Worker Nodes")
            }
        }
    }

    function update_info(block_num, value) {
        var info = template_infos[value];
        $("#" + block_num + "_info_content").text(info);
    }

    function create_info(type) {
        var info = '<div class="well ' + type + '_info" id="'+ last_template_idx +'_info"> ' +
            '<h4><span  id="header_' + last_template_idx + '">';
            if (type == "jt_nn") {
                info += "Job Tracker + Name Node"
            }
            if (type == "jt") {
                info += "Job Tracker"
            }
            if (type == "nn") {
                info += "Name Node"
            }
            if (type == "worker") {
                info += "Worker Nodes" + '</span> (<span id="count_hint_' + last_template_idx + '"></span>)'
            }
            info += '</h4><div id="' + last_template_idx +'_info_content">'+
            '</div>'+
            '<div>';
        if (type != "worker") {
            $("#infos").prepend(info)
        } else {
            $(".well").last().after(info);
        }
    }

    function create_inputs(type) {
        last_template_idx += 1;

        var choice_input = '' +
            '<div class="control-group form-field clearfix">' +
                '<div class="' + type + '" style="display:none"></div>';
            if (type == 'worker') {
                choice_input += '<span id="remove_template_input_' + last_template_idx + '" data-add-to-field="id_keypair" class="btn btn-inline pull-right remove-inputs">-</span>'
            }
        var header;
        if (type == "jt_nn") {
            header = "Job Tracker + Name Node node template";
        }
        if (type == "jt") {
            header = "Job Tracker node template";
        }
        if (type == "nn") {
            header = "Name Node node template";
        }
        if (type == "worker") {
            header = "Worker node template";
        }
        choice_input +=
                '<label for="id_template_' + last_template_idx + '">' + header + '</label>' +
                '<span class="help-block" style="display: none;"></span>' +
                '<div class="input">' +
                    '<select name="template_' + last_template_idx + '" id="id_template_'+ last_template_idx +'" class="templates_select">' +
                        $("#id_" + type + "_template_choices").html() +
                    '</select>' +
                '</div>' +
            '</div>';
        var count_input = '' +
            '<div class="control-group form-field clearfix">' +
                '<div class="' + type + '" style="display:none"></div>' +
                '<label for="id_count_' + last_template_idx + '">Nodes number</label>' +
                '<span class="help-block" style="display: none;"></span>'+
                '<div class="input">'+
                    '<input type="text" class="count-input" name="count_' + last_template_idx + '" value="1" id="id_count_' + last_template_idx + '" data-original-title="">'+
                '</div>'+
            '</div>';
        if (type != "worker") {
            $("#id_hadoop_cluster_topology").closest(".control-group").after(choice_input + count_input);
        } else {
            $("#id_result_field").closest(".control-group").before(choice_input + count_input + "<hr>");
        }
        create_info(type);
        $("#id_template_" + last_template_idx).change();
        $("#count_hint_" + last_template_idx).change();
    }

    function switch_topology() {
        $(".jt_nn").closest(".control-group").remove();
        $(".jt").closest(".control-group").remove();
        $(".nn").closest(".control-group").remove();

        $(".jt_nn_info").remove();
        $(".jt_info").remove();
        $(".nn_info").remove();

        var topology_type = $("#id_hadoop_cluster_topology").val();
        if (topology_type == "Single-node master")  {
            create_inputs("jt_nn");
        } else {
            create_inputs("nn");
            create_inputs("jt");
        }
    }

    $(document).on('change', '.templates_select', function() {
        var id = this.id;
        var block_num = id.replace("id_template_", "");
        var selected = $(this).val().toLowerCase();
        update_info(block_num, selected);
        var count_selector = $("#id_count_" + block_num);
        if (selected.indexOf("jt") != -1 || selected.indexOf("nn") != -1) {
            count_selector.val(1);
            count_selector.closest('.control-group').hide();
        } else {
            count_selector.closest('.control-group').show();
        }

        validate();
    });


    $(document).on('click', '#add_template_inputs_btn', function(evt) {
        create_inputs("worker");
        $(".count-input").keyup();
    });

    $(document).on('change', '#id_hadoop_cluster_topology', function(evt){
        switch_topology();
        $(".count-input").keyup();
    });

    $(document).on('keyup', '.count-input', function(evt){
        var id = this.id;
        var block_num = id.replace("id_count_", "");
        var value = $(this).val();
        update_count_info(block_num, value);
    });

    $(document).on('click','.remove-inputs', function(evt) {
        var id = this.id;
        var block_num = id.replace("remove_template_input_", "");
        $("#id_template_" + block_num).closest(".control-group").remove();
        $("#id_count_" + block_num).closest(".control-group").next().remove(); //hr
        $("#id_count_" + block_num).closest(".control-group").remove();
        $("#" + block_num + "_info").remove();


        $("#id_option_" + block_num).closest(".control-group").remove();
        $("#id_opt_" + block_num).closest(".control-group").next().remove(); //hr
        $("#id_opt_" + block_num).closest(".control-group").remove();
        validate();
    });


    horizon.modals.addModalInitFunction(function (modal) {
        last_template_idx = 0;

        //node templates workflow
        $("#id_node_type").change();
        $("#id_jt_opts").closest(".control-group").hide();
        $("#id_nn_opts").closest(".control-group").hide();
        $("#id_tt_opts").closest(".control-group").hide();
        $("#id_dn_opts").closest(".control-group").hide();

        $("#id_jt_required_opts").closest(".control-group").hide();
        $("#id_nn_required_opts").closest(".control-group").hide();
        $("#id_tt_required_opts").closest(".control-group").hide();
        $("#id_dn_required_opts").closest(".control-group").hide();

        //clusters workflow
        $("input[type=submit][value='Create & Launch']").bind('click', function() {
            var result = fillClusterResultField();
            $("#id_result_field").val(result);
        });
        $("input[type=submit][value='Create']").bind('click', function() {
            var result = fillTemplateResultField();
            $("#id_template_result_field").val(result);
        });
        $($("#create_cluster__generalconfigurationaction").find("table")[0]).after(
            '<span id="add_template_inputs_btn" class="btn btn-inline">+</span>');

        $("#id_jt_nn_template_choices").closest(".control-group").hide();
        $("#id_jt_template_choices").closest(".control-group").hide();
        $("#id_nn_template_choices").closest(".control-group").hide();
        $("#id_worker_template_choices").closest(".control-group").hide();
        $("#id_result_field").closest(".control-group").hide();
        $("#id_template_result_field").closest(".control-group").hide();

        switch_topology();
        create_inputs("worker");
        $(".count-input").keyup();
    })


});