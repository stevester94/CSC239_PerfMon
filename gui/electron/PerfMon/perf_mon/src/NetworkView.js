import React, { Component } from 'react';
import StevesTable from "./StevesTable.js"
import DetailsReadout from "./DetailsReadout.js"
import StevesBarGraph from "./StevesBarGraph.js"
import StevesPieGraph from "./StevesPieGraph.js"
import 'react-table/react-table.css'
import StevesStreamingGraph from "./StevesStreamingGraph.js"
import StevesAdaptiveStreamingG from "./StevesAdaptiveStreamingG.js"
import './App.css';

class NetworkView extends Component
{
    state = {
        selections: { // Use this to determine available pages and which is active
            Summary:     {active: true},
            Nic_Metrics: {active: false},
            TCP_Metrics: {active: false},
            UDP_Metrics: {active: false}
        }
    }
    // Will return only elements who's properties contain the filter text
    // Only works with non-nested arrays
    // Returns null if given null
    filter_array_based_on_keys(array)
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
                if(String(element[key]).includes(this.state.filter_text))
                {
                    ret_ar.push(element);
                    break;
                }
            }
        }
        
        return ret_ar;
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
                table_data = this.filter_array_based_on_keys(table_data);
            }
        }
        if(this.state.current_button === "Disks")
        {
            if(this.state.disks != null)
            {
                table_data = this.convert_dict_to_array(this.state.disks, "disk_name");
                table_data = this.filter_array_based_on_keys(table_data);
            }
        }
        if(this.state.current_button === "System")
        {
            if(this.state.cpus != null)
            {
                table_data = this.convert_dict_to_array(this.state.cpus, "logical_cpu");
                table_data = this.filter_array_based_on_keys(table_data);
            }
        }
        if(this.state.current_button === "Network")
        {
            // table_data = this.state.network;
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

    }

    build_nic_page()
    {

    }

    build_tcp_page()
    {

    }

    build_udp_page()
    {

    }

    render()
    {
        const {net_metrics, net_metrics_rates, net_tcp, net_udp, net_nics, net_nics_rates, filter_text } = this.props;
        
        return  (
            <div>
                <select onChange={this.selectChangeHandler.bind(this)}>
                    {Object.keys(this.state.selections).map(function(selection_name) {
                        return <option value={selection_name}>{selection_name}</option>
                    })}
                </select>
                {this.build_summary_page()}
                {this.build_nic_page()}
                {this.build_tcp_page()}
                {this.build_udp_page()}
            </div>
            );
        }
    }
    
    
    
    
    export default NetworkView;
    
    
    
    
    