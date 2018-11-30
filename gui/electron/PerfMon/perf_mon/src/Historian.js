import React, { Component } from 'react';
import { runInThisContext } from 'vm';
const { ipcRenderer } = window.require('electron');


class Historian extends Component {
    state = {
        keys: [],
        current_data: {}
    }

    constructor()
    {
        super();
        console.log("Historian constructing");

        this.request_all_keys();
    }

    // msg: historian-request-all
    // response: historian-response-all
    request_all_history(key)
    {

    }

    // msg: historian-request-keys
    // response: historian-response-keys
    request_all_keys()
    {
        console.log("Requesting keys");
        let response = ipcRenderer.send('historian-request-keys', "");

        ipcRenderer.once('historian-response-keys', (event, arg) => {
            console.log("Renderer asynch received:");
            console.log(arg);
        })
        this.state.current_data = response;
    }

    // msg: historian-request-range
    // response: historian-response-range
    request_history(key, start_epoch, end_epoch)
    {

    }

    render() {
        return (
            <div>JEJ: {this.state.current_data}</div>
        );
    }
}



export default Historian;