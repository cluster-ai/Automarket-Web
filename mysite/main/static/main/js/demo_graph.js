// set the dimensions and margins of the graph
var margin = {top: 6, right: 30, bottom: 19, left: 41},
    width = 800 - margin.left - margin.right,
    height = 200 - margin.top - margin.bottom;

// append the svg object to the body of the page
var svg = d3.select("#graph")
  .append("svg")
    .attr("viewBox", "36 0 775 200")
    .attr("preserveAspectRatio", "xMinYMin meet")
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// set the ranges
var x = d3.scaleTime().range([0, width]);
var y = d3.scaleLinear().range([height, 0]);

// gridlines in x axis function
function make_x_gridlines() {
  return d3.axisBottom(x).ticks(5)
}

// gridlines in y axis function
function make_y_gridlines() {
  return d3.axisLeft(y).ticks(5)
}

//Read the data
d3.csv("https://raw.githubusercontent.com/holtzy/data_to_viz/master/Example_dataset/3_TwoNumOrdered_comma.csv",

  // When reading the csv, I must format variables:
  function(d){
    return { date : d3.timeParse("%Y-%m-%d")(d.date), value : d.value }
  },

  // Now I can use this dataset:
  function(data) {

    // add the X gridlines
    svg.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(make_x_gridlines()
            .tickSize(-height)
            .tickFormat(""));

    // add the Y gridlines
    svg.append("g")
        .call(make_y_gridlines()
            .tickSize(-width)
            .tickFormat(""));

    // Add X axis --> it is a date format
    var x = d3.scaleTime()
      .domain(d3.extent(data, function(d) { return d.date; }))
      .range([ 0, width ]);
    svg.append("g")
      .attr("class", "axis")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x));

    // Add Y axis
    var y = d3.scaleLinear()
      .domain([0, d3.max(data, function(d) { return +d.value; })])
      .range([ height, 0 ]);
    svg.append("g")
      .attr("class", "axis")
      .attr("transform", "translate(" + width + ", 0)")
      .call(d3.axisRight(y));

    // Add the line
    svg.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "#86C232")
      .attr("stroke-width", "1.5")
      .attr("d", d3.line()
        .x(function(d) { return x(d.date) })
        .y(function(d) { return y(d.value) })
        )
  }
)