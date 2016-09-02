
//////////////////////////////////////////////
// Filter inventory code
//////////////////////////////////////////////

var filterDrops = $(".filter");

$(filterDrops).on("change", function() {
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
        $("#inv-table").html(results);
    });
});


//////////////////////////////////////////////
// Search inventory code
//////////////////////////////////////////////

$("#search-button").on("click", function() {
    // Get the entered search term.
    var searchTerm = $("#search-term").val();

    // Encode the search term for use in URLs.
    var encodedSearchTerm = encodeURIComponent(searchTerm);

    // Craft a request URL.
    var requestURL = "/inventory/search-results.html?search=" + encodedSearchTerm;

    // Make a get request to the crafted URL. Expecting new html for the
    // inventory table in response.
    $.get(requestURL, function(results) {
        $("#inv-table").html(results);
    });
});


/////////////////////////////////////////////
// Clear all applied filters/searches
/////////////////////////////////////////////

$("#clear-filters").on("click", function() {

    requestURL = "/inventory/filter.html?brand=&supplytype=&color=";
    $.get(requestURL, function(results) {
        $("#inv-table").html(results);
    });
});