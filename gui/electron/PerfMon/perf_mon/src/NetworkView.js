import React, { Component } from 'react';
import StevesTable from "./StevesTable.js"
import DetailsReadout from "./DetailsReadout.js"
import StevesBarGraph from "./StevesBarGraph.js"
import StevesPieGraph from "./StevesPieGraph.js"
import 'react-table/react-table.css'
import StevesStreamingGraph from "./StevesStreamingGraph.js"
import StevesAdaptiveStreamingG from "./StevesAdaptiveStreamingG.js"
import './App.css';

var RANDOM_COLORS = ['rgb(255, 99, 132)', 'rgb(255, 159, 64)', 'rgb(255, 205, 86)', 'rgb(75, 192, 192)', 'rgb(54, 162, 235)', 'rgb(153, 102, 255)', 'rgb(231,233,237)' ];

class NetworkView extends Component
{
    net_metrics = null;
    net_metrics_rates = null;
    net_tcp = null;
    net_udp = null;
    net_nics = null;
    net_nics_rates = null;
    filter_text = null;

    state = {
        selections: { // Use this to determine available pages and which is active
            // Summary:     {active: true},
            Nic_Metrics: {active: true},
            TCP_Metrics: {active: false},
            UDP_Metrics: {active: false}
        }
    }
    // Will return only elements who's properties contain the filter text
    // Only works with non-nested arrays
    // Returns null if given null
    filter_array_based_on_keys(array, filter)
    {
        if(array == null)
        {
            return null;
        }
        
        let ret_ar = []
        for(var element of array)
        {
            for(var key of Object.keys(element))
            {
                if(String(element[key]).includes(filter))
                {
                    ret_ar.push(element);
                    break;
                }
            }
        }
        
        return ret_ar;
    }

    // I know, I'm mixing python terms here. dict == object with a shit ton of keys
    // Will convert the object into a list, with the keys stored as <name_for_primary_key>
    convert_dict_to_array(dict, name_for_primary_key)
    {
        let array = [];

        for(var entry of Object.keys(dict))
        {
            dict[entry][name_for_primary_key] = entry;
            array.push(dict[entry]);
        }

        return array;
    }
    
    // Select the correct table data and transmute to the generic format that
    // StevesTable can ingest. If there is no data, returns null
    generate_table_data()
    {
        let table_data = null;
        
        if(this.state.current_button === "Processes")
        {
            if(this.state.procs != null)
            {
                table_data = this.convert_dict_to_array(this.state.procs, "pid");
                table_data = this.filter_array_based_on_keys(table_data, this.filter_text);
            }
        }
        
        return table_data;
    }
    
    selectChangeHandler(event)
    {
        console.log(event.target.value);

        for(var selection of Object.keys(this.state.selections))
        {
            if(selection === event.target.value)
                this.state.selections[selection].active = true;
            else    
                this.state.selections[selection].active = false;
        }

        this.setState(prevState =>({}));
    }

    build_summary_page()
    {
        if(!this.state.selections.Summary.active || this.net_nics_rates == null)
            return;
        
    }


    // <StevesAdaptiveStreamingG 
    // // title={reads_writes_title} 
    // data_points={reads_writes_data} 
    // data_labels={reads_writes_labels} 
    // data_label_colors={reads_writes_colors}
    // x_index={reads_writes_x_index}
    // max_data_points={5}/>

    build_nic_page()
    {
        if(!this.state.selections.Nic_Metrics.active || this.net_nics_rates == null)
            return;

        let table_data;
        table_data = this.convert_dict_to_array(this.net_nics, "NIC");
        table_data = this.filter_array_based_on_keys(table_data, this.filter_text);

        let nic_rates = this.convert_dict_to_array(this.net_nics_rates, "NIC");
        console.log(nic_rates);
        let nic_rates_graphs = [];
        for(var nic of nic_rates)
        {
            let data_points = [];
            let data_labels = [];
            let label_colors = [];
            let index = 0;
            for(var key of Object.keys(nic))
            {
                // Skip if key is NIC or key is max_speed_bytes and that value is -1
                if (!(key == "NIC" || (key == "max_speed_bytes" && nic.max_speed_bytes == -1))) // Filter out the sentinel max speed bytes value 
                {
                    data_labels.push(key);
                    data_points.push(nic[key]);
                    label_colors.push(RANDOM_COLORS[index]);
                }
                index++;
            }
            console.log(nic.NIC);
            nic_rates_graphs.push(
                <div className="flex-grower">
                    <StevesAdaptiveStreamingG 
                    title={nic.NIC}     
                    data_points={data_points} 
                    data_labels={data_labels} 
                    data_label_colors={label_colors}
                    x_index={this.timestamp}
                    max_data_points={5}/>
                </div>
            );

        }

        let containers = [];
        for(var i = 0; i < nic_rates_graphs.length; i++)
        {
            
            containers.push(
                <div className="container">
                    {nic_rates_graphs[i]}
                    {++i < nic_rates_graphs.length ? (nic_rates_graphs[i]) : (null)}
                </div>
            );
                    
        }

        return (
            <>
                {/* <div className="container"> */}
                    {/* {nic_rates_graphs} */}
                    {containers}
                {/* </div> */}
                <StevesTable table_data={table_data}/>
            </>
        );
        
    }

    build_tcp_page()
    {
        if(!this.state.selections.TCP_Metrics.active || this.net_nics_rates == null)
            return;

        let table_data;

        table_data = this.filter_array_based_on_keys(this.net_tcp, this.filter_text);

        let metrics = [];
        let metrics_rates_line_graphs = [];
        for(var key of Object.keys(this.net_metrics))
        {
            console.log(key);
            if(key.includes("tcp"))
            {
                metrics.push(key + ": " + this.net_metrics[key]);
            }
        }
        for(var key of Object.keys(this.net_metrics_rates))
        {
            if(key.includes("tcp"))
            {
                metrics_rates_line_graphs.push(
                    <div>
                        <StevesStreamingGraph 
                            data_point={this.net_metrics_rates[key]} 
                            label={this.timestamp} 
                            title={key} 
                            max_data_points={5}/>
                    </div>
                );
            }
        }
        return (
            <div>
                <div className="container">
                    {metrics_rates_line_graphs}
                    <div><DetailsReadout details={metrics} title="TCP Totals"/></div>
                </div>
                <StevesTable table_data={table_data}/>
            </div>
        );
        
    }

    build_udp_page()
    {
        if(!this.state.selections.UDP_Metrics.active || this.net_nics_rates == null)
            return;
        let table_data;

        table_data = this.filter_array_based_on_keys(this.net_udp, this.filter_text);

        let metrics = [];
        let metrics_rates_line_graphs = [];
        for(var key of Object.keys(this.net_metrics))
        {
            console.log(key);
            if(key.includes("udp"))
            {
                metrics.push(key + ": " + this.net_metrics[key]);
            }
        }
        for(var key of Object.keys(this.net_metrics_rates))
        {
            if(key.includes("udp"))
            {
                metrics_rates_line_graphs.push(
                    <div>
                        <StevesStreamingGraph 
                            data_point={this.net_metrics_rates[key]} 
                            label={this.timestamp} 
                            title={key} 
                            max_data_points={5}/>
                    </div>
                );
            }
        }
        return (
            <div>
                <div className="container">
                    {metrics_rates_line_graphs}
                    <div><DetailsReadout details={metrics} title="UDP Totals"/></div>
                </div>
                <StevesTable table_data={table_data}/>
            </div>
        );
    }

    render()
    {
        const { net_metrics, net_metrics_rates, net_tcp, net_udp, net_nics, net_nics_rates, filter_text, timestamp} = this.props;

        this.net_metrics = net_metrics;
        this.net_metrics_rates = net_metrics_rates;
        this.net_tcp = net_tcp;
        this.net_udp = net_udp;
        this.net_nics = net_nics;
        this.net_nics_rates = net_nics_rates;
        this.filter_text = filter_text;
        this.timestamp = timestamp;
        
        return  (
            <div>
                <select onChange={this.selectChangeHandler.bind(this)}>
                    {Object.keys(this.state.selections).map(function(selection_name) {
                        return <option value={selection_name}>{selection_name}</option>
                    })}
                </select>
                {/* {this.build_summary_page()} */}
                {this.build_nic_page()}
                {this.build_tcp_page()}
                {this.build_udp_page()}
            </div>
            );
        }
    }
    
    
    
    
    export default NetworkView;
    
    
    
    
    