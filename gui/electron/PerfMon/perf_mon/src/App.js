import React, { Component } from 'react';
import './App.css';

class NewApp extends Component {
  constructor()
  {
    super();
    // In renderer process (web page).
    const { ipcRenderer } = window.require('electron');
    console.log(ipcRenderer.sendSync('synchronous-message', 'Hello main process!'))

    // ipcRenderer.on('asynchronous-reply', (event, arg) => {
    //   console.log("Renderer asynch received:" + arg) // prints "pong"
    // })
    // ipcRenderer.send('asynchronous-message', 'From asynch renderer')
  }
  render() {
    return (
      <div className="App">
        <p>
          Chedd would love this!!<br/>
          <StevesApp my_state="jej"/>
        </p>
      </div>
    );
  }
}

class StevesApp extends Component {
  render() {
    return (
      <div className="Steves_App">
        This is my app!<br/>
        My state: {this.props.my_state}
      </div>
    );
  }
}

export {
  NewApp,
  StevesApp
}
