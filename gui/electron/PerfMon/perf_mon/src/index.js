import React from 'react';
import ReactDOM from 'react-dom';
import {NewApp, StevesApp} from './App';
import * as serviceWorker from './serviceWorker';

ReactDOM.render(<NewApp />, document.getElementById('root'));
ReactDOM.render(<StevesApp />, document.getElementById('steve-root'));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA
serviceWorker.unregister();
