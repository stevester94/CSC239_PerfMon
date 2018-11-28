import React, { Component, TextInput } from 'react';
import StevesTable from "./StevesTable.js"
import DetailsReadout from "./DetailsReadout.js"
import StevesBarGraph from "./StevesBarGraph.js"
import StevesPieGraph from "./StevesPieGraph.js"
import { Chart } from 'react-chartjs-2';

import './App.css';
import 'react-table/react-table.css'
// import { throws } from 'assert';
import StevesStreamingGraph from "./StevesStreamingGraph.js"
import StevesAdaptiveStreamingG from "./StevesAdaptiveStreamingG.js"
import NetworkView from "./NetworkView.js"


const { ipcRenderer } = window.require('electron');

var COLORS = {
	RED: 'rgb(255, 99, 132)',
	ORANGE: 'rgb(255, 159, 64)',
	YELLOW: 'rgb(255, 205, 86)',
	GREEN: 'rgb(75, 192, 192)',
	BLUE: 'rgb(54, 162, 235)',
	PURPLE: 'rgb(153, 102, 255)',
  GREY: 'rgb(231,233,237)',
};

class NewApp extends Component {
  state = {
    procs: null,
    disks: null,
    cpus: null,
    system: null,
    net_metrics: null,
    net_metrics_rates: null,
    net_tcp: null,
    net_udp: null,
    net_nics: null,
    net_nics_rates: null,
    buttons: [ // Beware, selected is only used for theming of the button
      {name: "Processes", selected: true},
      {name: "Disks", selected: false},
      {name: "System", selected: false},
      {name: "Network", selected: false}
    ],
    current_button: "Processes",
    filter_text: "",
    time_of_last_data: null,
    cpus_or_system_received: false // Need to synchronize these two because the state is getting update too fast
  };

  get_current_time()
  {
    let d = new Date();
    return String(d.getHours()) + ":" + String(d.getMinutes()) + ":" + String(d.getSeconds());
  }
  constructor()
  {
    super();

    Chart.defaults.global.defaultFontColor = 'white';

    // In renderer process (web page).

    // The state of this class will hold the raw objects that are sent from the distributor
    // Further processing will occur on demand when feeding consumers
    // State is only truely updated for the currently selected button
    // Other states are updated, but not through the actual setState, so render is not fired needlessly
    // Message handlers
    ipcRenderer.on('msg_procs', function(event, arg) {
      console.log("Renderer received following msg_id: " + "msg_procs");
      console.log("Current button " + this.state.current_button);
      if(this.state.current_button === "Processes")
      {
        console.log("Setting procs state");
        this.setState(prevState =>({
          procs: arg,
          time_of_last_data: this.get_current_time()
        }));
      }
      else
      {
        this.state.procs = arg;
      }
    }.bind(this));

    ipcRenderer.on('msg_disks', function(event, arg) {
      console.log("Renderer received following msg_id: " + "msg_disks");
      if(this.state.current_button === "Disks")
      {
        this.setState(prevState =>({
          disks: arg,
          time_of_last_data: this.get_current_time()
        }));
      }
      else
      {
        this.state.disks = arg;
      }
    }.bind(this));

    ipcRenderer.on('msg_cpus', function(event, arg) {
      console.log("Renderer received following msg_id: " + "msg_cpus");
      if(this.state.cpus_or_system_received)
      {
        if(this.state.current_button === "System")
        {
          this.setState(prevState =>({
            cpus: arg,
            time_of_last_data: this.get_current_time(),
            cpus_or_system_received: false // Reset for next volley
          }));
        }
        else 
        {
          this.state.cpus = arg;
          this.state.cpus_or_system_received = false;
        }
      }
      else
      {
        this.state.cpus_or_system_received = true;
        this.state.cpus = arg;
      }
    }.bind(this));

    ipcRenderer.on('msg_system', function(event, arg) {
      console.log("Renderer received following msg_id: " + "msg_system");
      if(this.state.cpus_or_system_received)
      {
        if(this.state.current_button === "System")
        {
          this.setState(prevState =>({
            system: arg,
            time_of_last_data: this.get_current_time(),
            cpus_or_system_received: false // Reset for next volley
          }));
        }
        else
        {
          this.state.cpus_or_system_received = false;
          this.state.system = arg;
        }
      }
      else
      {
        this.state.cpus_or_system_received = true;
        this.state.system = arg;
      }
    }.bind(this));

    ipcRenderer.on('msg_net', (event, arg) => {
      console.log("Renderer received following msg_id: " + "msg_net");
      if(this.state.current_button == "Network")
      {
        this.setState(prevState =>({
          net_metrics: arg.net_metrics,
          net_metrics_rates: arg.net_metric_rates,
          net_tcp: arg.tcp_info,
          net_udp: arg.udp_info,
          net_nics: arg.nic_metrics,
          net_nics_rates: arg.nic_metrics_rates,
          time_of_last_data: this.get_current_time()
        }));
      }
      else
      {
        this.state.net_metrics = arg.net_metrics;
        this.state.net_metrics_rates = arg.net_metric_rates;
        this.state.net_tcp = arg.tcp_info;
        this.state.net_udp = arg.udp_info;
        this.state.net_nics = arg.nic_metrics;
        this.state.net_nics_rates = arg.nic_metrics_rates;
      }

    });

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

  handleChildClick(childData, event)
  {
    for(var button of this.state.buttons)
    {
      if(button.name === String(childData))
      {
        button.selected = true;
      }
      else
      {
        button.selected = false;
      }
    }

    this.setState(prevState =>({
      current_button: String(childData)
    }));


  }

  handleFilterTextEnter(event)
  {
    if (event.key === 'Enter') {
      console.log('Filter text: ' + this.filter_text);
      this.setState(prevState =>({
        filter_text: this.state.filter_text
      }));
    }
  }

  handleFilterTextChange(change)
  {
    this.state.filter_text = change.target.value;
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

  build_procs_page()
  {
    let components = [];

    if(this.state.procs != null && this.state.current_button === "Processes")
    {
      let table_data = this.generate_table_data();

      // Num procs graph
      let num_procs = Object.keys(this.state.procs).length
      let procs_graph = <StevesStreamingGraph
        title="Num Procs"
        label={this.state.time_of_last_data} 
        data_point={num_procs} 
        max_data_points={5}/>;

      // Data table
      let table = <StevesTable table_data={table_data}/>;

      let user_busyness = {}
      let total_mem_bytes = 0;
      let total_interval_usage  = 0;
      for(var process of table_data)
      {
        total_mem_bytes += process.physical_mem_KBytes;
        total_interval_usage += process.interval_utilization;

        if(!(process.username in user_busyness))
        {
          user_busyness[process.username] = 0.0;
        }
        console.log(process.interval_utilization);
        user_busyness[process.username] += process.interval_utilization;
      }

      let details = [];
      let busiest_user = Object.keys(user_busyness).reduce(function(a, b){ return user_busyness[a] > user_busyness[b] ? a : b });
      details.push("Busiest User: " + busiest_user);
      details.push("Average physical mem usage: " + String(total_mem_bytes /table_data.length    ));
      details.push("Average interval usage: " + String(total_interval_usage/table_data.length    ));

      return (
        <>
          <div className="container">
            <div>{procs_graph}</div>
            <div><DetailsReadout details={details}/></div>
          </div>
          <div>{table}</div>
        </>
      )
    }
    
    return;
  }

  build_disks_page()
  {
    let components = [];

    if(this.state.disks != null && this.state.current_button == "Disks")
    {
      let table_data = this.generate_table_data();
      
      // Disk usage bar graph
      let usage_title = "Disk Usage"
      let usage_data = [];
      let usage_labels = [];
      for(var disk of table_data)
      {
        usage_labels.push(disk.disk_name);
        usage_data.push(disk.percent_used);
      }

      // TODO: Too fuckin lazy to do this shit, streaming graph doesn't support multiple datasets to be streamed
      // Reads per second line graph
      let reads_writes_title = "Total Reads/Writes per second";
      let reads_writes_data = [0,0];
      let reads_writes_labels = ["Reads", "Writes"];
      let reads_writes_colors = [COLORS.BLUE, COLORS.RED];
      let reads_writes_x_index = this.state.time_of_last_data;
      for(var disk of table_data)
      {
        reads_writes_data[0] += disk.reads_per_second;
        reads_writes_data[1] += disk.writes_per_second;
        // delete disk.writes_per_second;
        // delete disk.reads_per_second;
      }

      // console.log("reads_data");
      // console.log(reads_data);
      // console.log(table_data);

      let disks_graph = <StevesBarGraph title={usage_title} labels={usage_labels} data={usage_data} max_y={1.0}/>

      // Data table
      let table = <StevesTable table_data={table_data}/>;

      return (
        <>
          <div className="container">
            <div>{disks_graph}</div>
            {/* <div className="flex-grower"> */}
            <div>
              <StevesAdaptiveStreamingG 
                  // title={reads_writes_title} 
                  data_points={reads_writes_data} 
                  data_labels={reads_writes_labels} 
                  data_label_colors={reads_writes_colors}
                  x_index={reads_writes_x_index}
                  max_data_points={5}/></div>
          </div>
          <div>{table}</div>

        </>
      );
    }

    return;
  }

  build_system_page()
  {
    if(this.state.system != null && this.state.current_button == "System")
    {

      // Mem usage pie chart
      let mem_labels = ["used", "free"];
      let mem_data = [this.state.system.total_kbytes - this.state.system.free_kbytes, this.state.system.free_kbytes];
      let mem_title = "Memory usage";

      // context switches per second graph
      let context_label = this.state.time_of_last_data;
      let context_data   = this.state.system.context_switches_per_second;
      let context_title  = "Context Switches per second";
      delete this.state.system.context_switches_per_second; // Perhaps delete from the details table instead?

      // interrupts per second graph
      let interrupts_label = this.state.time_of_last_data;
      let interrupts_data  = this.state.system.interrupts_per_second;
      let interrupts_title = "Interrupts per second";
      delete this.state.system.interrupts_per_second;


      let details = Object.keys(this.state.system).map(function(detail_key) {
        return detail_key + ": " + String(this.state.system[detail_key]);
      }.bind(this));

      let table_data = this.generate_table_data();
      let cpu_labels = [];
      let cpu_data   = [];
      let cpu_title = "CPU Utilization";

      for(var cpu of table_data)
      {
        cpu_labels.push(cpu.logical_cpu);
        cpu_data.push(cpu.interval_utilization);
      }

      return (
        <>
          <div className="container">
            <div><StevesBarGraph title={cpu_title} labels={cpu_labels} data={cpu_data} max_y={1}/></div>
            <div><StevesPieGraph labels={mem_labels} data={mem_data} title={mem_title} /></div>
            <div><DetailsReadout details={details} /></div>
          </div>
          <div className="container">
            <div><StevesStreamingGraph data_point={context_data} label={context_label} title={context_title} max_data_points={5}/></div>
            <div><StevesStreamingGraph data_point={interrupts_data} label={interrupts_label} title={interrupts_title} max_data_points={5}/></div>
          </div>
          <StevesTable table_data={table_data}/>
        </>
      );
    }
  }

  build_network_page()
  {
    console.log(this.time_of_last_data);
    if(this.state.net_tcp != null && this.state.current_button == "Network")
      return( <NetworkView 
        net_metrics={this.state.net_metrics}
        net_metrics_rates={this.state.net_metrics_rates}
        net_tcp={this.state.net_tcp}
        net_udp={this.state.net_udp}
        net_nics={this.state.net_nics}
        net_nics_rates={this.state.net_nics_rates}
        filter_text={this.state.filter_text}
        timestamp={this.state.time_of_last_data}
      /> );
  }

  render() {
    return (
      <div>
        { this.state.buttons.map(function(button_data) {
          return (
            <button onClick={this.handleChildClick.bind(this, button_data.name)}
               className={button_data.selected ? "selected" : ""}>{button_data.name}</button>
          )
        }.bind(this)) }

        <input
          onKeyPress={this.handleFilterTextEnter.bind(this)} onChange={this.handleFilterTextChange.bind(this)} placeholder="Filter string" type="text"
        />
          
        {this.build_procs_page()}
        {this.build_disks_page()}
        {this.build_system_page()}
        {this.build_network_page()}
      </div>
    );
  }
}





export{
  NewApp
};