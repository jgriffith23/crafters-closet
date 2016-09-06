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

        $("#search-active-head").html("Click title links to view matching project pages.");

        $.get("/projects/search-results?search=" + encodedSearchTerm,
            function(results) {
                if (results.indexOf("td") > -1) {
                    $("#project-search-results").html(results);
                }

                else {
                    $("#project-search-results").html("<i>I'm sorry, I couldn't find any matching projects! Please try again.</i><br>");
                    $("#project-search-results").append("<img src=\"https://s-media-cache-ak0.pinimg.com/736x/29/d1/1c/29d11cff4795c805abc6010a1690916b.jpg\"></img>");
                }
        });
    }
});