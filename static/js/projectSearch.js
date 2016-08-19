///////////////////////////////////////////////
// Code for searching the entire database of 
// user-created project pages.
///////////////////////////////////////////////

$("#search-projects").on("click", function () {
    console.log("I see that click you made.");

    var searchTerm = $("#search-term").val();

    console.log("I see " + searchTerm + " in your search box.");

    encodedSearchTerm = encodeURIComponent(searchTerm);

    console.log("I'll send " + encodedSearchTerm + " to the server.");

    $("#search-active-head").html("Projects Relevant to Your Search");

    $.get("/projects/search-results.html?search=" + encodedSearchTerm,
        function(results) {
            $("#project-search-results").append(results);
    });
});