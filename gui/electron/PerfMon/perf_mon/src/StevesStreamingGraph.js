import {Line} from 'react-chartjs-2';
import 'react-table/react-table.css';
import React, { Component } from 'react';






var type = "line";

var options= {
    responsive: true,
    animation: false,
    title: {
    display: false,
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
        display: false,
        labelString: 'Month'
        }
    }],
    yAxes: [{
        display: true,
        scaleLabel: {
        display: false,
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
        const {data_point, label, max_data_points, title} = this.props;
        this.data_points.push(data_point);
        this.labels.push(label);
        this.data.datasets[0].label = title;

        // Since we only receive one data point at a time, only need to pop one element from front
        if(this.data_points.length > max_data_points)
        {
            this.data_points.shift();
            this.labels.shift();
        }
        //<Line data={this.data} options={options} width={600} height={250} type={type} redraw={true}/>
        return(
            <Line data={this.data} options={options} type={type} redraw={true}/>
        );
    };


}

export default StevesStreamingGraph;