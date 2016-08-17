
var supplyTypes = ["yarn", "oven-bake clay", "acrylic paint"];
var brands = {
    "yarn": ["Red Heart", "Loops & Threads", "Craft Smart"],
    "oven-bake clay": ["Sculpey", "Some Other Place"],
    "acrylic paint": ["Americana", "Craft Smart"]
};

var units = {
    "yarn": "yds",
    "oven-bake clay": "oz",
    "acrylic paint": "oz"
};

console.log("JavaScript maybe?");

// Place an event listener on the supply type dropdown that fires when
// the dropdown value changes.
$("#supplytype").on("click", function () {

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
        var optionStr = "<option value=\""+brands[supplyType][i]+"\">"+brands[supplyType][i]+"</option>";
        $("#brand").append(optionStr);
    }

    $("#units").val(units[supplyType]);

});
