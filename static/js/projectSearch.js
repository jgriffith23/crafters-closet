///////////////////////////////////////////////
// Code for searching the entire database of 
// user-created project pages.
///////////////////////////////////////////////

$("#search-projects").on("click", function () {

    // Get the search term.
    var searchTerm = $("#search-term").val();

    // If the search string is empty, just remove the whole search
    // results section from the page.
    if (searchTerm === ""){
        $("#search-active-head").html("");
        $("#project-search-results").html("");
    }

    // Otherwise, encode search term, create a URL, and send a get request
    // to the server for html containing the search results.
    else{
        encodedSearchTerm = encodeURIComponent(searchTerm);

        $("#search-active-head").html("Projects Relevant to Your Search (Click title links to view supply lists.)");

        $.get("/projects/search-results.html?search=" + encodedSearchTerm,
            function(results) {
                $("#project-search-results").html(results);
        });
    }
});