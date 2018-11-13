import React, { Component } from 'react';
import './App.css';

const { ipcRenderer } = window.require('electron');


class NewApp extends Component {
  state = {
    procs : null
  };

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
      <div className="App">
        <p>
          Chedd would love this!!<br/>
          Last message received from main: {this.state.procs}
        </p>
      </div>
    );
  }
}

export{
  NewApp
};