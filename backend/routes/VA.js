// routes/users.js
const express = require('express');
const router = express.Router();
const api = require('../API/V1API');
const { getMapPoints } = require('../API/V1API');
const { getLinks } = require('../API/V1API');
const { parseGraph } = require('../API/V1API');
const { parsePointPositions } = require('../API/V1API');

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

router.get('/links', (req, res) => {
  try {
    const graphPath = 'data/version 1/output.txt';
    const pointPath = 'data/version 1/pospoints.txt';

    const { nodes, edges } = parseGraph(graphPath);
    const coordMap = parsePointPositions(pointPath);

    const nodeMap = {};
    nodes.forEach((node, index) => {
      const pos = coordMap.get(node.name);
      nodeMap[index] = {
        name: node.name,
        line: node.line,
        ...(pos || {}) // { x, y }
      }
    });
    console.log('Node Map:', nodeMap);
    console.log('Node Map:', edges);
    const links = getLinks(edges, nodeMap);
    console.log('Links:', links);
    res.json(links);
  } catch (err) {
    console.error('Erreur /links:', err);
    res.status(500).json({ error: 'Erreur lors du traitement des liens.' });
  }
});



module.exports = router;