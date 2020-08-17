

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
        load_chart(data['data']);
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
  let myChart = document.getElementById('graph').getContext('2d');

  // TEMPORARY iterates df_values for price_average TEMPORARY //
  price_average = [];
  for (row in df_values) {
    price_average.push(row[2]);
  }

  console.log(Array.from(price_average));

  let massPopChart = new Chart(myChart, {
    //properties
    type:'line', // bar, horizontal, pie, line, doughnut, radar, polarArea
    data:{
      labels: [],
      datasets:[{
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
      responsiveAnimationDuration: 0
    }
  });
}