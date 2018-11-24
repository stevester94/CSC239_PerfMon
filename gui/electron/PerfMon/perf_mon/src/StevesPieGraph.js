import {Pie} from 'react-chartjs-2';
import React, { Component } from 'react';

var options= {
    responsive: true,
    animation: false,
    title: {
        display: true,
        text: '_TITLE_'
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

window.chartColors = {
	red: 'rgb(255, 99, 132)',
	orange: 'rgb(255, 159, 64)',
	yellow: 'rgb(255, 205, 86)',
	green: 'rgb(75, 192, 192)',
	blue: 'rgb(54, 162, 235)',
	purple: 'rgb(153, 102, 255)',
	grey: 'rgb(231,233,237)'
};

var data = {
    labels: [0,1],
    datasets: [{
        label: 'My First dataset',
        backgroundColor: [
            window.chartColors.red,
            window.chartColors.orange,
            window.chartColors.yellow,
            window.chartColors.green,
            window.chartColors.blue,
          ],
        borderColor: 'rgb(255, 99, 132)',
        data: [10,90],
        fill: false,
    }]
}

class StevesPieGraph extends Component {

    render()
    {
        data.labels = this.props.labels;
        data.datasets[0].data = this.props.data;
        options.title.text = this.props.title;
        return (
            <Pie data={data} options={options} redraw={true}/>
        );
    }
}



export default StevesPieGraph;