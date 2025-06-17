// routes/users.js
const express = require('express');
const router = express.Router();
const api = require('../API/V1API');
const { getMapPoints } = require('../API/V1API');
const { getIntersections } = require('../API/V1API');



router.get('/map-points', (req, res) => {
  try {
    const filePath = 'data/version 1/pospoints.txt';
    const points = getMapPoints(filePath);
    console
    res.json(points);
  } catch (error) {
    console.error('Erreur lors de la lecture du fichier:', error);
    res.status(500).json({ error: 'Impossible de lire les points' });
  }
});

router.get('/intersections', (req, res) => {
  try {
    const filePath = 'data/version 1/metro.txt'; // adapte le chemin
    const intersections = getIntersections(filePath);
    res.json(intersections);
  } catch (err) {
    console.error('Erreur API intersections:', err);
    res.status(500).json({ error: 'Erreur lors du traitement des intersections.' });
  }
});

module.exports = router;