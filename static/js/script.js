window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

$(document).ready(function () {
  $("#seeking_venue, #seeking_talent").on("change", function (e) {
    e.preventDefault();

    if ($(this).prop("checked", true)) {
      $(this).attr("value") == true;
    } else {
      $(this).attr("value") == false;
    }
  });
});
