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

#================================== PRODUKT ====================================

@app.route('/usun/<id_produktu>')
def usun_produkt(id_produktu):
    moj_katalog.removeProduktById(id_produktu)

    save_produkty_do_json("produkty.json", moj_katalog)

    return redirect(request.referrer or url_for('strona_glowna'))

@app.route('/dodaj', methods=['GET', 'POST'])
def dodaj_produkt():
    if request.method == 'POST':
        nazwa = request.form.get('nazwa')
        data = request.form.get('data')

        try:
            ilosc = float(request.form.get('ilosc'))
        except ValueError:
            ilosc = 0.0

        jednostka = request.form.get('wybrana_jednostka')
        jest_mrozone = request.form.get('czy_zamrozone') is not None

        if jednostka == 'szt':
            nowy_produkt = ProduktSztuki(nazwa, data, float(ilosc))
        else:
            nowy_produkt = ProduktWaga(nazwa, data, ilosc, jednostka)

        nowy_produkt.isFrozen = jest_mrozone

        moj_katalog.addProdukt(nowy_produkt)

        save_produkty_do_json("produkty.json", moj_katalog)

        chce_kolejny = request.form.get('dodaj_kolejny')

        if chce_kolejny:
            flash(f"Dodano produkt: {nazwa}. Możesz dodać następny.", "success")
            return redirect(url_for('dodaj_produkt'))
        else:
            return redirect(url_for('lista_produktow'))

    return render_template('dodaj.html')

#================================== LISTA ====================================

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

            save_produkty_do_json("produkty.json", moj_katalog)

        except ValueError:
            flash("Błąd! Wpisz liczbę.", "error")

        return redirect(url_for('lista_produktow'))

    return render_template('zuzyj.html', p=produkt)

@app.route('/edytuj/<id_produktu>', methods=['GET', 'POST'])
def edytuj_produkt(id_produktu):
    produkt = moj_katalog.getProduktById(id_produktu)

    if not produkt:
        flash("Nie znaleziono produktu!", "error")
        return redirect(url_for('lista_produktow'))

    if request.method == 'POST':
        nowa_nazwa = request.form.get('nazwa')
        nowa_ilosc = float(request.form.get('ilosc'))
        nowa_jednostka = request.form.get('jednostka')
        nowa_data = request.form.get('data')
        jest_mrozone = request.form.get('czy_zamrozone') is not None

        # === SCENARIUSZ A: DUPLIKAT ===
        duplikat = moj_katalog.znajdzDuplikat(
            nowa_nazwa, nowa_data, nowa_jednostka, jest_mrozone, id_produktu
        )

        if duplikat:
            duplikat.ilosc += nowa_ilosc
            moj_katalog.removeProduktById(id_produktu)

            save_produkty_do_json("produkty.json", moj_katalog)  # 🔥 SAVE

            flash(
                f"Produkt połączono z istniejącym '{duplikat.name}'! "
                f"(Nowa ilość: {duplikat.ilosc} {nowa_jednostka})",
                "info"
            )
            return redirect(url_for('lista_produktow'))

        # === SCENARIUSZ B / C ===
        stara_jednostka = getattr(produkt, 'jednostka', 'szt')
        czy_byl_sztuki = (stara_jednostka == 'szt')
        czy_ma_byc_sztuki = (nowa_jednostka == 'szt')

        if czy_byl_sztuki != czy_ma_byc_sztuki:
            # REINKARNACJA
            if czy_ma_byc_sztuki:
                nowy_produkt = ProduktSztuki(nowa_nazwa, nowa_data, nowa_ilosc)
            else:
                nowy_produkt = ProduktWaga(nowa_nazwa, nowa_data, nowa_ilosc, nowa_jednostka)

            nowy_produkt.id = produkt.id
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

        save_produkty_do_json("produkty.json", moj_katalog)  # 🔥 SAVE

        return redirect(url_for('lista_produktow'))

    return render_template('edytuj.html', p=produkt)

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
        save_produkty_do_json("produkty.json", moj_katalog)
        flash(f"Dodano tag: #{tag}", "success")

    return redirect(request.referrer or url_for("lista_produktow"))


@app.route("/usun-tag", methods=["POST"])
def usun_tag():
    produkt_id = request.form.get("produkt_id")
    tag = request.form.get("tag")
    produkt = moj_katalog.getProduktById(produkt_id)

    if produkt and tag:
        produkt.remove_tag(tag)
        save_produkty_do_json("produkty.json", moj_katalog)
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
        produkt.isFrozen = not produkt.isFrozen

        flash(
            f"{produkt.name} został {'zamrożony ❄️' if produkt.isFrozen else 'odmrożony'}",
            "success"
        )

        save_produkty_do_json("produkty.json", moj_katalog)

    return redirect(request.referrer or url_for('mrozenie'))

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

if __name__ == '__main__':
    app.run(debug=True)