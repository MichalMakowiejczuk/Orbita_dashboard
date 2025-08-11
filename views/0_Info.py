import streamlit as st

st.title("Dashboard Maratonu Kolarskiego - Orbita'25")


st.markdown("""
Witaj w interaktywnym dashboardzie podsumowującym lokalny maraton kolarski - Orbita'25.
Dzięki temu narzędziu możesz przeanalizować wyniki zawodników, trasę oraz profil wysokościowy.
Dane pochodzą z rzeczywistego wydarzenia i zostały przetworzone na potrzeby tego dashboardu.
\nZaleca się przeglądanie na komputerze dla lepszej wygody.

---
                         
### Co znajdziesz w tym dashboardzie?
W menu po lewej stronie możesz nawigować między:
- Opisem wydarzenia
- Trasą i profilem wysokościowym
- Prostymi wykresami
- Statystykami wyników z filtrami, rankingiem/listą startową
            
---

### Zasady zawodów            
ORBITA'25 to nie są zawody, to jazda na rowerze (dowolnym byle nie elektrycznym) maksymalnie do 24 godzin po wyznaczonej trasie wokół Częstochowy w ruchu otwartym.
Starty i całodobowy pit stop w Fabryce Rowerów TREK - Wojciech Kluk, Częstochowa ul. Drogowców 12.            

- Uczestnicy deklarowali liczbę okrążeń, które planują przejechać.
- Start odbywał się o różnych porach – rano i wieczorem.
- Uczestnicy mogli nie ukończyć okrążenia lub nie wystartować (DNS – Did Not Start).
""")

# --- Footer ---
st.markdown("---")
st.sidebar.markdown("Made with ❤️ by Michał Makowiejczuk")