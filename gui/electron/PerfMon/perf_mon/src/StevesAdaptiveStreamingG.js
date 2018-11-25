import {Line} from 'react-chartjs-2';
import 'react-table/react-table.css';
import React, { Component } from 'react';


var type = "line";



class StevesAdaptiveStreamingG extends Component {
    constructor()
    {
        super();

        this.data = {
            labels: [],
            datasets: [],
            options: {
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
            }
        }
    }
    render() {
        const {data_points, data_labels, x_index, max_data_points, data_label_colors, title} = this.props;

        while(data_points.length > this.data.datasets.length)
        {
            this.data.datasets.push({
                label: '',
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: [],
                fill: false,
            });
        }
        if(title != null)
        {
            this.data.options.title.display = true;
            this.data.options.title.text    = title;
        }
        else
        {
            this.data.options.title.display = false;
        }
        
        for(const [index, data_point] of data_points.entries())
        {
            this.data.datasets[index].data.push(data_point);
            if(this.data.datasets[index].data.length > max_data_points)
            {
                this.data.datasets[index].data.shift();
            }
        }

        for(const [index, data_label] of data_labels.entries())
        {
            this.data.datasets[index].label = data_label;
        }

        for(const [index, color] of data_label_colors.entries())
        {
            this.data.datasets[index].backgroundColor = color;
            this.data.datasets[index].borderColor     = color;
        }

        this.data.labels.push(x_index);
        if(this.data.labels.length > max_data_points)
        {
            this.data.labels.shift();
        }

        // Since we only receive one data point at a time, only need to pop one element from front
        // if(this.data_points.length > max_data_points)
        // {
        //     this.data_points.shift();
        //     this.labels.shift();
        // }
        return(
            <Line data={this.data} options={this.data.options} type={type} redraw={true}/>
        );
    };


}

export default StevesAdaptiveStreamingG;