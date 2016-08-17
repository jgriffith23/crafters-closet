
// var units = {
//     "yarn": "yds",
//     "oven-bake clay": "oz",
//     "acrylic paint": "oz"
// };

// Craft a URL to send a get request to.
var brandsURL = "/dashboard/brands.json";
var brands;
var unitsURL = "/dashboard/units.json";
var units;

$.get(brandsURL, function(results) {
    console.log("I'm trying to get the brands!");
    brands = results;
});

$.get(unitsURL, function(results) {
    debugger;
    console.log("I'm trying to get the units!");
    units = results;
    console.log(results);
});

console.log("JavaScript maybe?");

// Place an event listener on the supply type dropdown that fires when
// the dropdown value changes.
$("#supplytype").on("change", function () {

    console.log("I'm in the event now!");


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
        console.log("I'm getting inside your for loop.");
        var optionStr = "<option value=\""+brands[supplyType][i]+"\">"+brands[supplyType][i]+"</option>";
        $("#brand").append(optionStr);
    }

    $("#units").val(units[supplyType]);

});
