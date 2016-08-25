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
    // debugger;
    console.log(buttonID);
    var col = "#"+buttonID+".qty-column";
    var field = "#"+buttonID+".qty-field";
    if (updating === false) {
        $(this).html("Done!");
        updating = true;
        $(col).html("hey hey hey");
        $(field).toggle();
    }

    else if (updating === true) {
        // debugger;
        updating = false;
        $.post("/update-test", {"qty": $(field).val(), "itemID": buttonID}, function(data) {
            console.log("AJAX sent: " + $(field).val() + " foo " + buttonID);
            console.log(data);
            // debugger;
            $(this).html("Update");
            $(field).toggle();
            $(col).html(data);
        });
    }

});