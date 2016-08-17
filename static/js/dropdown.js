
// var units = {
//     "yarn": "yds",
//     "oven-bake clay": "oz",
//     "acrylic paint": "oz"
// };

// Craft a URL to send a get request for brands and make a variable to hold
// the response.
var brandsURL = "/dashboard/brands.json";
var brands;

// Craft a URL to send a get request for units and make a variable to hold
// the response.
var unitsURL = "/dashboard/units.json";
var units;

// On successfully receiving brands/units data from the server, 
// store it in the variables created previously. These are AJAX get requests
// that take the corresponding URL from above and an anonymous function
// as parameters.
$.get(brandsURL, function(results) {
    brands = results;
});

$.get(unitsURL, function(results) {
    units = results;
});

// Place an event listener on the supply type dropdown that fires when
// the dropdown value changes.
$("#supplytype").on("change", function () {

    // Enable the brands dropdown.
    $("#brand").prop("disabled", false);

    // Clear the old options from the brands dropdown
    $("#brand").empty();

    // Get the supply type from the first dropdown
    var supplyType = $("#supplytype").val();

    // Iterate over the length of the list of brand options. For each,
    // create an option string based on the brands available, and 
    // append that string to the brands dropdown.
    for(var i = 0; i < brands[supplyType].length; i++){
        var optionStr = "<option value=\""+brands[supplyType][i]+"\">"+brands[supplyType][i]+"</option>";
        $("#brand").append(optionStr);
    }

    // Set the value of the units field.
    $("#units").val(units[supplyType]);

});
