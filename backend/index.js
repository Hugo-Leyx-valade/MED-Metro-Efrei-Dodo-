const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');

const app = express();
app.use(cors());

app.get('/run-python', (req, res) => {
  const python = spawn('python', ['script.py', 'arg1', 'arg2']); // ou 'python3'

  let output = '';
  let errorOutput = '';

  python.stdout.on('data', (data) => {
    output += data.toString();
  });

  python.stderr.on('data', (data) => {
    errorOutput += data.toString();
    console.error(`Erreur Python : ${data}`);
  });

  python.on('close', (code) => {
    if (code !== 0) {
      return res.status(500).send({ error: errorOutput, code });
    }
    res.send({ output, code });
  });

  python.on('error', (err) => {
    console.error('Erreur lors du lancement du script Python:', err);
    res.status(500).send({ error: 'Impossible de lancer le script Python.' });
  });
});

app.listen(3001, () => {
  console.log('✅ Backend en écoute sur http://localhost:3001');
});
