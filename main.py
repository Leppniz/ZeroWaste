from katalog import Katalog
from produkt import ProduktSztuki, ProduktWaga

# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
    # === TESTY ===
    # jajka = ProduktSztuki("Jajka", "2025-12-24", 10)
    # mleko = ProduktWaga("Mleko", "2025-12-05", 1.5, "l")
    #
    # # === Zamrozenie ===
    # print(jajka.getInfo())
    # jajka.isFrozen = True
    # print(jajka.getInfo())

    # print(mleko.getInfo())
    #
    # print("\n--- Test zabezpieczeń ---")
    #
    # mleko.ilosc = -5
    # print(f"Waga po błędzie (bez zmian): {mleko.ilosc}")
    #
    # jajka.data_waznosci = "Bzdura"
    #
    # jajka.ilosc = 20
    # print(f"Nowa ilość jajek: {jajka.ilosc}")

    # sklep = Katalog()
    # mleko = ProduktSztuki("Mleko", "2025-12-01", 10)
    # id_mleka = mleko.id
    # sklep.addProdukt(mleko)
    #
    # print("--- Przed zmianą ---")
    # sklep.displayAll()
    #
    # znaleziony_produkt = sklep.getProductById(id_mleka)
    #
    # if znaleziony_produkt:
    #     znaleziony_produkt.name = "Mleko Łaciate"
    #     znaleziony_produkt.ilosc = 55
    #
    #     if isinstance(znaleziony_produkt, ProduktSztuki):
    #         print("Edytowano sztuki!")
    #
    # print("\n--- Po zmianie ---")
    # sklep.displayAll()


def main():
    sklep = Katalog()

    while True:
        print("\n=== MENU MAGAZYNU ===")
        print("1. Dodaj produkt (Sztuki)")
        print("2. Dodaj produkt (Waga)")
        print("3. Wyświetl wszystko")
        print("4. Usuń produkt")
        print("5. Edytuj produkt")
        print("0. Wyjdź")

        wybor = input("\nWybierz opcję: ")

        if wybor == '0':
            print("Zamykanie programu...")
            break

        elif wybor == '1':
            nazwa = input("Podaj nazwę: ")
            data = input("Data ważności (YYYY-MM-DD) lub Enter dla braku: ")
            if data == "": data = None

            try:
                ilosc = int(input("Ilość (szt): "))

                nowy = ProduktSztuki(nazwa, data, ilosc)
                sklep.addProdukt(nowy)
                print("✅ Dodano produkt!")
            except ValueError:
                print("❌ Błąd: Ilość musi być liczbą całkowitą!")

        elif wybor == '2':
            nazwa = input("Podaj nazwę: ")
            data = input("Data ważności (YYYY-MM-DD) lub Enter dla braku: ")
            if data == "": data = None

            try:
                ilosc = float(input("Ilość: "))
                jednostka = input("Jednostka (kg, g, l, ml): ")
                nowy = ProduktWaga(nazwa, data, ilosc, jednostka)
                sklep.addProdukt(nowy)
                print("✅ Dodano produkt!")
            except ValueError as e:
                print(f"❌ Błąd: {e}")

        elif wybor == '3':
            print("\n--- STAN MAGAZYNU ---")
            sklep.displayAll()

        elif wybor == '4':
            id_do_usuniecia = input("Podaj ID produktu do usunięcia: ")
            sukces = sklep.removeProduktById(id_do_usuniecia)
            if sukces:
                print("🗑️ Usunięto produkt.")
            else:
                print("⚠️ Nie znaleziono takiego ID.")

        elif wybor == '5':
            id_do_edycji = input("Podaj ID produktu do edycji: ")
            produkt = sklep.getProductById(id_do_edycji)

            if produkt:
                print(f"Edytujesz: {produkt.name}")
                nowa_nazwa = input("Nowa nazwa (Enter żeby pominąć): ")
                if nowa_nazwa:
                    produkt.name = nowa_nazwa

                nowa_ilosc = input("Nowa ilość (Enter żeby pominąć): ")
                if nowa_ilosc:
                    # Tutaj trzeba by sprawdzić czy to int czy float zależnie od typu produktu
                    produkt.ilosc = float(nowa_ilosc)

                mrozenie = input("Czy zamrozić? (t/n/Enter pominąć): ")
                if mrozenie == 't':
                    produkt.isFrozen = True
                elif mrozenie == 'n':
                    produkt.isFrozen = False

                print("✅ Zaktualizowano!")
            else:
                print("⚠️ Nie znaleziono takiego ID.")

        else:
            print("Nieznana opcja!")


if __name__ == "__main__":
    main()