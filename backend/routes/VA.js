// routes/users.js
const express = require('express');
const router = express.Router();
const api = require('../API/V1API');
const { getMapPoints } = require('../API/V1API');
const { getLinks } = require('../API/V1API');
const { parseGraph } = require('../API/V1API');
const { parsePointPositions } = require('../API/V1API');
const { computeShortestPath } = require('../API/V1API');

router.get('/map-points', (req, res) => {
  try {
    const filePath = 'data/version 1/pospoints.txt';
    const points = getMapPoints(filePath);
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
    const links = getLinks(edges, nodeMap);
    res.json(links);
  } catch (err) {
    console.error('Erreur /links:', err);
    res.status(500).json({ error: 'Erreur lors du traitement des liens.' });
  }
});

router.get('/shortest-path', async (req, res) => {

  const { from, to } = req.query; // <--- Utiliser req.query au lieu de req.body
  console.log('Paramètres de la requête:', { from, to });
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
  const links = getLinks(edges, nodeMap);

  if (!from || !to) {
    return res.status(400).json({ error: 'Paramètres "from" et "to" requis' });
  }

  try {
    // Appelle ici ta fonction de calcul de chemin
    const path = await computeShortestPath(nodeMap[from], nodeMap[to], links); // à adapter selon ton implémentation
    res.json(path);
  } catch (error) {
    console.error('Erreur calcul du chemin :', error);
    res.status(500).json({ error: 'Erreur interne du serveur' });
  }
} catch (error) {
    console.error('Erreur lors de la lecture du fichier:', error);
    res.status(500).json({ error: 'Impossible de lire les points' });
  }
}
);
module.exports = router;