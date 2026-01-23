from flask import Flask, render_template, request, redirect, url_for, flash
from katalog import Katalog
from produkt import ProduktSztuki, ProduktWaga
from settings import DAYS_TO_WARNING

app = Flask(__name__)

# Config-żeby widzieć zmiany od razu
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'TAJNY_KLUCZ'

# Tworzymy JEDEN wspólny katalog dla całej aplikacji
moj_katalog = Katalog()

# Dodajemy dane startowe, żeby nie było pusto na start
jajka = ProduktSztuki("Jajka", "2026-02-1", 10)
mleko = ProduktWaga("Mleko", "2026-01-15", 1.5, "l", True)
moj_katalog.addProdukt(jajka)
moj_katalog.addProdukt(mleko)


# ======= ŚCIEŻKI DO STRON =========
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
    # Pobieramy tryb z paska adresu (domyślnie 'szczegoly')
    tryb = request.args.get('tryb', 'szczegoly')

    if tryb == 'ogolne':
        # Pobieranie listy zgrupowanej po nazwie
        produkty_data = moj_katalog.get_grouped_by_name()
    else:
        # Pobieranie normalnej listy produktów
        produkty_data = moj_katalog.getAll()

    return render_template('lista.html', produkty=produkty_data, tryb=tryb, limit_dni=DAYS_TO_WARNING)


@app.route('/zuzyj/<id_produktu>', methods=['GET', 'POST'])
def zuzyj_produkt_strona(id_produktu):
    produkt = moj_katalog.getProduktById(id_produktu)
    if not produkt:
        flash("Nie znaleziono produktu!", "error")
        return redirect(url_for('lista_produktow'))
    if request.method == 'POST':
        try:
            ile = float(request.form.get('zuzyta_ilosc'))
            nowa_ilosc = produkt.ilosc - ile
            if nowa_ilosc <= 0:
                moj_katalog.removeProduktById(id_produktu)
                flash(f"Zużyto całość '{produkt.name}'. Usunięto.", "info")
            else:
                produkt.ilosc = nowa_ilosc
                jedn = getattr(produkt, 'jednostka', 'szt')
                flash(f"Zostało: {nowa_ilosc:g} {jedn}", "success")
        except ValueError:
            flash("Błąd! Wpisz liczbę.", "error")
        return redirect(url_for('lista_produktow'))
    return render_template('zuzyj.html', p=produkt)


@app.route('/edytuj/<id_produktu>', methods=['GET', 'POST'])
def edytuj_produkt(id_produktu):
    # 1. Pobieramy edytowany produkt
    produkt = moj_katalog.getProduktById(id_produktu)

    if not produkt:
        flash("Nie znaleziono produktu!", "error")
        return redirect(url_for('lista_produktow'))

    if request.method == 'POST':
        # 2. Pobieramy dane z formularza
        nowa_nazwa = request.form.get('nazwa')
        nowa_ilosc = float(request.form.get('ilosc'))
        nowa_jednostka = request.form.get('jednostka')
        nowa_data = request.form.get('data')  # String np. "2026-01-30"
        jest_mrozone = request.form.get('czy_zamrozone') is not None

        # === SCENARIUSZ A: CZY POWSTANIE DUPLIKAT? ===
        # Sprawdzamy, czy w lodówce już jest taki produkt (inny niż ten edytowany)
        duplikat = moj_katalog.znajdzDuplikat(nowa_nazwa, nowa_data, nowa_jednostka, jest_mrozone, id_produktu)

        if duplikat:
            duplikat.ilosc += nowa_ilosc

            moj_katalog.removeProduktById(id_produktu)

            flash(f"Produkt połączono z istniejącym '{duplikat.name}'! (Nowa ilość: {duplikat.ilosc} {nowa_jednostka})",
                  "info")
            return redirect(url_for('lista_produktow'))

        # === SCENARIUSZ B i C: BRAK DUPLIKATU===

        stara_jednostka = getattr(produkt, 'jednostka', 'szt')
        czy_byl_sztuki = (stara_jednostka == 'szt')
        czy_ma_byc_sztuki = (nowa_jednostka == 'szt')

        # Czy zmieniamy TYP? (Sztuki <-> Waga)
        if czy_byl_sztuki != czy_ma_byc_sztuki:
            # REINKARNACJA (Podmiana obiektu)
            if czy_ma_byc_sztuki:
                nowy_produkt = ProduktSztuki(nowa_nazwa, nowa_data, nowa_ilosc)
            else:
                nowy_produkt = ProduktWaga(nowa_nazwa, nowa_data, nowa_ilosc, nowa_jednostka)

            nowy_produkt.id = produkt.id  # Zachowujemy ID
            nowy_produkt.isFrozen = jest_mrozone
            moj_katalog.podmienProdukt(produkt.id, nowy_produkt)
            flash(f"Zmieniono typ produktu na {nowa_jednostka}!", "success")

        else:
            # ZWYKŁA AKTUALIZACJA
            produkt.name = nowa_nazwa
            produkt.ilosc = nowa_ilosc
            produkt.data_waznosci = nowa_data
            produkt.isFrozen = jest_mrozone

            if not czy_byl_sztuki:
                produkt.jednostka = nowa_jednostka

            flash(f"Zaktualizowano produkt: {produkt.name}", "success")

        return redirect(url_for('lista_produktow'))

    return render_template('edytuj.html', p=produkt)

@app.route('/usun/<id_produktu>')
def usun_produkt(id_produktu):
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

        # 1. Sprawdzamy, czy użytkownik zaznaczył "Zamrożone"
        # Checkbox zwraca 'on' jeśli zaznaczony, albo None, jeśli nie
        jest_mrozone = request.form.get('czy_zamrozone') is not None

        # 2. Tworzymy obiekt (OOP)
        if jednostka == 'szt':
            nowy_produkt = ProduktSztuki(nazwa, data, float(ilosc))
        else:
            nowy_produkt = ProduktWaga(nazwa, data, ilosc, jednostka)

        # Ustawiamy flagę zamrożenia (musisz mieć pole is_frozen w klasie Produkt!)
        nowy_produkt.isFrozen = jest_mrozone

        # 3. Dodajemy do katalogu
        moj_katalog.addProdukt(nowy_produkt)

        # 4. Sprawdzamy, czy user chce dodać kolejny, czy wyjść
        chce_kolejny = request.form.get('dodaj_kolejny')

        if chce_kolejny:
            # Jeśli zaznaczył "Dodaj kolejny", wyświetlamy komunikat i zostajemy tu
            flash(f"Dodano produkt: {nazwa}. Możesz dodać następny.", "success")
            return redirect(url_for('dodaj_produkt'))
        else:
            # Standardowo wracamy na listę
            return redirect(url_for('lista_produktow'))

    # === GET: Wyświetlamy formularz ===
    return render_template('dodaj.html')

if __name__ == '__main__':
    app.run(debug=True)