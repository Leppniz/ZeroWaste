from itertools import count

from flask import Flask, render_template, request, redirect, url_for
from katalog import Katalog
from produkt import ProduktSztuki, ProduktWaga
from settings import DAYS_TO_WARNING

app = Flask(__name__)

# Config - zeby widziec zmiany od razu
app.config['TEMPLATES_AUTO_RELOAD'] = True

# Tworzymy JEDEN wspólny katalog dla całej aplikacji
moj_katalog = Katalog()

# Dodajemy dane startowe, żeby nie było pusto na start
jajka = ProduktSztuki("Jajka", "2026-02-1", 10)
mleko = ProduktWaga("Mleko", "2026-01-15", 1.5, "l", True)
moj_katalog.addProdukt(jajka)
moj_katalog.addProdukt(mleko)


# ======= SCIEŻKI DO STRON =========
@app.route('/')
def strona_glowna():

    context = {
        'product_count': moj_katalog.count_all(),
        'close_date_count': moj_katalog.count_expiring_soon(),
        'expired_count': moj_katalog.count_expired(),
        'frozen_count': moj_katalog.count_frozen()
    }

    return render_template('dashboard.html', **context)

@app.route('/lista')
def lista_produktow():
    # Pobieramy listę obiektów z Katalog
    lista = moj_katalog.getAll()
    # Przekazanie do HTML'a
    return render_template('index.html', produkty=lista, limit_dni=DAYS_TO_WARNING)


@app.route('/zuzyj/<id_produktu>', methods=['GET', 'POST'])
def zuzyj_produkt_strona(id_produktu):
    # 1. Szukamy produktu
    produkt = moj_katalog.getProduktById(id_produktu)

    # Zabezpieczenie: jak nie ma takiego ID, wracamy na listę
    if not produkt:
        return redirect(url_for('lista_produktow'))

    # === POST: Ktoś kliknął "Zapisz" ===
    if request.method == 'POST':
        try:
            ile = float(request.form.get('zuzyta_ilosc'))

            # Logika: odejmowanie
            nowa_ilosc = produkt.ilosc - ile

            # Nie pozwalamy na ujemne ilości
            if nowa_ilosc < 0:
                nowa_ilosc = 0

            produkt.ilosc = nowa_ilosc

        except ValueError:
            pass  # Ignorujemy błędy

        # Wracamy na listę zobaczyć efekt
        return redirect(url_for('lista_produktow'))

    # === GET: Ktoś wszedł na stronę ===
    return render_template('zuzyj.html', p=produkt)

@app.route('/usun/<id_produktu>')
def usun_produkt(id_produktu):
    # Używamy Twojej metody z Katalogu
    moj_katalog.removeProduktById(id_produktu)
    return redirect(request.referrer or url_for('strona_glowna'))


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
        nowy_produkt = ProduktWaga(nazwa, data, ilosc, jednostka)

    # 3. Dodanie do katalogu
    moj_katalog.addProdukt(nowy_produkt)

    return redirect(request.referrer or url_for('strona_glowna'))

if __name__ == '__main__':
    app.run(debug=True)