import React, { Component } from 'react';
import StevesTable from "./StevesTable.js"
import StevesStreamingGraph from "./StevesStreamingGraph.js"

import './App.css';
import 'react-table/react-table.css'
// import { throws } from 'assert';

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
    current_button: "Processes"
  };

  constructor()
  {
    super();
    // In renderer process (web page).

    // The state of this class will hold the raw objects that are sent from the distributor
    // Further processing will occur on demand when feeding consumers
    // Message handlers
    ipcRenderer.on('msg_procs', (event, arg) => {
      console.log("Renderer received following msg_id: " + "msg_procs");
      this.setState(prevState =>({
        procs: arg
      }));
    });

    ipcRenderer.on('msg_disks', (event, arg) => {
      console.log("Renderer received following msg_id: " + "msg_disks");
      this.setState(prevState =>({
        disks: arg
      }));
    });

    ipcRenderer.on('msg_cpus', (event, arg) => {
      console.log("Renderer received following msg_id: " + "msg_cpus");
      this.setState(prevState =>({
        cpus: arg
      }));
    });

    ipcRenderer.on('msg_system', (event, arg) => {
      console.log("Renderer received following msg_id: " + "msg_system");
      this.setState(prevState =>({
        system: arg
      }));
    });

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
      current_button: childData
    }));
  }

  // Select the correct table data and transmute to the generic format that
  // StevesTable can ingest. If there is no data, returns null
  generate_table_data()
  {
    let table_data = null;

    if(this.state.current_button === "Processes")
    {
      if(this.state.procs != null)
        table_data = this.convert_dict_to_array(this.state.procs, "pid");
    }
    if(this.state.current_button === "Disks")
    {
      if(this.state.disks != null)
        table_data = this.convert_dict_to_array(this.state.disks, "disk_name");
    }
    if(this.state.current_button === "CPUs")
    {
      if(this.state.cpus != null)
        table_data = this.convert_dict_to_array(this.state.cpus, "logical_cpu");
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

  render() {
    return (

      <div>
        { this.state.buttons.map(function(button_data) {
          return <button onClick={this.handleChildClick.bind(this, button_data.name)}>{button_data.name}</button>
        }.bind(this)) }
        <StevesStreamingGraph />
        <StevesTable table_data={this.generate_table_data()}/>
      </div>
    );
  }
}





export{
  NewApp
};