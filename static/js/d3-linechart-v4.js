
    var response = {{ response|tojson|safe }};
    var news = response.news;
    newsAsHTML = news.replace(/(?:\\[rn])+/g,'<br>');
    newsSep = news.replace(/(?:\\[rn])+/g,';');
    console.log(news);
    var newsAsStr = JSON.stringify(news, undefined, 2);
    
    d3.select("body")
  	.append("div").attr("id","json");
    var divJson = document.getElementById("json");
    divJson.innerHTML = newsAsHTML;
    
    /** d3js */
    var margin = {top: 30, right: 20, bottom: 30, left: 50},
    width = 600 - margin.left - margin.right,
    height = 270 - margin.top - margin.bottom;

    // Parse the date / time
    var parseDate = d3.timeParse("%Y-%d-%e");

    // Set the ranges
    var x = d3.scaleTime().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    // Define the axes
    //var xAxis = d3.svg.axis().scale(x).orient("bottom").ticks(5);
    var xAxis = d3.select(".axis").call(d3.axisBottom(x));
    //.tickArguments([5, "s"])
    
    //var yAxis = d3.svg.axis().scale(y).orient("left").ticks(5);
    var yAxis = d3.select(".axis").call(d3.axisLeft(y));
    
    // Define the line
    var valueline = d3.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.close); });
        
    // Adds the svg canvas
    var svg = d3.select("body")
        .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
        .append("g")
            .attr("transform", 
                  "translate(" + margin.left + "," + margin.top + ")");

    var data1 = "date,close\r\n1-May-12,58.13\r\n30-Apr-12,53.98\r\n27-Apr-12,67.00\r\n26-Apr-12,89.70\r\n25-Apr-12,99.00\r\n24-Apr-12,130.28\r\n23-Apr-12,166.70\r\n20-Apr-12,234.98\r\n19-Apr-12,345.44\r\n18-Apr-12,443.34\r\n17-Apr-12,543.70\r\n16-Apr-12,580.13\r\n13-Apr-12,605.23\r\n12-Apr-12,622.77\r\n11-Apr-12,626.20\r\n10-Apr-12,628.44";

    // Prepare data for D3js v4
    var data2 = newsSep.split(';');
    var data = [];
    data2.forEach(function(d) {
      var cols = d.split(',');
      var date1 = parseDate(cols[0]);
      var close = parseFloat(cols[1]);
      var row = {date: date1, close: close};
      console.log(row);
      data.push(row);
    });

    // Get the data
    //d3.csv("data.csv", function(error, data) {
      data.forEach(function(d) {
          console.log('d.date=' + d.date + ', d.close=' + d.close)
      });

      // Scale the range of the data
      x.domain(d3.extent(data, function(d) { return d.date; }));
      y.domain([0, d3.max(data, function(d) { return d.close; })]);

      // Add the valueline path.
      svg.append("path")
          .attr("class", "line")
          .attr("d", valueline(data));

      // Add the X Axis
      svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

      // Add the Y Axis
      svg.append("g")
          .attr("class", "y axis")
          .call(yAxis);
    //});