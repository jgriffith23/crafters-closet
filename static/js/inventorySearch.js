console.log("Hey I found inventorySearch woo!");

// FIXME: On click of one filtering option, disable others!!!

$("#apply-filter").on("click", function() {
    console.log("so I found your apply-filter event...");
    console.log("brand, type, color from dropdowns incoming...");
    console.log($("#filter-brand").val(),
                $("#filter-type").val(),
                $("#filter-color").val());

    var brand = $("#filter-brand").val();

    // Need to use encodeURIComponent() to escape spaces, &, etc. to sanitize
    // input. Will be useful later too!
    var encodedBrand = encodeURIComponent(brand);
    var requestURL = "/inventory/filter.html?brand=" + encodedBrand;
    $.get(requestURL, function(results){
        console.log("Here's my result fresh from Flask: " + results);
        $("#inv-table").html(results);
    });
});

