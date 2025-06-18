


# Remplace chaque espace par un point-virgule, sauf si déjà un point-virgule
with open('C:\\Users\\hugol\\Documents\\projet\\mastercamp\\MED-Metro-Efrei-Dodo-\\backend\\data\\metro.txt', 'r') as infile, open('output.txt', 'w') as outfile:
    for line in infile:
        parts = line.strip().split()
        if parts:
            outfile.write(';'.join(parts) + '\n')