ZADACI

- Poceti sa kontrolom prema koordinatama(najbitnije, focus)
    - Mora biti fluidno
- Snimit rutu (checkpointove)
- Lootanje Herba
- Odlazak do prodaje sa heartstonom
    - Prepoznat kada je inventory full
    - Koristenje Hearstona
    - Klikanje na prodaju
- Odlazak nazad do rute




IDEJE
Nebo je granica hheheh



7.2. Fico
Trenutna implementacija kretnje bota radi, ali ima nekoliko ključnih nedostataka koje treba poboljšati:
Puno bolje radi bez Mounta, jer ide sporije i stigne reagirat..ali moramo napravit da radi sa mountom

🔹 Trenutni problemi:
1. Analiza smjera koristi samo jednu zadnju koordinatu
    - Bot trenutno uspoređuje samo zadnju poznatu koordinatu s trenutnom, što može dovesti do čestih i nepotrebnih prilagodbi smjera.
2. Vrijeme pritiska tipke za skretanje (A/D) je fiksno (0.1 sekunda)
    - Skretanje treba biti dinamičko – duljina pritiska bi trebala zavisiti o tome koliko je bot udaljen od idealne putanje.
3. Mogućnost izbjegavanja prepreka kroz poboljšanu putanju
    - Ako se putanja fino podesi i bot prilagodi kretnje na temelju povijesnih podataka, onda bi rekao da ce ovo rjesenje bit TOP!


🔹 Bitne Varijable u Kodiranju
1️⃣ Interval provjere smjera (Linija 68)
Trenutno: 1 sekunda
Utjecaj:
Ako se smanji ispod 1 sekunde → premalo podataka, bot se može vrtjeti u krug.
Ako se poveća iznad 3 sekunde → bot može otići predaleko i onda se mora vraćati.
2️⃣ Margina za preciznost smjera (Linija 75 i 81)
Trenutno: 0.05
Utjecaj:
Ako se poveća → bot može skrenuti nepotrebno i izgubiti optimalan put.
Ako se smanji → može ignorirati male pogreške u smjeru, ali treba biti precizan.
3️⃣ Margina za postizanje ciljne koordinate (Trenutno 1.00)
Utjecaj:
Velika margina (1.00): Dobro za veće udaljenosti, ali može rezultirati netočnostima.
Manja margina (npr. 0.1 - 0.2): Točnija navigacija, ali može uzrokovati "vrtloženje" blizu cilja ako nema dovoljno podataka.
