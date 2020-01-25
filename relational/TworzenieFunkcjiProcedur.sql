-- Definicja funkcji i procedur

-- Przenosi sprzęt z magazynu do danego przypisania.
-- Zwraca kod błędu.
-- 0 - Brak błędu.
-- 1 - Sprzęt nie jest na magazynie.
-- 2 - Wyjątek podczas wstawiania rekordu.
DELIMITER $$
CREATE FUNCTION PrzypiszSprzet(pNumerEwidencyjny INTEGER, pPrzypisanieId INTEGER)
  RETURNS INTEGER
  BEGIN
    DECLARE vKodBledu INTEGER DEFAULT 0;
    DECLARE vIdObecnegoMagazynu INTEGER; -- Id magazynu, na którym sprzęt się obecnie znajduje
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
      SET vKodBledu = 2; -- Wyjątek podczas wstawiania rekordu
    SELECT magazyn_numer INTO vIdObecnegoMagazynu FROM Sprzet WHERE numer_ewidencyjny = pNumerEwidencyjny;
    IF vIdObecnegoMagazynu IS NOT NULL THEN
      INSERT INTO SprzetWPrzypisaniu (sprzet_numer_ewidencyjny, przypisanie_id_przydzialu)
      VALUES (pNumerEwidencyjny, pPrzypisanieId);
      UPDATE Sprzet SET magazyn_numer = NULL WHERE numer_ewidencyjny = pNumerEwidencyjny;
    ELSE
      SET vKodBledu = 1; -- Sprzęt nie jest na magazynie
    END IF;
    RETURN vKodBledu;
  END $$
DELIMITER ;

-- Wstawia do bazy danych fakt zwrotu sprzętu na magazyn
-- Zwraca kod błędu.
-- 0 - brak błędu.
-- 1 - Brak miejsca na magazynie.
DELIMITER $$
CREATE FUNCTION ZwrocSprzet(pNumerEwidencyjny INTEGER, pPrzypisanieId INTEGER, pMagazynId INTEGER, pDataZwrotu DATE)
  RETURNS INTEGER
  DETERMINISTIC
  BEGIN
    DECLARE vIloscMiejscaMagazyn INTEGER;
    DECLARE vKodBledu INTEGER DEFAULT 0;
    SELECT WolnaPojemnoscMagazynu(pMagazynId) INTO vIloscMiejscaMagazyn FROM DUAL;
    IF vIloscMiejscaMagazyn > 0 THEN
      UPDATE Przypisanie SET data_zwrotu = pDataZwrotu WHERE id_przydzialu = pPrzypisanieId;
      UPDATE Sprzet SET magazyn_numer = pMagazynId WHERE numer_ewidencyjny = pNumerEwidencyjny;
    ELSE
      SET vKodBledu = 1;
    END IF;
    RETURN vKodBledu;
  END $$
DELIMITER ;

-- Zwraca liczbę wolnych (obecnie nie używanych) kopii licencji danego oprogramowania.
-- Wartość NULL oznacza, że liczba kopii jest nieograniczona.
DELIMITER $$
CREATE FUNCTION IleWolnychLicencji(pIdOprogramowania INTEGER)
  RETURNS INTEGER
  DETERMINISTIC
  BEGIN
    DECLARE vIleWolnych INTEGER;
    DECLARE vIleZajetych INTEGER;
    DECLARE vIleLacznie INTEGER;
    SELECT ilosc_licencji INTO vIleLacznie FROM Oprogramowanie WHERE numer_ewidencyjny = pIdOprogramowania;
    IF vIleLacznie IS NULL THEN
      SET vIleWolnych = NULL;
    ELSE
      SELECT COUNT(*) INTO vIleZajetych FROM OprogramowanieNaSprzecie WHERE oprogramowanie_numer = pIdOprogramowania;
      SET vIleWolnych = vIleLacznie - vIleZajetych;
    END IF;
    RETURN vIleWolnych;
  END $$
DELIMITER ;

-- Wstawia do bazy danych fakt instalacji wskazanego oprogramowania na wskazanym sprzęcie.
-- Zwraca kod błędu.
-- 0 - Brak błędu.
-- 1 - Brak wystarczającej liczby kopii oprogramowania.
-- 2 - Wyjątek podczas dodawania rekordu. Prawdopodobnie dane oprogramowanie było już zainstalowane na danym sprzęcie.
DELIMITER $$
CREATE FUNCTION ZainstalujOprogramowanie(pIdSprzetu INTEGER, pIdOprogramowania INTEGER)
  RETURNS INTEGER
  DETERMINISTIC
  BEGIN
    DECLARE vIleWolnychLicencji INTEGER;
    DECLARE vKodBledu INTEGER DEFAULT 0;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
      SET vKodBledu = 2; -- Prawdopodobnie oprogramowanie jest już zainstalowane
    SELECT IleWolnychLicencji(pIdOprogramowania) INTO vIleWolnychLicencji FROM DUAL;
    IF vIleWolnychLicencji >= 1 OR vIleWolnychLicencji IS NULL THEN
      INSERT INTO OprogramowanieNaSprzecie (sprzet_numer, oprogramowanie_numer)
      VALUES (pIdSprzetu, pIdOprogramowania);
    ELSE
      SET vKodBledu = 1; -- Brak wystarczającej liczby kopii
    END IF;
    RETURN vKodBledu;
  END $$
DELIMITER ;

-- Dla każdego oprogramowania z wygasłą licencją oznacza wszystkie jego kopie jako usunięte ze sprzętu.
DELIMITER $$
CREATE OR REPLACE PROCEDURE OdinstalujWygasleOprogramowanie()
  BEGIN
    DECLARE vNumerOprogramowania INTEGER;
    DECLARE vPrzeszukano INTEGER DEFAULT 0;
    DECLARE cWygasleOpr CURSOR FOR SELECT numer_ewidencyjny FROM Oprogramowanie WHERE data_wygasniecia < CURRENT_DATE;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET vPrzeszukano = 1;
    OPEN cWygasleOpr;
    wygasle: LOOP
      FETCH cWygasleOpr INTO vNumerOprogramowania;
      IF vPrzeszukano = 1 THEN
        LEAVE wygasle;
      END IF;
      DELETE FROM OprogramowanieNaSprzecie WHERE oprogramowanie_numer = vNumerOprogramowania;
    END LOOP;
  END $$
DELIMITER ;

-- Zwraca ilość wolnych miejsc w biurze
DELIMITER $$
CREATE FUNCTION IleWolnychMiejscBiuro(pNumerBiura INTEGER)
  RETURNS INTEGER
  DETERMINISTIC
  BEGIN
    DECLARE vIleLacznieMiejsc INTEGER;
    DECLARE vIleZajetychMiejsc INTEGER;
    DECLARE vIleWolnychMiejsc INTEGER;
    SELECT liczba_stanowisk INTO vIleLacznieMiejsc FROM Biuro WHERE numer = pNumerBiura;
    SELECT COUNT(*) INTO vIleZajetychMiejsc FROM Pracownik WHERE biuro_numer = pNumerBiura AND czy_nadal_pracuje = '1';
    SET vIleWolnychMiejsc = vIleLacznieMiejsc - vIleZajetychMiejsc;
    RETURN vIleWolnychMiejsc;
  END $$
DELIMITER ;

-- Wstawia nowy rekord do tablicy Biuro sprawdzając czy wkazane w parametrze piętro istnieje w budynku.
-- Zwraca kod błędu.
-- 0 - Brak błędu.
-- 1 - Nieprawidłowe piętro.
-- 2 - Wyjątek przy wstawianiu rekordu.
DELIMITER $$
CREATE OR REPLACE FUNCTION DodajBiuro(pNumer INTEGER, pLiczbaStanowisk INTEGER, pPietro INTEGER, pBudynekAdres VARCHAR(30))
  RETURNS INTEGER
  DETERMINISTIC
  BEGIN
    DECLARE vKodBledu INTEGER DEFAULT 0;
    DECLARE vLiczbaPieterWBudynku INTEGER;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
      SET vKodBledu = 2; -- Wyjątek przy wstawianiu rekordu
    SELECT ilosc_pieter INTO vLiczbaPieterWBudynku FROM Budynek WHERE adres = pBudynekAdres;
    IF pPietro >= 0 AND pPietro < vLiczbaPieterWBudynku THEN
      INSERT INTO Biuro (numer, liczba_stanowisk, pietro, budynek_adres)
      VALUES (pNumer, pLiczbaStanowisk, pPietro, pBudynekAdres);
    ELSE
      SET vKodBledu = 1; -- Nieprawidłowe piętro
    END IF;
    RETURN vKodBledu;
  END $$
DELIMITER ;

-- Zwraca wolną pojemność danego magazynu.
DELIMITER $$
CREATE FUNCTION WolnaPojemnoscMagazynu(pNumerMagazynu INTEGER)
  RETURNS INTEGER
  DETERMINISTIC
  BEGIN
    DECLARE vLacznaPojemnosc INTEGER;
    DECLARE vZajetaPojemnosc INTEGER;
    DECLARE vWolnaPojemnosc INTEGER;
    SELECT pojemnosc INTO vLacznaPojemnosc FROM Magazyn WHERE numer = pNumerMagazynu;
    SELECT COUNT(*) INTO vZajetaPojemnosc FROM Sprzet WHERE magazyn_numer = pNumerMagazynu;
    SET vWolnaPojemnosc = vLacznaPojemnosc - vZajetaPojemnosc;
    RETURN vWolnaPojemnosc;
  END $$
