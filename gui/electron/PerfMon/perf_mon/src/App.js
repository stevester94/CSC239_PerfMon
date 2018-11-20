import React, { Component } from 'react';
import StevesTable from "./StevesTable.js"

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
    buttons: [
      {name: "Processes"},
      {name: "Disks"},
      {name: "CPUs"},
      {name: "System XDDD"}
    ],
    current_button: "Processes"
  };

  constructor()
  {
    super();
    // In renderer process (web page).

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
  }

  // I know, I'm mixing python terms here. dict == object with a shit ton of keys
  convert_dict_to_array(dict)
  {
    let array = [];
    for(var entry of Object.keys(dict))
    {
      dict[entry].name = entry;
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

  render() {
    console.log(this.current_button);


    return (

      <div>
        { this.state.buttons.map(function(button_data) {
          console.log(button_data);
          return <button onClick={this.handleChildClick.bind(null, button_data.name)}>{button_data.name}</button>
        }.bind(this)) }

        <StevesTable table_data={this.state.procs}/>
      </div>
    );
  }
}





export{
  NewApp
};