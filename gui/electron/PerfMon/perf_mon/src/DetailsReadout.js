import React, { Component } from 'react';

class DetailsReadout extends Component {
    render() {
        const {details} = this.props;

        return (
            <ul className="DetailsReadout">
                { details.map(function(detail) {
                    return <li>{detail}</li>
                }) }
            </ul>
        );
    }


}


export default DetailsReadout;