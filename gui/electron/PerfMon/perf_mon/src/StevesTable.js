import React, { Component } from 'react';
import ReactTable from "react-table";

import 'react-table/react-table.css'

class StevesTable extends Component {
    // props = {
    //   table_data : null,
    // };
  
    get_column_representation(single_entry)
    {
      let keys = Object.keys(single_entry);
      let column_array = []
      for(var key of keys)
      {
        column_array.push({
          Header: key,
          accessor: key
        });
      }
      return column_array;
    }
  
    constructor()
    {
      console.log("StevesTable constructing!");
      super();  
    }
  
    render() {
      console.log("StevesTable rendering!");
      const { table_data } = this.props;
      if(table_data == null)
      {
        return (<div>no data</div>);
      }
      return (
        <div>
          <ReactTable
            data={table_data}
            columns={this.get_column_representation(table_data[0])}
            defaultPageSize={table_data.length}
            className="-striped -highlight"
          />
        </div>
      );
    }
  }

export default StevesTable;