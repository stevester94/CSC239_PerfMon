import React, { Component, TextInput } from 'react';
import StevesTable from "./StevesTable.js"
import DetailsReadout from "./DetailsReadout.js"
import StevesBarGraph from "./StevesBarGraph.js"
import StevesPieGraph from "./StevesPieGraph.js"
import './App.css';
import 'react-table/react-table.css'
// import { throws } from 'assert';
import StevesStreamingGraph from "./StevesStreamingGraph.js"


const { ipcRenderer } = window.require('electron');

class NewApp extends Component {
  state = {
    procs: null,
    disks: null,
    cpus: null,
    system: null,
    network: {jej: "kek"},
    buttons: [
      {name: "Processes"},
      {name: "Disks"},
      {name: "CPUs"},
      {name: "System"},
      {name: "Network"}
    ],
    current_button: "Processes",
    filter_text: ""
  };

  constructor()
  {
    super();

    // In renderer process (web page).
    this.num_received = 0;

    // The state of this class will hold the raw objects that are sent from the distributor
    // Further processing will occur on demand when feeding consumers
    // State is only truely updated for the currently selected button
    // Other states are updated, but not through the actual setState, so render is not fired needlessly
    // Message handlers
    ipcRenderer.on('msg_procs', function(event, arg) {
      console.log("Renderer received following msg_id: " + "msg_procs");
      console.log("Current button " + this.state.current_button);
      console.log(this);
      this.num_received++;
      if(this.state.current_button === "Processes")
      {
        console.log("Setting procs state");
        this.setState(prevState =>({
          procs: arg
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
          disks: arg
        }));
      }
      else
      {
        this.state.disks = arg;
      }
    }.bind(this));

    ipcRenderer.on('msg_cpus', function(event, arg) {
      console.log("Renderer received following msg_id: " + "msg_cpus");
      if(this.state.current_button === "CPUs")
      {
        this.setState(prevState =>({
          cpus: arg
        }));
      }
      else
      {
        this.state.cpus = arg;
      }
    }.bind(this));

    ipcRenderer.on('msg_system', function(event, arg) {
      console.log("Renderer received following msg_id: " + "msg_system");
      if(this.state.current_button === "System")
      {
        this.setState(prevState =>({
          system: arg
        }));
      }
      else
      {
        this.state.cpus = arg;
      }
    }.bind(this));

    ipcRenderer.on('msg_net', (event, arg) => {
      console.log("Renderer received following msg_id: " + "msg_net");
      console.log("Ignoring for now");
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
    console.log("Child clicked: " + String(childData));
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
    if(this.state.current_button === "CPUs")
    {
      if(this.state.cpus != null)
      {
        table_data = this.convert_dict_to_array(this.state.cpus, "logical_cpu");
        table_data = this.filter_array_based_on_keys(table_data);
      }
    }
    if(this.state.current_button === "System")
    {
      
      table_data = [this.state.system]; // Make it an array of 1 to fit the model
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
        label={this.num_received} 
        data_point={num_procs} 
        max_data_points={5}/>;

      // Data table
      let table = <StevesTable table_data={table_data}/>;

      return (
        <>
          <div className="container">
            <div>{procs_graph}</div>
            <div><DetailsReadout details={["jejjjjjjjjjjjjj", "kek"]}/></div>
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
      let num_disks = Object.keys(this.state.disks).length
      let table_data = this.generate_table_data();
      
      // Disk usage bar graph
      let title = "Disk Usage"
      let data = [];
      let labels = [];
      for(var disk of table_data)
      {
        labels.push(disk.disk_name);
        data.push(disk.sectors_written);
      }

      let disks_graph = <StevesBarGraph title={title} labels={labels} data={data}/>
      components.push(disks_graph);

      // Data table
      let table = <StevesTable table_data={table_data}/>;
      components.push(table);

      return (
        <>
          <div className="container">
            <div>{disks_graph}</div>
            <div><DetailsReadout details={["jejjjjjjjjjjjjj", "kek"]}/></div>
          </div>
          <div>{table}</div>
        </>
      );
    }

    return;
  }

  build_system_page()
  {
    // return <StevesPieGraph />
  }

  render() {
    let streaming_graph;
    let table;
    let table_data = this.generate_table_data();
    // if(this.state.procs != null)
    // {
    //   streaming_graph = <StevesStreamingGraph
    //                     title="Num filtered data"
    //                     label={this.num_received} 
    //                     data_point={table_data.length} 
    //                     max_data_points={5}/>;
    //   table           = <StevesTable table_data={table_data}/>;
    // }

    return (
      <div>
        { this.state.buttons.map(function(button_data) {
          return <button onClick={this.handleChildClick.bind(this, button_data.name)}>{button_data.name}</button>
        }.bind(this)) }

        <input
          onKeyPress={this.handleFilterTextEnter.bind(this)} onChange={this.handleFilterTextChange.bind(this)} placeholder="Filter string" type="text"
        />
          
        {this.build_procs_page()}
        {this.build_disks_page()}
        {this.build_system_page()}
      </div>
    );
  }
}





export{
  NewApp
};