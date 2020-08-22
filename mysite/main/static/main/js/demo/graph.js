

function update_graph() {
  
  //loads index_id
  let index_id = document.getElementById('index_id').innerHTML;
  console.log(index_id);

  //loads selected data features by id into list
  var selected_data = [];
  $("#selector_buttons button").each(function(index) {
    if (this.classList.contains('clicked') == true) {
      selected_data.push(this.id);
    }
  })

  //loads dataframe from server for given index_id
  $.ajax({
      url: 'market_data/',
      data: {
        'index_id': index_id,
        'columns': selected_data
      },
      dataType: 'json',
      type: 'POST',
      success: function (data) {
        load_chart(JSON.parse(data['data']), ['columns']);
      },
      error: function () {
        console.log('error');
      }
    });
}


function load_chart(df_values, column_order) {
  /*
  Parameters:
    df_values (array) - df.to_json(orient="values")
    columns (dict) - key: selected_column, value: list_index of df.columns
  */
  console.log('VALUES:', df_values);

  let myChart = document.getElementById('graph').getContext('2d');

  function averagePrice(row) {
    return row[2];
  }

  var count = 0;
  var time_period_start = [];
  function timePeriodStart(row) {
    time_period_start.push(row[0]);
  }

  var price_average = df_values.map(averagePrice);
  df_values.forEach(timePeriodStart);

  console.log('\nPRICE AVERAGE:', price_average);

  let massPopChart = new Chart(myChart, {
    //properties
    type:'line', // bar, horizontal, pie, line, doughnut, radar, polarArea
    data:{
      labels: time_period_start,
      datasets:[{
        borderWidth: 1,
        label: 'price_average',
        data: price_average,
        lineTension: 0,
        backgroundColor: 'transparent',
        borderColor: '#86C232',
        pointBorderColor: 'transparent'
      }]
    },
    options: {
      animation: {
        duration: 0 // general animation time
      },
        hover: {
        animationDuration: 0 // duration of animations when hovering an item
      },
      responsiveAnimationDuration: 0,
      scales: {
        xAxes: [{
          ticks: {
            userCallback: function(item, index) {
              if (!(index % 500)) return item;
            },
            autoSkip: false
          },
          display: true
        }]
      }
    }
  });
}