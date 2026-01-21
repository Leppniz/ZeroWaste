from itertools import count

from flask import Flask, render_template, request, redirect, url_for, flash
from katalog import Katalog
from produkt import ProduktSztuki, ProduktWaga
from settings import DAYS_TO_WARNING

app = Flask(__name__)

# Config - zeby widziec zmiany od razu
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'TAJNY_KLUCZ'

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
    return render_template('lista.html', produkty=lista, limit_dni=DAYS_TO_WARNING)

@app.route('/tagi')
def tagi():
    # Pobieramy listę obiektów z Katalog
    lista = moj_katalog.getAll()
    # Przekazanie do HTML'a
    return render_template('tagi.html', produkty=lista, limit_dni=DAYS_TO_WARNING)

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


@app.route('/dodaj', methods=['GET', 'POST'])
def dodaj_produkt():
    # === POST: Zapisujemy dane ===
    if request.method == 'POST':
        nazwa = request.form.get('nazwa')
        data = request.form.get('data')

        try:
            ilosc = float(request.form.get('ilosc'))
        except ValueError:
            ilosc = 0.0

        jednostka = request.form.get('wybrana_jednostka')

        # 1. Sprawdzamy czy użytkownik zaznaczył "Zamrożone"
        # Checkbox zwraca 'on' jeśli zaznaczony, albo None jeśli nie
        jest_mrozone = request.form.get('czy_zamrozone') is not None

        # 2. Tworzymy obiekt (OOP)
        if jednostka == 'szt':
            nowy_produkt = ProduktSztuki(nazwa, data, int(ilosc))
        else:
            nowy_produkt = ProduktWaga(nazwa, data, ilosc, jednostka)

        # Ustawiamy flagę zamrożenia (musisz mieć pole is_frozen w klasie Produkt!)
        nowy_produkt.isFrozen = jest_mrozone

        # 3. Dodajemy do katalogu
        moj_katalog.addProdukt(nowy_produkt)

        # 4. Sprawdzamy czy user chce dodać kolejny, czy wyjść
        chce_kolejny = request.form.get('dodaj_kolejny')

        if chce_kolejny:
            # Jeśli zaznaczył "Dodaj kolejny", wyświetlamy komunikat i zostajemy tu
            flash(f"Dodano produkt: {nazwa}. Możesz dodać następny.")
            return redirect(url_for('dodaj_produkt'))
        else:
            # Standardowo wracamy na listę
            return redirect(url_for('lista_produktow'))

    # === GET: Wyświetlamy formularz ===
    return render_template('dodaj.html')

if __name__ == '__main__':
    app.run(debug=True)