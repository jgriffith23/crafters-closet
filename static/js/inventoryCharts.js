// Make the chart responsive...? 
var options = { responsive: true,
                tooltips: {
                enabled: true,
                mode: 'single',
                callbacks: {
                    label: function(tooltipItems, data) {
                                // debugger;
                                return data.labels[tooltipItems.index] + ": " + data.datasets[0].data[tooltipItems.index] + '%';
                           }
                }
              }
};

// Get the chart context (div where it will live), and make it 2D
var contextForDonut = $("#donutChart").get(0).getContext("2d");

// Make a GET request for the chart data, and make the chart.
$.get("/supply-types", function (data) {
    var inventoryChart = new Chart(contextForDonut, {
                                            label: "Supplies by Quantity",
                                            type: 'doughnut',
                                            data: data,
                                            options: options
                                          });
});
