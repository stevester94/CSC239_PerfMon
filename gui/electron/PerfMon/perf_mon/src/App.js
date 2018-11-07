import React, { Component } from 'react';
import './App.css';

const { ipcRenderer } = window.require('electron');


class NewApp extends Component {
  state = {
    last_message : "Initial Message"
  };

  constructor()
  {
    super();
    // In renderer process (web page).

    ipcRenderer.on('main-to-renderer-message', (event, arg) => {
      console.log("Renderer received following from Main process:");
      console.log(arg);
      this.setState(prevState =>({
        last_message: String(arg)
      }));
    });
  }

  render() {
    return (
      <div className="App">
        <p>
          Chedd would love this!!<br/>
          Last message received from main: {this.state.last_message}
          <MessageWindow  message={this.state.last_message}/>
          <SendToMain/>
        </p>
      </div>
    );
  }
}



// Displays the messages that are passed from the parent
class MessageWindow extends React.Component {
  constructor(props) {
    super(props);

    console.log("MessageWindow props:");
    console.log(props);

    // I have no clue why this is necessary
    this.getMessage = this.getMessage.bind(this);

    this.numRenders = 0;
  }

  // componentWillReceiveProps(props) {
  //   this.setState({ message: props.message});
  // }

  getMessage() {
    if(this.props) {
      console.log("Returning: " + this.props.message);
      return this.props.message;
    }
  }

  render() {
    console.log("MessageWindow rendering");
    let carnality_indicator = null;
    if(this.numRenders % 2)
    {
      carnality_indicator = <OddNum />
    }
    else
    {
      carnality_indicator = <EvenNum />
    }
    this.numRenders++;

    return (
    <div>
      Last Message Received: {this.getMessage()}
      {carnality_indicator}  
    </div>
    )}
}




class SendToMain extends React.Component {
  constructor(props) {
    super(props);
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    ipcRenderer.send('renderer-to-main-message', 'Requesting message');
    console.log("Renderer requested message...");
  }

  render() {
    console.log("SendToMain rendering");
    return (
      <button onClick={this.handleClick}> Request Message</button>
    )
  }
}

class OddNum extends React.Component {
  render() {
    return (
      <strong>ODD NUM OF STUFF</strong>
    );
  }
}

class EvenNum extends React.Component {
  render() {
    return (
      <strong>EVEN NUM OF STUFF</strong>
    );
  }
}

export {
  NewApp
}





/*
 * BONEYARD
 */

class Toggle extends React.Component {
  constructor(props) {
    super(props);
    console.log("Toggle is initializing");
    console.log(props);

    this.state = {isToggleOn: true};

    // This binding is necessary to make `this` work in the callback
    this.handleClick = this.handleClick.bind(this);
  }

  handleClick() {
    this.setState(prevState => ({
      isToggleOn: !prevState.isToggleOn
    }));
  }

  render() {
    return (
      <button onClick={this.handleClick}>
        {this.state.isToggleOn ? 'ON' : 'OFF'}
      </button>
    );
  }
}

class StevesApp extends Component {
  render() {
    return (
      <div className="Steves_App">
        This is my app!<br/>
        My state: {this.props.my_state}<br/>
      </div>
    );
  }
}