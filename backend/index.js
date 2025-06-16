const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');


const app = express();
app.use(cors()); // pour autoriser les requêtes depuis le frontend

app.get('/run-python', (req, res) => {
  const python = spawn('python3', ['script.py', 'arg1', 'arg2']);

  let output = '';
  python.stdout.on('data', (data) => {
    output += data.toString();
  });

  python.stderr.on('data', (data) => {
    console.error(`Erreur Python : ${data}`);
  });

  python.on('close', (code) => {
    res.send({ output, code });
  });
});

app.listen(3001, () => {
  console.log('Backend en écoute sur http://localhost:3001');
});
