


# Remplace chaque espace par un point-virgule, sauf si déjà un point-virgule
with open('data/version 1/metro.txt', 'r') as infile, open('output.txt', 'w') as outfile:
    for line in infile:
        parts = line.strip().split()
        if parts:
            outfile.write(';'.join(parts) + '\n')