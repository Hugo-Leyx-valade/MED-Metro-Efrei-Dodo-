from collections import defaultdict, deque

def parse_graph(file_path):
    id_to_name = {}  # id (int) -> nom station (str)
    graph = defaultdict(set)

    with open(file_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('V;'):
                parts = line.split(';')
                station_id = int(parts[1])
                station_name = ' '.join(p for p in parts[2:5] if p)
                id_to_name[station_id] = station_name

            elif line.startswith('E;'):
                parts = line.split(';')
                a = int(parts[1])
                b = int(parts[2])
                # relier les stations dans le graphe
                graph[a].add(b)
                graph[b].add(a)

    return graph, id_to_name

def count_connected_components(graph):
    visited = set()
    components = []

    for node in graph:
        if node not in visited:
            queue = deque([node])
            component = []

            while queue:
                current = queue.popleft()
                if current in visited:
                    continue
                visited.add(current)
                component.append(current)
                queue.extend(graph[current] - visited)

            components.append(component)

    return components

# Analyse
file_path = "C:\\Users\\jungk\\Documents\\projet\\MED-Metro-Efrei-Dodo-\\backend\\data\\version 1\\output.txt"
graph, id_to_name = parse_graph(file_path)
components = count_connected_components(graph)

print(f"Nombre de composantes connexes : {len(components)}")
for i, comp in enumerate(components):
    noms = [id_to_name.get(s, f"#{s}") for s in comp]
    print(f"Composante {i + 1} ({len(comp)} stations) : {', '.join(noms[:5])}{'...' if len(comp) > 5 else ''}")

if len(components) == 1:
    print("Le métro est connexe ✅")
else:
    print("Le métro n'est pas connexe ❌")
