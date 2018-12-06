import React, { Component } from 'react';
const { ipcRenderer } = window.require('electron');




class Interceptor extends Component {
    state = {
        interceptor_buffer: ""
    }
    constructor()
    {
        super();

        ipcRenderer.on('msg_interceptor', function (event, arg) {
            console.log("Interceptor received following: " + arg);
            let new_buffer = this.state.interceptor_buffer += arg;
            this.setState(prevState => ({
                interceptor_buffer: new_buffer
            }));
        }.bind(this));
    }

    render()
    {
        return (
            <div>{this.state.interceptor_buffer}</div>
        );
    }
}



export default Interceptor;