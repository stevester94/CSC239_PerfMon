import React, { Component } from 'react';
import StevesTable from "./StevesTable.js"

import './App.css';
import 'react-table/react-table.css'

// const { ipcRenderer } = window.require('electron');



class NewApp extends Component {


  constructor()
  {
    super();
    // In renderer process (web page).

    ipcRenderer.on('procs-json-message', (event, arg) => {
      console.log("Renderer received following from Main process:");
      console.log(arg);
      this.setState(prevState =>({
        procs: JSON.stringify(arg)
      }));
    });
  }

  render() {
    return (
      <div>
        <StevesTable />
      </div>
    );
  }
}





export{
  NewApp
};