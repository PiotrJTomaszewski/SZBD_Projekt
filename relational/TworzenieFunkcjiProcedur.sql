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
    DECLARE vKodBledu INTEGER;
    DECLARE vIdObecnegoMagazynu INTEGER; -- Id magazynu, na którym sprzęt się obecnie znajduje
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
      SET vKodBledu = 2; -- Wyjątek podczas wstawiania rekordu
    SET vKodBledu = 0;
    SELECT magazyn_numer INTO vIdObecnegoMagazynu FROM Sprzet WHERE numer_ewidencyjny = pNumerEwidencyjny;
    IF vIdObecnegoMagazynu IS NULL THEN
      INSERT INTO SprzetWPrzypisaniu (sprzet_numer_ewidencyjny, przypisanie_id_przydzialu)
      VALUES (pNumerEwidencyjny, pPrzypisanieId);
      UPDATE Sprzet SET magazyn_numer = NULL;
    ELSE
      SET vKodBledu = 1; -- Sprzęt nie jest na magazynie
    END IF;
    RETURN vKodBledu;
  END $$
DELIMITER ;

-- Zwraca sprzęt na magazyn
DELIMITER $$
CREATE PROCEDURE ZwrocSprzet(pNumerEwidencyjny INTEGER, pPrzypisanieId INTEGER, pMagazynId INTEGER, pDataZwrotu DATE)
  BEGIN
    UPDATE Przypisanie SET termin_zwrotu = pDataZwrotu WHERE id_przydzialu = pPrzypisanieId;
    UPDATE Sprzet SET magazyn_numer = pMagazynId WHERE numer_ewidencyjny = pNumerEwidencyjny;
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

-- Oznacza w bazie danych fakt instalacji wskazanego oprogramowania na wskazanym sprzęcie.
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
    DECLARE vKodBledu INTEGER;
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
      SET vKodBledu = 2; -- Prawdopodobnie oprogramowanie jest już zainstalowane
    SET vKodBledu = 0;
    SELECT IleWolnychLicencji(pIdOprogramowania) INTO vIleWolnychLicencji FROM DUAL;
    IF vIleWolnychLicencji >= 1 OR vIleWolnychLicencji IS NULL THEN
      INSERT INTO OprogramowanieNaSprzecie (sprzet_numer, oprogramowanie_numer)
      VALUES (pIdSprzetu, pIdOprogramowania);
    ELSE
      SET vKodBledu = 1; -- Brak wystarczającej liczby kopii
    END IF;
    RETURN vKodBledu;
  end $$
DELIMITER ;

