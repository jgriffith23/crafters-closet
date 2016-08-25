/////////////////////////////////////////////////
// jQuery UI Autocomplete Code for Color Fields
/////////////////////////////////////////////////

// Success function to be called after AJAX request for color data.
// Should change the autocomplete options in color textbox.
function replaceColors(results) {
    var tags = results;
    $( ".autocomplete" ).autocomplete({
          source: tags
    });
}

// Fetch the color data from the server.
function updateColors() {
  var brand = encodeURIComponent($("#brand").val());
  $.get("/typeahead/colors-by-brand.json?brand="+brand, replaceColors);
  console.log("AJAX sent.");
}

// Event listeners for elements tha should cause the colors
// autocomplete options to change.
$("#brand").on("change", updateColors);
$(".supplytype").on("change", updateColors);
$(".autocomplete").on("click", updateColors);