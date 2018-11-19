import React, { Component } from 'react';
import StevesTable from "./StevesTable.js"

import './App.css';
import 'react-table/react-table.css'
import { throws } from 'assert';

const { ipcRenderer } = window.require('electron');



class NewApp extends Component {
  state = {
    procs : null
  };

  constructor()
  {
    super();
    // In renderer process (web page).


    ipcRenderer.on('msg_procs', (event, arg) => {
      console.log("Renderer received following msg_id: " + "msg_procs");
      this.setState(prevState =>({
        procs: this.convert_dict_to_array(arg)
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

  render() {
    console.log(this.state.procs);

    return (
      <div>
        <StevesTable table_data={this.state.procs}/>
      </div>
    );
  }
}





export{
  NewApp
};