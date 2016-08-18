console.log("Hey I found inventorySearch woo!");

$("#apply-filter").on("click", function() {
    console.log("so I found your apply-filter event...");

    // Get the values to craft our request URL from the DOM.
    var brand = $("#filter-brand").val();
    var type = $("#filter-type").val();
    var color = $("#filter-color").val();

    // Need to use encodeURIComponent() to escape spaces, &, etc. to sanitize
    // input. Will be useful later too!
    var encodedBrand = encodeURIComponent(brand);
    var encodedType = encodeURIComponent(type);
    var encodedColor = encodeURIComponent(color);

    // Craft request URL with filter params.
    var requestURL = "/inventory/filter.html?brand=" + encodedBrand +
                     "&supplytype=" + encodedType +
                     "&color=" + encodedColor;

    // Make a get request to the crafted URL. Expecting new html for the
    // inventory table in response.
    $.get(requestURL, function(results){
        console.log("Here's my result fresh from Flask: " + results);
        $("#inv-table").html(results);
    });
});

