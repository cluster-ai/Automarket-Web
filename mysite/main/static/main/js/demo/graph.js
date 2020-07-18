

function update_graph() {
  let myChart = document.getElementById('graph').getContext('2d');

  myChart.height = 500;

  let massPopChart = new Chart(myChart, {
    //properties
    type:'line', // bar, horizontal, pie, line, doughnut, radar, polarArea
    data:{
      labels:['Boston', 'Worcester', 'Springfield', 'Lowell', 'Cambridge', 'New Bedford'],
      datasets:[{
        label:'KRAKEN_BTC_5MIN',
        data:[
          617594,
          181045,
          153060,
          106519,
          105162,
          95072
        ],
        lineTension: 0,
        backgroundColor: 'transparent',
        borderColor: '#86C232',
        pointBorderColor: 'transparent'
      }]
    },
    options: {}
  });
}