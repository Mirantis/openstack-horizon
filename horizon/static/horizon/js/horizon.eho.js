horizon.addInitFunction(function () {
////////////////////////////////
//   Node Templates workflow //
///////////////////////////////
    function update_process_properties_fields(field) {
        var $this = $(field),
            desired_field = $this.val().toLowerCase();
        var fields = desired_field.split("+");

        $("input").filter(function() {
            var _id = this.id;
            var matches = false;
            $(["jt", "nn", "tt", "dn"]).each(function() {
                if (_id.indexOf("id_" + this) == 0) {
                    matches = true;
                }
            });
            return matches;
        }).each(function() {
                $(this).closest(".control-group").hide();
            });

        $("input").filter(function() {
           var _id = this.id;
           var matches = false;
           $(fields).each(function() {
               if (_id.indexOf("id_" + this) == 0) {
                   matches = true;
               }
           });
           return matches;
       }).each(function() {
              $(this).closest(".control-group").show();
           });
    }

    $(document).on('change', '.workflow #id_node_type', function (evt) {
        update_process_properties_fields(this)
    });

    $('.workflow #id_node_type').change();

    horizon.modals.addModalInitFunction(function (modal) {
        $(modal).find("#id_node_type").change();
    });

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

    function fillResultField() {
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
        console.log(block_num, value);
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
        $("#id_count_" + block_num).closest(".control-group").next().remove();
        $("#id_count_" + block_num).closest(".control-group").remove();
        $("#" + block_num + "_info").remove();
        validate();
    });


    horizon.modals.addModalInitFunction(function (modal) {
        last_template_idx = 0;

        $("input[type=submit][value='Create & Launch']").bind('click', function() {
            var result = fillResultField();
            $("#id_result_field").val(result);
        });
        $($("#create_cluster__generalconfigurationaction").find("table")[0]).after(
            '<span id="add_template_inputs_btn" data-add-to-field="id_keypair" class="btn btn-inline">+</span>');

        $("#id_jt_nn_template_choices").closest(".control-group").hide();
        $("#id_jt_template_choices").closest(".control-group").hide();
        $("#id_nn_template_choices").closest(".control-group").hide();
        $("#id_worker_template_choices").closest(".control-group").hide();
        $("#id_result_field").closest(".control-group").hide();

        switch_topology();
        create_inputs("worker");
        $(".count-input").keyup();
    })


});