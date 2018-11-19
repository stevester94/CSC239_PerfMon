const electron = require('electron');
const fs  = require("fs");

// Module to control application life.
const app = electron.app;
// Module to create native browser window.
const BrowserWindow = electron.BrowserWindow;

const path = require('path');
const url = require('url');

let g_message_counter = 0;

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let mainWindow;

// IPC testing to the render window
const {ipcMain} = require('electron')
// ipcMain.on('asynchronous-message', (event, arg) => {
//   console.log("Main received: " + arg) // prints "ping"
//   event.sender.send('asynchronous-reply', 'Hello from main process')
// })


let sample_data = fs.readFileSync(path.join(__dirname, '/../test_data/sample_procs.json'), "utf8");
let procs_json   = JSON.parse(sample_data);


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
    mainWindow = new BrowserWindow({width: 800, height: 600});

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
