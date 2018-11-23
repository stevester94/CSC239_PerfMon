import {Pie} from 'react-chartjs-2';
import React, { Component } from 'react';

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
        display: false,
        scaleLabel: {
        display: false,
        labelString: 'Month'
        }
    }],
    yAxes: [{
        display: false,
        scaleLabel: {
        display: false,
        labelString: 'Value'
        }
    }]
    }
};

var data = {
    labels: [0,1],
    datasets: [{
        label: 'My First dataset',
        backgroundColor: 'rgb(255, 99, 132)',
        borderColor: 'rgb(255, 99, 132)',
        data: [10,90],
        fill: false,
    }]
}

class StevesPieGraph extends Component {

    render()
    {
        // data.labels = this.props.labels;
        // data.datasets[0].data = this.props.data;
        // data.datasets[0].label = this.props.title;
        return (
            <Pie data={data} options={options} redraw={true}/>
        );
    }
}



export default StevesPieGraph;