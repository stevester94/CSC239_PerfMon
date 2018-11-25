import React, { Component } from 'react';

class DetailsReadout extends Component {
    render() {
        const {details, title} = this.props;

        return (
            <ul className="DetailsReadout">{title}
                { details.map(function(detail) {
                    return <li>{detail}</li>
                }) }
            </ul>
        );
    }


}


export default DetailsReadout;