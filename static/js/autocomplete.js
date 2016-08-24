/////////////////////////////////////////////////
// jQuery UI Autocomplete Code for Color Fields
/////////////////////////////////////////////////

function replaceColors(results) {
    var tags = results;
    $( "#color" ).autocomplete({
          source: tags
    });
}

function updateColors() {
  var brand = encodeURIComponent($("#brand").val());
  $.get("/typing-test/colors-by-brand.json?brand="+brand, replaceColors);
  console.log("AJAX sent.");
}

$("#brand").on("change", updateColors);
$("#supplytype").on("change", updateColors);
$("#color").on("click", updateColors);