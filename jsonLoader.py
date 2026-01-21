import json

from produkt import ProduktSztuki, ProduktWaga


def load_produkty_z_json(path, katalog):
    with open(path, "r", encoding="utf-8") as f:
        dane = json.load(f)

    for p in dane:
        if p["typ"] == "sztuki":
            produkt = ProduktSztuki(
                p["nazwa"],
                p["data"],
                p["ilosc"]
            )
        else:
            produkt = ProduktWaga(
                p["nazwa"],
                p["data"],
                p["ilosc"],
                p.get("jednostka", "")
            )

        produkt.isFrozen = p.get("zamrozone", False)

        # tags (optional)
        for tag in p.get("tags", []):
            produkt.add_tag(tag)

        katalog.addProdukt(produkt)


def save_produkty_do_json(path, katalog):
    data = []

    for p in katalog.getAll():
        base = {
            "id": p.id,
            "nazwa": p.name,
            "data": p._data_waznosci.isoformat() if p._data_waznosci else None,
            "zamrozone": p.isFrozen,
            "tags": p.tags
        }

        if hasattr(p, "jednostka"):
            base.update({
                "typ": "waga",
                "ilosc": p.ilosc,
                "jednostka": p.jednostka
            })
        else:
            base.update({
                "typ": "sztuki",
                "ilosc": p.ilosc
            })

        data.append(base)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
