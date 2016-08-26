// Make the chart responsive...? 
var options = { responsive: true };

// Get the chart context (div where it will live), and make it 2D
var contextForDonut = $("#donutChart").get(0).getContext("2d");

// Make a GET request for the chart data, and make the chart.
$.get("/supply-types.json", function (data) {
    var inventoryChart = new Chart(contextForDonut, {
                                            label: "Supplies by Quantity",
                                            type: 'doughnut',
                                            data: data,
                                            options: options
                                          });
    //$('#donutLegend').html(inventoryChart.generateLegend());
});
