window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

$(document).ready(function () {
  $("#seeking_venue, #seeking_talent").on("change", function(e){
    e.preventDefault();
    if ($(this).prop("checked", true)) {
      $(this).attr("value") == true;
    } else {
      $(this).attr("value") == false;
    }
  });
  $(document).on('click', '#delete_venue', function(e){
    e.preventDefault();
    let venue_id = $(this).data('id'),
        url = '/venues/' + venue_id + '/delete';
    if(confirm("Are You Sure ?")){
      $.ajax({
        url: url,
        method: 'DELETE',
        success: function(data){
          // window.location.href = '/venues';
        },
        error: function(err){
          console.log(err);
        }
      });
    }
  });
});
