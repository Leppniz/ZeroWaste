from katalog import Katalog
from produkt import ProduktSztuki, ProduktWaga

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    jajka = ProduktSztuki("Jajka", "2025-12-24", 10)
    mleko = ProduktWaga("Mleko", "2025-12-05", 1.5, "l")

    print(jajka.getInfo())
    print(mleko.getInfo())

    print("\n--- Test zabezpieczeń ---")

    mleko.ilosc = -5
    print(f"Waga po błędzie (bez zmian): {mleko.ilosc}")

    jajka.data_waznosci = "Bzdura"

    jajka.ilosc = 20
    print(f"Nowa ilość jajek: {jajka.ilosc}")
