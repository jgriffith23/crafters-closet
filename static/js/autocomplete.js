/////////////////////////////////////////////////
// jQuery UI Autocomplete Code for Color Fields
/////////////////////////////////////////////////

// Success function to be called after AJAX request for color data.
// Should change the autocomplete options in color textbox.
function replaceTags(results) {
    var tags = results;
    $( ".autocomplete" ).autocomplete({
          source: tags
    });
}

// Fetch the color data from the server.
function updateColors() {
  var brand = encodeURIComponent($("#brand").val());
  $.get("/typeahead/colors-by-brand?brand="+brand, replaceTags);
}

function updateInventorySearch() {
    var searchTerm = encodeURIComponent($("#search-term").val());
    $.get("/inventory/search-autocomplete-tags?search="+searchTerm, replaceTags);
}

// Event listeners for elements tha should cause the colors
// autocomplete options to change.
$("#brand").on("change", updateColors);
$(".supplytype").on("change", updateColors);
$(".autocomplete").on("click", updateColors);
$("#search-term").on("input", updateInventorySearch);