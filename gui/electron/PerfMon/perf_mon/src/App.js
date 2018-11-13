import React, { Component } from 'react';
import ReactTable from "react-table";

import './App.css';
import 'react-table/react-table.css'

// const { ipcRenderer } = window.require('electron');


class NewApp extends Component {
  state = {
    procs : null,
    intervalID : null
  };

  gen_procs() {
    let ret_array = []
    for(let i = 0; i < 5000; i++)
    {
      ret_array.push(
        {
          pid: String(Math.floor(Math.random() * 10000)),
          command: "Python",
          UID: "1"
        }
      );
    }

    return ret_array;
  }

  updateState()
  {
    console.log("Updating");
    this.setState(prevState =>({
      procs: this.gen_procs()
    }));
  }

  constructor()
  {
    super();
    // In renderer process (web page).

    this.updateState = this.updateState.bind(this);
    this.state.intervalID = setInterval(this.updateState, 5000);

    this.state.procs = this.gen_procs();

    // ipcRenderer.on('procs-json-message', (event, arg) => {
    //   console.log("Renderer received following from Main process:");
    //   console.log(arg);
    //   this.setState(prevState =>({
    //     procs: JSON.stringify(arg)
    //   }));
    // });
  }

  render() {
    const { procs } = this.state;
    return (
      <div>
        <ReactTable
          data={procs}
          columns={[
            {
              // Header: "Stuff",
              columns: [
                {
                  Header: "PID",
                  accessor: "pid"
                },
                {
                  Header: "command",
                  accessor: "command"
                }
              ]
            }
          ]}
          defaultPageSize={5000}
          className="-striped -highlight"
        />
      </div>
    );
  }
}





export{
  NewApp
};