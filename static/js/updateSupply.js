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
    var col = "#"+buttonID+".qty-column";
    var field = "#"+buttonID+".qty-field";

    if (updating === false) {
        updating = true;
        // Get the button id and use it to create a class/id selector
        // for the column we want to chang.

        $(col).html("hey hey hey");
        $(field).toggle();
    }

    else if (updating === true) {
        updating = false;
        $.post("/update-test", $(field).val(), function(data) {
            console.log("AJAX sent." + $(field).val());
            console.log(data);
        });
    }

});