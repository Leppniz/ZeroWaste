from flask import Flask, render_template, request, redirect, url_for
from katalog import Katalog
from produkt import ProduktSztuki, ProduktWaga

app = Flask(__name__)

# Config - zeby widziec zmiany od razu
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Tworzymy JEDEN wspólny katalog dla całej aplikacji
moj_katalog = Katalog()

# Dodajemy dane startowe, żeby nie było pusto na start
jajka = ProduktSztuki("Jajka", "2026-02-24", 10)
mleko = ProduktWaga("Mleko", "2026-01-15", 1.5, "l")
moj_katalog.addProdukt(jajka)
moj_katalog.addProdukt(mleko)


@app.route('/')
def strona_glowna():
    # Pobieramy listę obiektów z Twojej klasy Katalog
    lista = moj_katalog.getAll()

    # Przekazujemy je do HTML
    return render_template('index.html', produkty=lista)


@app.route('/usun/<id_produktu>')
def usun_produkt(id_produktu):
    # Używamy Twojej metody z Katalogu
    moj_katalog.removeProduktById(id_produktu)
    return redirect(url_for('strona_glowna'))


@app.route('/dodaj', methods=['POST'])
def dodaj_produkt():
    # 1. Pobieramy dane
    nazwa = request.form.get('nazwa')
    data = request.form.get('data')
    try:
        ilosc = float(request.form.get('ilosc'))
    except ValueError:
        ilosc = 0  # Zabezpieczenie jak ktoś wpisze głupoty

    jednostka = request.form.get('wybrana_jednostka')

    # 2. Logika wyboru klasy (OOP)
    if jednostka == 'szt':
        # Dla sztuk ilosc musi byc int
        nowy_produkt = ProduktSztuki(nazwa, data, int(ilosc))
    else:
        # Dla wagi/objętości przekazujemy wybraną jednostkę (kg, g, l, ml)
        # Twoja klasa ProduktWaga sama sprawdzi czy jednostka jest poprawna!
        nowy_produkt = ProduktWaga(nazwa, data, ilosc, jednostka)

    # 3. Dodanie do katalogu
    moj_katalog.addProdukt(nowy_produkt)

    return redirect(url_for('strona_glowna'))

if __name__ == '__main__':
    app.run(debug=True)