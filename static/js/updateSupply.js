///////////////////////////////////////////////
// Code for "Update" buttons on dashboard
///////////////////////////////////////////////


// Get ALL the update buttons!
var update_buttons = $(".update-item");
var updating = false;


// Add an event listener to all the buttons to get the id and send it
// to the server. The button is the thing calling the anonymous function,
// so we can use the fabled `this` keyword.
update_buttons.on("click", function() {
    var buttonID = $(this).attr("id");
    var buttonSelector = "#" + buttonID+".update-item";
    var col = "#"+buttonID+".qty-column";
    var field = "#"+buttonID+".qty-field";
    if (updating === false) {
        $(buttonSelector).html("Done!");
        updating = true;
        $(field).toggle();
    }

    else if (updating === true) {
        updating = false;
        $.post("/update-test", {"qty": $(field).val(), "itemID": buttonID}, function(data) {
            $(field).toggle();
            $(col).html(data);
            if (data === "Deleted!") {
                $(buttonSelector).hide();
            }

            else {
                $(buttonSelector).html("Update");
            }
        });
    }

});