import React, { Component } from 'react';
import { Line } from 'react-chartjs-2';
import 'chartjs-plugin-streaming';
import './App.css';

class StevesStreamingGraph extends Component {

  render() {
    return (
      <Line
        data={{
          datasets: [{
            data: []
          }, {
            data: []
          }]
        }}

        options={{
          scales: {
            xAxes: [{
              type: 'realtime'
            }]
          }
        }}
      />
    );
  }
}

export default StevesStreamingGraph;
