import React, { Component } from 'react';
import { runInThisContext } from 'vm';
const { ipcRenderer } = window.require('electron');


class Historian extends Component {
    state = {
        keys: null,
        current_data: {},
        current_source: [] // This is just going to be indeces
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
            console.log("Received historian-response-keys");
            console.log(arg);

            this.setState(prevState => ({
                keys: arg
            }));
        })
    }

    // msg: historian-request-range
    // response: historian-response-range
    request_history(key, start_epoch, end_epoch)
    {

    }

    selectChangeHandler(arg)
    {
        console.log("Selector called: " + String(arg));
    }

    build_selectors()
    {
        if(this.state.keys == null)
            return;
        
        let selectors = [];
        // This is the special case where nothing has been selected yet, 
        // Therefore just 
        if(this.state.current_source.length >= 0)
        {
            let selector =
                <select onChange={this.selectChangeHandler.bind(this)}>
                    {Object.keys(this.state.keys).map(function (selection_name) {
                        return <option value={selection_name}>{selection_name}</option>
                    })}
                </select>
            selectors.push(selector);
        }


        return selectors;
    }

    render() {
        return (
            <div>JEJ:
                {this.build_selectors()}
            </div>
        );
    }
}



export default Historian;