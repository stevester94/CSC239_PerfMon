const electron = require('electron');
const fs  = require("fs");

// Module to control application life.
const app = electron.app;
// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow;

const path = require('path');
const url = require('url');

const MongoClient = require('mongodb').MongoClient;
const assert = require('assert');

const { ipcMain } = require('electron')
var zlib = require('zlib');





/********************
 * Interceptor Shit *
 ********************/
function myFunc() {
    fs.readFile('/tmp/data', 'utf8', function(err, contents) {
        console.log("Contents: " + contents);
        if(contents != null)
            mainWindow.webContents.send("msg_interceptor", contents);
    });

    setTimeout(myFunc, 1500);

}

setTimeout(myFunc, 1500);


/******************
 * Historian shit *
 ******************/
// Database Name
const dbName = 'historic_db';
let history;
// Create a new MongoClient
const client = new MongoClient('mongodb://localhost:27017');

// The keys we pass to the historian are the nice display keys,
// need to translate them back when we query the database
function translate_historian_keys_to_mongo_keys(historian_keys)
{
    translated_keys = [];

    for(let key of historian_keys)
    {
        if(key === "Disks")
        {
            translated_keys.push("msg_disks");
        }
        else if(key === "CPUs")
        {
            translated_keys.push("msg_cpus");
        }
        else if(key === "NIC_metrics")
        {
            translated_keys.push("msg_net");
            translated_keys.push("nic_metrics");
        }
        else if(key === "NIC_metrics_rates")
        {
            translated_keys.push("msg_net");
            translated_keys.push("nic_metrics_rates")
        }
        else if(key == "System")
        {
            translated_keys.push("msg_system");
        }
        else
        {
            translated_keys.push(key);
        }
    }

    return translated_keys;
}


// msg: historian-request-keys
// response: historian-response-keys
// msg: historian-request-range
// response: historian-response-range
function serve_historian_request_keys(callback)
{
    client.connect(function (err) {
        function get_first_member_of_object(obj) {
            return obj[Object.keys(obj)[0]];
        }

        assert.equal(null, err);
        console.log("Connected successfully to server");

        history = client.db(dbName).collection("history");

        history.find({}).toArray(function (err, docs) {
            assert.equal(err, null);
            doc = docs[0];
            console.log("First record found");
            // console.log(doc);

            // Procs and specific sockets are going to be a bitch, probably won't do them...

            // Use this as a template
            // for (var _main_name of Object.keys(doc.__msg_name__)) {
            //     source = [];
            //     fields = [];

            //     source.push(__msg_name__);
            //     source.push(_main_name);
            //     for (var field of Object.keys(doc.__msg_name__[_main_name])) {
            //         fields.push(field);
            //     }
            //     keys._dict_name_.push({ source: source, fields: fields, main_name: _main_name });
            // }

            let keys = {};

            // Disks
            keys.Disks = {};
            for (var disk of Object.keys(doc.msg_disks)) {

                keys.Disks[disk] = {};
                for (var disk_key of Object.keys(doc.msg_disks[disk])) {
                    keys.Disks[disk][disk_key] = null;
                }
            }

            // CPUs
            keys.CPUs = {};
            for (var _main_name of Object.keys(doc.msg_cpus)) {

                keys.CPUs[_main_name] = {};
                for (var field of Object.keys(doc.msg_cpus[_main_name])) {
                    keys.CPUs[_main_name][field] = null;
                }
            }

            // NIC_metrics
            keys.NIC_metrics = {};
            for (var _main_name of Object.keys(doc.msg_net.nic_metrics)) {

                keys.NIC_metrics[_main_name] = {}
                for (var field of Object.keys(doc.msg_net.nic_metrics[_main_name])) {
                    keys.NIC_metrics[_main_name][field] = null;
                }
            }

            keys.NIC_metrics_rates = {};
            for (var _main_name of Object.keys(doc.msg_net.nic_metrics_rates)) {

                keys.NIC_metrics_rates[_main_name] = {};
                for (var field of Object.keys(doc.msg_net.nic_metrics_rates[_main_name])) {
                    keys.NIC_metrics_rates[_main_name][field] = null;
                }
            }

            // System metrics
            keys.System = {};
            for (var field of Object.keys(doc.msg_system)) {
                keys.System[field] = null;
            }

            // console.log(Object.keys(get_first_member_of_object(doc.msg_disks)));
            // console.log(Object.keys(get_first_member_of_object(doc.msg_cpus)));
            // console.log(Object.keys(doc.msg_system));
            // console.log(Object.keys(doc.msg_net.net_metric_rates));
            // console.log(Object.keys(doc.msg_net.net_metrics));
            // console.log(Object.keys(get_first_member_of_object(doc.msg_net.nic_metrics)));
            // console.log(Object.keys(get_first_member_of_object(doc.msg_net.nic_metrics_rates)));

            callback(keys);
        });

    });
}




ipcMain.on('historian-request-keys', (event, arg) => {
    console.log("Main received: historian-request-keys");

    serve_historian_request_keys((keys) => {
        event.sender.send('historian-response-keys', keys)
    });
});




// ipcMain.on('asynchronous-message', (event, arg) => {
//   console.log("Main received: " + arg) // prints "ping"
//   event.sender.send('asynchronous-reply', 'Hello from main process')
// })

// Use connect method to connect to the Server

// msg: historian-request-all
// response: historian-response-all
function serve_historian_request_all(keys, callback) {
    client.connect(function (err) {
        assert.equal(null, err);
        console.log("Connected successfully to server");

        history = client.db(dbName).collection("history");

        let projection_string = keys.join('.');
        console.log("Projection String");
        console.log(projection_string);

        let projection = { "_id": 0, "timestamp": 1};
        projection[projection_string] = 1;

        console.log(projection);

        history.find({}).project(projection).toArray(function (err, docs) {
            assert.equal(err, null);
            console.log("First doc found: ");
            console.log(docs[0]);

            let payload = [];
            for(var doc of docs)
            {
                let value = doc;
                for(var key of keys)
                {
                    value = value[key];
                }
                payload.push({timestamp: doc.timestamp, value: value})

            }
            callback(payload);
        });
    });
}

// serve_historian_request_all(["msg_cpus", "cpu", "interval_utilization"], console.log);
// app.quit();


ipcMain.on('historian-request-all', (event, arg) => {
    console.log("Main received: historian-request-all");

    mongo_keys = translate_historian_keys_to_mongo_keys(arg);
    console.log("mongo_keys" + String(mongo_keys));

    serve_historian_request_all(mongo_keys, (time_tagged_values) => {
        console.log("historian-response-all: ");
        console.log(time_tagged_values);

        event.sender.send('historian-response-all', time_tagged_values)
    });
});



// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow;




// UDP Listening 
var PORT = 9001;
var HOST = '0.0.0.0';

var dgram = require('dgram');
var server = dgram.createSocket('udp4');

server.on('listening', function () {
    var address = server.address();
    console.log('UDP Server listening on ' + address.address + ":" + address.port);
});

server.on('message', function (message, remote) {
    console.log(message.toString());
    // Have I mentioned I don't know what I'm doing?
    let inflated_message = zlib.inflateSync(new Buffer(message.toString(), 'base64')).toString();
    json_payload = JSON.parse(inflated_message);
    console.log("Message received, msg_id: " + json_payload.msg_id);
    mainWindow.webContents.send(json_payload.msg_id, json_payload.data);

});

server.bind(PORT, HOST);



function createWindow() {
    // Create the browser window.
    mainWindow = new BrowserWindow({width: 1275, height: 575});

    // mainWindow.webContents.on('did-finish-load', () => {
    //     mainWindow.webContents.send('procs-json-message', procs_json);
    // });

    // If we have that url set it means we are in dev mode, otherwise we look at the files that webpack has generated for us (prod mode)
    const startUrl = process.env.ELECTRON_START_URL || url.format({
            pathname: path.join(__dirname, '/../build/index.html'),
            protocol: 'file:',
            slashes: true
    });
    // and load the index.html of the app.
    mainWindow.loadURL(startUrl);

    // Open the DevTools.
    // mainWindow.webContents.openDevTools();

    // Emitted when the window is closed.
    mainWindow.on('closed', function () {
        // Dereference the window object, usually you would store windows
        // in an array if your app supports multi windows, this is the time
        // when you should delete the corresponding element.
        mainWindow = null
    })
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);

// Quit when all windows are closed.
app.on('window-all-closed', function () {
    // On OS X it is common for applications and their menu bar
    // to stay active until the user quits explicitly with Cmd + Q
    if (process.platform !== 'darwin') {
        app.quit()
    }
});

app.on('activate', function () {
    // On OS X it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (mainWindow === null) {
        createWindow()
    }
});

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
