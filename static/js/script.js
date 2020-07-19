window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

$(document).ready(function () {
  
  // trigger delete action for both venue and artist
  $(document).on('click', '#delete_venue, #delete_artist', function(e){
    e.preventDefault();
    
    let action = $(this).data('action'),
        id = $(this).data('id'),
        url = `/${action}/${id}/delete`;
  
       if(confirm("Are You Sure ?")){
        $.ajax({
          url: url,
          method: 'DELETE',
          success: function(data){
            window.location.href = `/${action}`;
          },
          error: function(err){
            console.log(err);
          }
        });
      }

  });
});
