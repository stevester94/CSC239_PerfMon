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
        console.log("Requesting all for key: ");
        console.log(key);
        ipcRenderer.send('historian-request-all', key);

        ipcRenderer.once('historian-response-all', (event, arg) => {
            console.log("Received historian-response-all");
            console.log(arg);

            this.setState(prevState => ({
                current_data: arg
            }));
        })
    }

    // msg: historian-request-keys
    // response: historian-response-keys
    request_all_keys()
    {
        console.log("Requesting keys");
        ipcRenderer.send('historian-request-keys', "");

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

    selectChangeHandler(is_final_field, source_index, arg)
    {
        console.log("Selector called: " + arg.target.value);
        if(source_index == this.state.current_source.length) // Regular case where we just tack it on
        {
            this.state.current_source.push(arg.target.value);
        }
        else if(source_index < this.state.current_source.length) 
        {
            /* This is the case where we have gone somewhere back in the chain and changed our
             * mind as to what we want to see.
             * Could be as simple as change the last field, or have to completely blow away everything in front of it
             */
            this.state.current_source[source_index] = arg.target.value;
            this.state.current_source = this.state.current_source.slice(0, source_index+1); // End index is non-inclusive so add 1
        }

        if(is_final_field)
        {
            console.log("Final field selected, total source array:");
            console.log(this.state.current_source);

            this.request_all_history(this.state.current_source);
        }
        else
        {
            // Just update the chain, nothing else to do
            this.setState(prevState => ({}));
        }
    }

    build_selectors()
    {
        if(this.state.keys == null)
            return;
        
        let selectors = [];
        
        for(let i = 0; i <= this.state.current_source.length; i++)
        {
            // This for loop is to progress through the hierarchy of keys that are defined
            // in the keys state object for our current depth.
            let current_keys = this.state.keys;
            for(let j = 0; j < i; j++)
            {
                current_keys = current_keys[this.state.current_source[j]]
            }

            if(current_keys == null)
            {
                console.log("Reached base case");
                return selectors;
            }

            // Check to see if this is the final layer, if so we need to indicate as much to the selectChangeHandler that selecting this
            // guy will mean we need to make a request to the backend.
            // Not great since we only check the first one (if the hierarchy was not balanced this would not work)
            let is_this_the_final_layer = false;
            if(current_keys[Object.keys(current_keys)[0]] == null)
            {
                is_this_the_final_layer = true;
            }

            let selector =
                <select onChange={this.selectChangeHandler.bind(this, is_this_the_final_layer, i)}>
                    <option value="" disabled selected>Select field</option>
                    {Object.keys(current_keys).map(function (selection_name) {
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