import React, { Component } from 'react';
import { runInThisContext } from 'vm';
import { Line } from 'react-chartjs-2';
import Historian2 from "./Historian2.js"


const { ipcRenderer } = window.require('electron');


var chart_options = {
    responsive: true,
    animation: false,
    maintainAspectRatio: false,
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
            // gridLines: {
            //     color: "grey"
            // },
            scaleLabel: {
                display: false,
                labelString: 'Month',
            }
        }],
        yAxes: [{
            display: true,
            // gridLines: {
            //     color: "grey"
            // },
            scaleLabel: {
                display: false,
                labelString: 'Value',
            }
        }]
    }
};

class Historian extends Component {
    state = {
        keys: null,
        current_data: {},
        current_source: [],
        chart_data: {
            labels: [],
            datasets: [{
                label: '',
                backgroundColor: 'rgb(94, 63, 144)',
                borderColor: 'rgb(94, 63, 144)',
                data: [],
                fill: false,
            }]
        },
        selector_refs:[] // Each selector will be given a ref from this, probably not great but whatever
    }

    constructor()
    {
        super();
        console.log("Historian constructing");

        for(var i = 0; i < 10; i++)
        {
            this.state.selector_refs.push(null);
        }

        this.x_data = [];
        this.y_data = [];

        this.request_all_keys();
    }

    get_time_string_from_epoch(epoch) {
        let d = new Date(epoch * 1000);
        return String(d.getHours()) + ":" + String(d.getMinutes()) + ":" + String(d.getSeconds());
    }

    // msg: historian-request-all
    // response: historian-response-all
    request_all_history(key)
    {
        console.log("Requesting all for key: ");
        console.log(key);
        ipcRenderer.send('historian-request-all', key);

        ipcRenderer.once('historian-response-all', (event, arg) => {
            console.log("Received historian-response-all");
            console.log(arg);

            this.state.y_data = [];
            this.state.x_data = [];

            for(var data_point of arg)
            {
                this.state.x_data.push(this.get_time_string_from_epoch(data_point.timestamp));
                this.state.y_data.push(data_point.value);
            }

            this.setState(prevState => ({}));
        });
    }

    // msg: historian-request-keys
    // response: historian-response-keys
    request_all_keys()
    {
        console.log("Requesting keys");
        ipcRenderer.send('historian-request-keys', "");

        ipcRenderer.once('historian-response-keys', (event, arg) => {
            console.log("Received historian-response-keys");
            console.log(arg);

            this.setState(prevState => ({
                keys: arg
            }));
        })
    }

    // msg: historian-request-range
    // response: historian-response-range
    request_history(key, start_epoch, end_epoch)
    {

    }

    selectChangeHandler(is_final_field, source_index, arg)
    {
        console.log("Selector called: " + arg.target.value);
        if(source_index == this.state.current_source.length) // Regular case where we just tack it on
        {

            this.state.current_source.push(arg.target.value);
        }
        else if(source_index < this.state.current_source.length) 
        {
            /* This is the case where we have gone somewhere back in the chain and changed our
             * mind as to what we want to see.
             * Could be as simple as change the last field, or have to completely blow away everything in front of it
             */
            this.state.current_source[source_index] = arg.target.value;
            this.state.current_source = this.state.current_source.slice(0, source_index+1); // End index is non-inclusive so add 1
            if(!is_final_field)
                this.state.selector_refs[source_index + 1].current.selectedIndex = 0; // Reset the god damn selection, as long as its not the last one
            // Reset the god damn chart data and title
            this.state.x_data = [];
            this.state.y_data = [];
            this.setState(prevState => ({}));

        }

        if(is_final_field)
        {
            console.log("Final field selected, total source array:");
            console.log(this.state.current_source);

            // Set the title of the chart to the last source name
            this.state.chart_data.datasets[0].label = this.state.current_source[this.state.current_source.length-1];


            this.request_all_history(this.state.current_source);
        }
        else
        {
            // Just update the chain, nothing else to do
            this.setState(prevState => ({}));
        }
    }

    build_selectors()
    {
        if(this.state.keys == null)
            return;
        
        let selectors = [];
        
        for(let i = 0; i <= this.state.current_source.length; i++)
        {
            // This for loop is to progress through the hierarchy of keys that are defined
            // in the keys state object for our current depth.
            let current_keys = this.state.keys;
            for(let j = 0; j < i; j++)
            {
                current_keys = current_keys[this.state.current_source[j]]
            }

            if(current_keys == null)
            {
                console.log("Reached base case");
                return selectors;
            }

            // Check to see if this is the final layer, if so we need to indicate as much to the selectChangeHandler that selecting this
            // guy will mean we need to make a request to the backend.
            // Not great since we only check the first one (if the hierarchy was not balanced this would not work)
            let is_this_the_final_layer = false;
            if(current_keys[Object.keys(current_keys)[0]] == null)
            {
                is_this_the_final_layer = true;
            }

            this.state.selector_refs[i] = React.createRef();

            let selector =
                <select fugg="jej" ref={this.state.selector_refs[i]} onChange={this.selectChangeHandler.bind(this, is_this_the_final_layer, i)}>
                    <option value="" disabled selected>Select field</option>
                    {Object.keys(current_keys).map(function (selection_name) {
                        return <option value={selection_name}>{selection_name}</option>
                    })}
                </select>
            selectors.push(selector);
        }

        return selectors;
    }

    render() {
        console.log(this.state.x_points);
        console.log(this.state.y_points);
        return (
            <div>
                {this.build_selectors()}
                <Historian2 x_data={this.state.x_data} y_data={this.state.y_data} />
            </div>
        );
    }
}



export default Historian;