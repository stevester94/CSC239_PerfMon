import React, { Component } from 'react';
import './App.css';
import * as am4core from "@amcharts/amcharts4/core";
import * as am4charts from "@amcharts/amcharts4/charts";
import am4themes_animated from "@amcharts/amcharts4/themes/animated";

am4core.useTheme(am4themes_animated);





class Historian2 extends Component {
    componentDidMount() {
        const {x_data, y_data} = this.props;
        let chart = am4core.create("chartdiv", am4charts.XYChart);
        
        // let x_data = [10,300,12];
        // let y_data = [1,2,3];

        chart.data = [];
        for(var i = 0; i < x_data.length; i++)
        {
            chart.data.push({"category": x_data[i], "value": y_data[i]});
        }

        // chart.data = [{
        //     "category": "1",
        //     "value": 12
        // }, {
        //     "category": "2",
        //     "value": 4
        // }, {
        //     "category": "3",
        //     "value": 7
        // }, {
        //     "category": "4",
        //     "value": 8
        // }, {
        //     "category": "5",
        //     "value": 4
        // }, {
        //     "category": "6",
        //     "value": 10
        // }];

        // Create axes
        var categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
        categoryAxis.dataFields.category = "category";
        categoryAxis.renderer.grid.template.location = 0;
        categoryAxis.renderer.minGridDistance = 30;
        categoryAxis.renderer.grid.template.location = 0.5;
        categoryAxis.startLocation = 0.3;
        categoryAxis.endLocation = 0.7;

        var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());

        // Create series
        var series = chart.series.push(new am4charts.LineSeries());
        series.strokeWidth = 3;
        series.dataFields.valueY = "value";
        series.dataFields.categoryX = "category";
        series.tooltipText = "{value}";


        chart.cursor = new am4charts.XYCursor();
    }
    
    componentWillUnmount() {
        if (this.chart) {
            this.chart.dispose();
        }
    }
    
    render() {
        return (
            <div id="chartdiv" style={{ width: "100%", height: "500px" }}></div>
            );
        }
    }
    
    
    export default Historian2;
    