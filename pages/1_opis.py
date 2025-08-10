import streamlit as st

st.title("📄 Opis projektu")

st.markdown("""
### 🎯 Cel projektu

Celem tego dashboardu jest analiza wyników z maratonu kolarskiego. 
Prezentowane dane obejmują m.in. dystans pokonany przez zawodników, porę startu, liczbę zadeklarowanych okrążeń i liczbę rzeczywiście wykonanych.

### 🏁 Zasady zawodów

ORBITA'25 to nie są zawody, to jazda na rowerze (dowolnym byle nie elektrycznym) maksymalnie do 24 godzin po wyznaczonej trasie wokół Częstochowy w ruchu otwartym.
Starty i całodobowy pit stop w Fabryce Rowerów TREK - Wojciech Kluk, Częstochowa ul. Drogowców 12.            

- Uczestnicy deklarowali liczbę okrążeń, które planują przejechać.
- Start odbywał się o różnych porach – rano i wieczorem.
- Uczestnicy mogli nie ukończyć biegu (DNF – Did Not Finish) lub nie wystartować (DNS – Did Not Start).
            
### 🧾 Opis kolumn danych

- **Deklarowane** – liczba zadeklarowanych okrążeń
- **Zrobione** – liczba wykonanych okrążeń
- **DNF km** – dystans pokonany w przypadku niedokończenia
- **Dystans km** – całkowity pokonany dystans
- **Pora startu** – ranny / wieczorny
- **Typ uczestnika** – np. stary (doświadczony zawodnik)

### Założenia analizy
- Statystyki nie obejmują zawodników, którzy nie wystartowali (DNS).
- Analiza skupia się na dystansie i liczbie okrążeń, a nie na czasie przejazdu.
""")
