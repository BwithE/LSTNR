const fs = require('fs');
const express = require('express');
const http = require('http');
const net = require('net');
const socketIo = require('socket.io');
const bodyParser = require('body-parser');
const { exec } = require('child_process');
const { promisify } = require('util');

const app = express();
const server = http.createServer(app);
const io = socketIo(server);

app.use(bodyParser.json());
app.use(express.static('public'));

let activePorts = {};
let servers = {};
let eventHistory = [];


const historyFile = 'history.txt';
if (fs.existsSync(historyFile)) {
    const data = fs.readFileSync(historyFile, 'utf8');
    eventHistory = data.split('\n').filter(Boolean);
}

function saveHistoryToFile() {
    fs.writeFileSync(historyFile, eventHistory.join('\n'));
}

app.post('/set-port', (req, res) => {
    const { port } = req.body;
    if (activePorts[port]) {
        return res.status(400).send('Port already in use');
    }

    const tcpServer = net.createServer((socket) => {
        console.log(`New connection on port ${port}`);
        socket.write('Welcome to the Death Star\n');
        socket.on('data', (data) => {
            console.log(`Data received on port ${port}: ${data}`);
        });
    });

    tcpServer.listen(port, () => {
        console.log(`Listening on port ${port}`);
        activePorts[port] = tcpServer;
        servers[port] = tcpServer;
        io.emit('new-port', port);
        const message = `New port listening on ${port}`;
        eventHistory.push(message);
        saveHistoryToFile();
        io.emit('history-event', message);
        res.status(200).end();
    });

    tcpServer.on('error', (err) => {
        console.error(`Error on port ${port}: ${err.message}`);
        res.status(500).send(`Error listening on port ${port}`);
    });
});

app.post('/send-command', (req, res) => {
    const { command } = req.body;

    console.log(`Executing command: ${command}`);
    io.emit('send-command', command);
    const message = `Sent command: ${command}`;
    eventHistory.push(message);
    saveHistoryToFile();
    io.emit('history-event', message);

  
    const execCommand = `xterm -fa "DejaVu Sans Mono" -fs 14 -sl 10000 -geometry 100x20+100+100 -e "${command}"`;
    exec(execCommand, (error, stdout, stderr) => {
        if (error) {
            console.error(`Error executing command: ${error.message}`);
            const errorMessage = `Error executing command: ${error.message}`;
            eventHistory.push(errorMessage);
            saveHistoryToFile();
            io.emit('history-event', errorMessage);
            return res.status(500).send(errorMessage);
        }
        if (stderr) {
            console.error(`stderr: ${stderr}`);
            const stderrMessage = `stderr: ${stderr}`;
            eventHistory.push(stderrMessage);
            saveHistoryToFile();
            io.emit('history-event', stderrMessage);
            return res.status(500).send(stderrMessage);
        }
        console.log(`stdout: ${stdout}`);
        res.status(200).end();
    });
});

app.post('/delete-port', async (req, res) => {
    const { port } = req.body;

    if (!activePorts[port]) {
        return res.status(400).send('Port not found');
    }


    try {
        await promisify(activePorts[port].close.bind(activePorts[port]))();
        delete activePorts[port];
        delete servers[port];
        io.emit('delete-port', port);
        const message = `Stopped listening on port ${port}`;
        eventHistory.push(message);
        saveHistoryToFile();
        io.emit('history-event', message);
        res.json({ message: `Stopped listening on port ${port}` });
    } catch (error) {
        console.error(`Error stopping port ${port}: ${error.message}`);
        res.status(500).send(`Error stopping port ${port}`);
    }
});

io.on('connection', (socket) => {
    console.log('Client connected');
    socket.on('disconnect', () => {
        console.log('Client disconnected');
    });

    socket.emit('history-event', 'Connected to Death Star');
    Object.keys(activePorts).forEach(port => {
        socket.emit('new-port', port);
    });
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`Death Star running on port ${PORT}`);
});
