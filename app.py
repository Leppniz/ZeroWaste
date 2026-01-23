from itertools import count

from flask import Flask, render_template, request, redirect, url_for, flash

from jsonLoader import load_produkty_z_json, save_produkty_do_json
from katalog import Katalog
from produkt import ProduktSztuki, ProduktWaga
from settings import DAYS_TO_WARNING


app = Flask(__name__)

# Config - zeby widziec zmiany od razu
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SECRET_KEY'] = 'TAJNY_KLUCZ'

moj_katalog = Katalog()
zakupy_katalog = Katalog()

load_produkty_z_json("produkty.json", moj_katalog)
load_produkty_z_json("zakupy.json", zakupy_katalog)


@app.route('/')
def strona_glowna():

    context = {
        'product_count': moj_katalog.count_all(),
        'close_date_count': moj_katalog.count_expiring_soon(),
        'expired_count': moj_katalog.count_expired(),
        'frozen_count': moj_katalog.count_frozen()
    }

    return render_template('dashboard.html', **context)

#================================== LISTA ====================================
@app.route('/lista')
def lista_produktow():
    # Pobieramy listę obiektów z Katalog
    lista = moj_katalog.getAll()
    # Przekazanie do HTML'a
    return render_template('lista.html', produkty=lista, limit_dni=DAYS_TO_WARNING)


#================================== TAGI ====================================
@app.route('/tagi')
def tagi():
    # Pobieramy listę obiektów z Katalog
    lista = moj_katalog.getAll()
    # Przekazanie do HTML'a
    return render_template('tagi.html', produkty=lista, limit_dni=DAYS_TO_WARNING)
@app.route("/dodaj-tag", methods=["POST"])
def dodaj_tag():
    produkt_id = request.form.get("produkt_id")
    tag = request.form.get("tag", "").strip()
    produkt = moj_katalog.getProduktById(produkt_id)

    if produkt and tag:
        produkt.add_tag(tag)
        save_produkty_do_json("produkty.json", moj_katalog)  # ✅ persist
        flash(f"Dodano tag: #{tag}", "success")

    return redirect(request.referrer or url_for("lista_produktow"))


@app.route("/usun-tag", methods=["POST"])
def usun_tag():
    produkt_id = request.form.get("produkt_id")
    tag = request.form.get("tag")
    produkt = moj_katalog.getProduktById(produkt_id)

    if produkt and tag:
        produkt.remove_tag(tag)
        save_produkty_do_json("produkty.json", moj_katalog)  # ✅ persist
        flash(f"Usunięto tag: #{tag}", "info")

    return redirect(request.referrer or url_for("lista_produktow"))

#================================== MROZENIE ====================================
@app.route('/mrozenie')
def mrozenie():
    # Pobieramy wszystkie produkty z katalogu
    produkty = moj_katalog.getAll()
    return render_template('mrozenie.html', produkty=produkty)

@app.route('/toggle-freeze', methods=['POST'])
def toggle_freeze():
    produkt_id = request.form.get('produkt_id')
    produkt = moj_katalog.getProduktById(produkt_id)

    if produkt:
        produkt.isFrozen = not produkt.isFrozen  # przełączamy stan zamrożenia
        flash(f"{produkt.name} został {'zamrożony ❄️' if produkt.isFrozen else 'odmrożony'}", "success")

        # Opcjonalnie: jeśli chcesz, możesz tu też zapisać do JSON, żeby zmiany były trwałe

    return redirect(request.referrer or url_for('mrozenie'))
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

#================================== ZAKUPY ====================================
@app.route('/zakupy')
def zakupy():
    # Pobieramy listę produktów z katalogu zakupów
    produkty = zakupy_katalog.getAll()
    return render_template('zakupy.html', produkty=produkty)


@app.route('/dodajzakupy', methods=['GET', 'POST'])
def dodaj_zakupy():
    if request.method == 'POST':
        nazwa = request.form.get('nazwa')
        jednostka = request.form.get('wybrana_jednostka')

        try:
            ilosc = float(request.form.get('ilosc'))
        except (ValueError, TypeError):
            ilosc = 0.0

        # Tworzymy odpowiedni typ produktu
        if jednostka == 'szt':
            nowy_produkt = ProduktSztuki(nazwa, ilosc=ilosc)
        else:
            nowy_produkt = ProduktWaga(nazwa, ilosc=ilosc, jednostka=jednostka)

        # Dodajemy do katalogu zakupów
        zakupy_katalog.addProdukt(nowy_produkt)

        # Zapis do JSON
        save_produkty_do_json("zakupy.json", zakupy_katalog)  # Twoja funkcja zapisująca zakupy

        flash(f"Dodano {ilosc} {jednostka} {nazwa} do listy zakupów.", "success")
        return redirect(url_for('zakupy'))

    # GET: wyświetlamy formularz
    return render_template('dodajzakupy.html')
@app.route("/usunzakupy", methods=["POST"])
def usun_zakupy():
    produkt_id = request.form.get("produkt_id")
    produkt = zakupy_katalog.getProduktById(produkt_id)

    if produkt:
        zakupy_katalog.removeProduktById(produkt_id)
        save_produkty_do_json("zakupy.json", zakupy_katalog)
        flash(f"Usunięto {produkt.name} z listy zakupów.", "info")

    return redirect(url_for("zakupy"))


#================================== WYSZUKIWARKA ====================================
@app.route("/wyszukiwarka", methods=["GET"])
def wyszukiwarka():
    query = request.args.get("q", "").strip().lower()
    produkty = []

    if query:
        # Szukamy w głównym katalogu
        produkty = [p for p in moj_katalog.getAll() if query in p.name.lower()]

    return render_template("wyszukiwarka.html", produkty=produkty)


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