
formCounter = 0;


$("#supply-form-gen").on("click", function() {

    $.get("/create-project/new-supply-form.html?counter="+formCounter, function(results) {
        $("#supplies-to-add").append(results);
    });

    $("#num-supplies").val(formCounter+1);
    formCounter++;
});