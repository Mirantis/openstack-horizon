horizon.addInitFunction(function() {
    $('.ajax-modal-loadbalancing').live('click', function (evt) {
      var $this = $(this),
          token = $('[name="csrfmiddlewaretoken"]').first().value,
          ids = $.map($('[name="object_ids"]'), function(obj) {
                    return $(obj).is(':checked') ? obj.value : null;
                });
      $.ajax({
          url: $this.attr('href'),
          data: {'instances': ids},
          error: function(jqXHR, status, errorThrown) {
            if (jqXHR.status === 401){
              var redir_url = jqXHR.getResponseHeader("X-Horizon-Location");
              if (redir_url){
                location.href = redir_url;
              } else {
                location.reload(true);
              }
            }
          },
          success: horizon.modals.success,
      });
      evt.preventDefault();
    });
});

$(function(){
    $('#instances :checkbox').change(function(){
        setTimeout(function(){
        if ($('#instances :checked').length > 0){
            $('a[id*="loadbalancing"]').removeClass('disabled');}
        else{
            $('a[id*="loadbalancing"]').addClass('disabled');
        }}, 50)
    
    })
})
