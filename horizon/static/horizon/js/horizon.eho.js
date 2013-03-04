horizon.addInitFunction(function () {

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


    var max_template_idx = 4;
    var last_template_idx = 0;

    function add_template_inputs() {
        if (last_template_idx == max_template_idx) {
            return;
        }
        last_template_idx += 1;
        $("#id_template_" + last_template_idx).closest(".control-group").show();
        $("#id_count_" + last_template_idx).closest(".control-group").show();

        if (last_template_idx == max_template_idx) {
            $('#add_template_inputs_btn').hide();
        }

    }

    $(document).on('click', '#add_template_inputs_btn', function(evt) {
        add_template_inputs();
    });


    //hide all template inputs initially

    horizon.modals.addModalInitFunction(function (modal) {
        last_template_idx = 0;
        $("#id_count_0").after("<hr>");
        $($("#create_cluster__nodesaction").find("table")[0]).after(
            '<span id="add_template_inputs_btn" data-add-to-field="id_keypair" class="btn btn-inline">+</span>');
        for (var i = 1; i <= max_template_idx; i++) {
            $("#id_template_" + i).closest(".control-group").hide();
            $("#id_count_" + i).closest(".control-group").hide();
            $("#id_count_" + i).after("<hr>");
        }
    })


});