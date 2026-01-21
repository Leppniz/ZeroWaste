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
