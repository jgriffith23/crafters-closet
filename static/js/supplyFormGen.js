console.log("You made it to supplyFormGen");
formCounter = 0;


$("#supply-form-gen").on("click", function() {

    $.get("/create-project/new-supply-form.html?counter="+formCounter, function(results) {
        $("#supplies-to-add").append(results);
    });

    $("#num-supplies").val(formCounter);
    formCounter++;
});