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

/******************
 * Historian shit *
 ******************/
// Database Name
const dbName = 'historic_db';
let history;
// Create a new MongoClient
const client = new MongoClient('mongodb://localhost:27017');


// msg: historian-request-all
// response: historian-response-all
// msg: historian-request-keys
// response: historian-response-keys
// msg: historian-request-range
// response: historian-response-range

ipcMain.on('historian-request-keys', (event, arg) => {
    console.log("Main received: historian-request-keys");

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
            keys.Disks = [];
            for (var disk of Object.keys(doc.msg_disks)) {
                source = [];
                fields = [];
                source.push("msg_disks");
                source.push(disk);
                for (var disk_key of Object.keys(doc.msg_disks[disk])) {
                    fields.push(disk_key);
                }
                keys.Disks.push({ source: source, fields: fields, main_name: disk });
            }

            // CPUs
            keys.CPUs = [];
            for (var _main_name of Object.keys(doc.msg_cpus)) {
                source = [];
                fields = [];

                source.push("msg_cpus");
                source.push(_main_name);
                for (var field of Object.keys(doc.msg_cpus[_main_name])) {
                    fields.push(field);
                }
                keys.CPUs.push({ source: source, fields: fields, main_name: _main_name });
            }

            keys.NIC_metrics = [];
            for (var _main_name of Object.keys(doc.msg_net.nic_metrics)) {
                source = [];
                fields = [];

                source.push("msg_net");
                source.push("nic_metrics");
                source.push(_main_name);
                for (var field of Object.keys(doc.msg_net.nic_metrics[_main_name])) {
                    fields.push(field);
                }
                keys.NIC_metrics.push({ source: source, fields: fields, main_name: _main_name });
            }

            keys.NIC_metrics_rates = [];
            for (var _main_name of Object.keys(doc.msg_net.nic_metrics_rates)) {
                source = [];
                fields = [];

                source.push("msg_net");
                source.push("nic_metrics_rates")
                source.push(_main_name);
                for (var field of Object.keys(doc.msg_net.nic_metrics_rates[_main_name])) {
                    fields.push(field);
                }
                keys.NIC_metrics_rates.push({ source: source, fields: fields, main_name: _main_name });
            }

            // console.log(Object.keys(get_first_member_of_object(doc.msg_disks)));
            // console.log(Object.keys(get_first_member_of_object(doc.msg_cpus)));
            // console.log(Object.keys(doc.msg_system));
            // console.log(Object.keys(doc.msg_net.net_metric_rates));
            // console.log(Object.keys(doc.msg_net.net_metrics));
            // console.log(Object.keys(get_first_member_of_object(doc.msg_net.nic_metrics)));
            // console.log(Object.keys(get_first_member_of_object(doc.msg_net.nic_metrics_rates)));

            event.sender.send('historian-response-keys', keys);


        });

        client.close();
    });
});

// ipcMain.on('asynchronous-message', (event, arg) => {
//   console.log("Main received: " + arg) // prints "ping"
//   event.sender.send('asynchronous-reply', 'Hello from main process')
// })

// Use connect method to connect to the Server





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
    json_payload = JSON.parse(message)
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
