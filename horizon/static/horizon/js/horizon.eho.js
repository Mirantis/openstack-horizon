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
        $($("#create_cluster__selectnodetemplatesaction").find("table")[0]).before('<div class="validation-hint"><span class="help-inline label label-important">' + text + '</span><br/><div>');
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

    function create_inputs() {
        last_template_idx += 1;

        var choice_input = '' +
            '<div class="control-group form-field clearfix">' +
            '<span id="remove_template_input_' + last_template_idx + '" data-add-to-field="id_keypair" class="btn btn-inline pull-right remove-inputs">-</span>' +
                '<label for="id_template_' + last_template_idx + '">Node template</label>' +
                '<span class="help-block" style="display: none;"></span>' +
                '<div class="input">' +
                    '<select name="template_' + last_template_idx + '" id="id_template_'+ last_template_idx +'" class="templates_select">' +
                    $("#id_template_choices").html() +
                    '</select>' +
                '</div>' +
            '</div>';
        var count_input = '' +
            '<div class="control-group form-field clearfix">' +
                '<label for="id_count_' + last_template_idx + '">Nodes number</label>' +
                '<span class="help-block" style="display: none;"></span>'+
                '<div class="input">'+
                    '<input type="text" name="count_' + last_template_idx + '" value="0" id="id_count_' + last_template_idx + '" data-original-title="">'+
                '</div>'+
            '</div>'+
            '<hr>';
        $("#id_template_choices").closest(".control-group").before(choice_input + count_input);
        $("#id_template_"+ last_template_idx).change();
    }

    $(document).on('change', '.templates_select', function() {
        var id = this.id;
        var block_num = id.replace("id_template_", "");
        var selected = $(this).val().toLowerCase();
        var count_selector = $("#id_count_" + block_num);
        if (selected.indexOf("jt") != -1 || selected.indexOf("nn") != -1) {
            count_selector.val(1);
            count_selector.prop("disabled", true)
        } else {
            count_selector.prop("disabled", false)
        }

        validate();
    });

    $(document).on('click', '#add_template_inputs_btn', function(evt) {
        create_inputs();
    });

    $(document).on('click','.remove-inputs', function(evt) {
        var id = this.id;
        var block_num = id.replace("remove_template_input_", "");
        $("#id_template_" + block_num).closest(".control-group").remove();
        $("#id_count_" + block_num).closest(".control-group").next().remove();
        $("#id_count_" + block_num).closest(".control-group").remove();
        validate();
    });


    horizon.modals.addModalInitFunction(function (modal) {
        last_template_idx = 0;

        $("input[type=submit][value='Create & Launch']").bind('click', function() {
            var result = fillResultField();
            $("#id_result_field").val(result);
        });
        $($("#create_cluster__selectnodetemplatesaction").find("table")[0]).after(
            '<span id="add_template_inputs_btn" data-add-to-field="id_keypair" class="btn btn-inline">+</span>');

        $("#id_template_choices").closest(".control-group").hide();
        $("#id_result_field").closest(".control-group").hide();

        create_inputs()


    })


});