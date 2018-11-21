import {Line} from 'react-chartjs-2';
import 'react-table/react-table.css';
import React, { Component } from 'react';






var type = "line";

var options= {
    responsive: true,
    animation: false,
    title: {
    display: true,
    text: 'Chart.js Line Chart'
    },
    tooltips: {
    mode: 'index',
    intersect: false,
    },
    hover: {
    mode: 'nearest',
    intersect: true
    },
    scales: {
    xAxes: [{
        display: true,
        scaleLabel: {
        display: true,
        labelString: 'Month'
        }
    }],
    yAxes: [{
        display: true,
        scaleLabel: {
        display: true,
        labelString: 'Value'
        }
    }]
    }
};

class StevesStreamingGraph extends Component {
    constructor()
    {
        super();
        this.data_points = [0,10,100];
        this.labels = [1,2,3];

        this.data = {
            labels: this.labels,
            datasets: [{
                label: 'My First dataset',
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: this.data_points,
                fill: false,
            }]
        }
    }
    render() {
        return(
            <Line data={this.data} options={options} width={600} height={250} type={type} redraw={true}/>
        );
    };


}

export default StevesStreamingGraph;