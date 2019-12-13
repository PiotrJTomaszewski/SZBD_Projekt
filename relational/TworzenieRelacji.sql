CREATE TABLE Oddzial (
    adres   VARCHAR(30) NOT NULL,
    nazwa   VARCHAR(30) NOT NULL,
    CONSTRAINT oddzial_pk PRIMARY KEY ( adres )
);

CREATE TABLE Budynek (
    adres           VARCHAR(30) NOT NULL,
    nazwa           VARCHAR(30) NOT NULL,
    ilosc_pieter    INTEGER NOT NULL,
    oddzial_adres   VARCHAR(30) NOT NULL,
    CONSTRAINT CHK_ilosc_pieter CHECK ( ilosc_pieter > 0 ),
    CONSTRAINT budynek_pk PRIMARY KEY ( adres )
);

CREATE TABLE Biuro (
    numer              INTEGER NOT NULL AUTO_INCREMENT,
    liczba_stanowisk   INTEGER NOT NULL,
    pietro             INTEGER NOT NULL,
    budynek_adres      VARCHAR(30) NOT NULL,
    CONSTRAINT CHK_liczba_stanowisk CHECK ( liczba_stanowisk > 0 ),
    CONSTRAINT biuro_pk PRIMARY KEY ( numer )
);

CREATE TABLE Dzial (
    nazwa           VARCHAR(30) NOT NULL,
    skrot           VARCHAR(5) NOT NULL,
    oddzial_adres   VARCHAR(30) NOT NULL,
    CONSTRAINT dzial_pk PRIMARY KEY ( nazwa )
);

CREATE TABLE Pracownik (
    pesel               VARCHAR(11) NOT NULL,
    imie                VARCHAR(30) NOT NULL,
    nazwisko            VARCHAR(30) NOT NULL,
    numer_telefonu      VARCHAR(9) NOT NULL,
    czy_nadal_pracuje   CHAR(1) NOT NULL,
    adres_email         VARCHAR(50) NOT NULL,
    dzial_nazwa         VARCHAR(30) NOT NULL,
    biuro_numer         INTEGER NOT NULL,
    CONSTRAINT pracownik_pk PRIMARY KEY ( pesel )
);

CREATE INDEX pracownik__idx ON
    Pracownik (
        pesel
    ASC );

CREATE TABLE KartaDostepu (
    id_karty          INTEGER NOT NULL AUTO_INCREMENT,
    data_przyznania   DATE NOT NULL DEFAULT current_date,
    pracownik_pesel   VARCHAR(11) NOT NULL,
    CONSTRAINT kartadostepu_pk PRIMARY KEY ( id_karty )
);

CREATE TABLE PrawoDostepu (
    data_przyznania         DATE NOT NULL default current_date,
    data_wygasniecia        DATE NULL,
    kartadostepu_id_karty   INTEGER NOT NULL,
    biuro_numer             INTEGER NOT NULL,
    CONSTRAINT prawodostepu_pk PRIMARY KEY ( kartadostepu_id_karty, biuro_numer ),
    CONSTRAINT CHK_data CHECK ( data_wygasniecia IS NULL OR data_wygasniecia > data_przyznania )

);

CREATE TABLE Magazyn (
    numer           INTEGER NOT NULL AUTO_INCREMENT,
    pojemnosc       INTEGER NOT NULL,
    oddzial_adres   VARCHAR(30) NOT NULL,
    CONSTRAINT magazyn_pk PRIMARY KEY ( numer ),
    CONSTRAINT CHK_pojemnosc CHECK ( pojemnosc > 0 )
);

CREATE TABLE Przypisanie (
    id_przydzialu     INTEGER NOT NULL AUTO_INCREMENT,
    data_przydzialu   DATE NOT NULL DEFAULT current_date,
    data_zwrotu       DATE NULL,
    pracownik_pesel   VARCHAR(11) NULL,
    biuro_numer       INTEGER NULL,
    CONSTRAINT przypisanie_pk PRIMARY KEY ( id_przydzialu ),
    -- Dane przypisanie może należeć do pracownika albo do biura ale nie do obu naraz
    CONSTRAINT CHK_wlasciciel CHECK ( (pracownik_pesel IS NOT NULL XOR biuro_numer IS NOT NULL) )
);

CREATE INDEX przypisanie__idx ON
    Przypisanie (
        id_przydzialu
    ASC );

CREATE TABLE Sprzet (
    numer_ewidencyjny   INTEGER NOT NULL AUTO_INCREMENT,
    data_zakupu         DATE NOT NULL DEFAULT current_date,
    nazwa               VARCHAR(30) NOT NULL,
    typ                 VARCHAR(30) NOT NULL,
    producent           VARCHAR(30) NOT NULL,
    uwagi               VARCHAR(150) NULL,
    magazyn_numer       INTEGER NULL,
    CONSTRAINT sprzet_pk PRIMARY KEY ( numer_ewidencyjny )
);

CREATE INDEX sprzet__idx ON
    Sprzet (
        numer_ewidencyjny
    ASC );

CREATE TABLE SprzetWPrzypisaniu (
    sprzet_numer_ewidencyjny    INTEGER NOT NULL,
    przypisanie_id_przydzialu   INTEGER NOT NULL,
    CONSTRAINT sprzetwprzypisaniu_pk PRIMARY KEY ( sprzet_numer_ewidencyjny, przypisanie_id_przydzialu )
);

CREATE TABLE Oprogramowanie (
    numer_ewidencyjny   INTEGER NOT NULL AUTO_INCREMENT,
    nazwa               VARCHAR(30) NOT NULL,
    producent           VARCHAR(30) NOT NULL,
    data_zakupu         DATE NOT NULL,
    data_wygasniecia    DATE NULL,
    ilosc_licencji      INTEGER NULL,
    uwagi               VARCHAR(150) NULL,
    CONSTRAINT oprogramowanie_pk PRIMARY KEY ( numer_ewidencyjny ),
    CONSTRAINT CHK_data CHECK ( data_wygasniecia IS NULL OR data_wygasniecia > data_zakupu ),
    CONSTRAINT CHK_ilosc_licencji CHECK ( ilosc_licencji IS NULL OR ilosc_licencji > 0 )
);

CREATE INDEX oprogramowanie__idx ON
    Oprogramowanie (
        numer_ewidencyjny
    ASC );

CREATE TABLE OprogramowanieNaSprzecie (
    sprzet_numer           INTEGER NOT NULL,
    oprogramowanie_numer   INTEGER NOT NULL,
    CONSTRAINT oprogramowanienasprzecie_pk PRIMARY KEY ( sprzet_numer, oprogramowanie_numer)
);

-- Dodanie kluczy obcych
ALTER TABLE Biuro
    ADD CONSTRAINT biuro_budynek_fk FOREIGN KEY ( budynek_adres )
        REFERENCES Budynek ( adres );

ALTER TABLE Budynek
    ADD CONSTRAINT budynek_oddzial_fk FOREIGN KEY ( oddzial_adres )
        REFERENCES Oddzial ( adres );

ALTER TABLE Dzial
    ADD CONSTRAINT dzial_oddzial_fk FOREIGN KEY ( oddzial_adres )
        REFERENCES Oddzial ( adres );

ALTER TABLE KartaDostepu
    ADD CONSTRAINT kartadostepu_pracownik_fk FOREIGN KEY ( pracownik_pesel )
        REFERENCES Pracownik ( pesel );

ALTER TABLE Magazyn
    ADD CONSTRAINT magazyn_oddzial_fk FOREIGN KEY ( oddzial_adres )
        REFERENCES Oddzial ( adres );

ALTER TABLE OprogramowanieNaSprzecie
    ADD CONSTRAINT oprognasprzecie_oprog_fk FOREIGN KEY ( oprogramowanie_numer )
        REFERENCES Oprogramowanie ( numer_ewidencyjny );

ALTER TABLE OprogramowanieNaSprzecie
    ADD CONSTRAINT oprognasprzecie_sprzet_fk FOREIGN KEY ( sprzet_numer )
        REFERENCES Sprzet ( numer_ewidencyjny );

ALTER TABLE Pracownik
    ADD CONSTRAINT pracownik_biuro_fk FOREIGN KEY ( biuro_numer )
        REFERENCES Biuro ( numer );

ALTER TABLE Pracownik
    ADD CONSTRAINT pracownik_dzial_fk FOREIGN KEY ( dzial_nazwa )
        REFERENCES Dzial ( nazwa );

ALTER TABLE PrawoDostepu
    ADD CONSTRAINT prawodostepu_kartadostepu_fk FOREIGN KEY ( kartadostepu_id_karty )
        REFERENCES KartaDostepu ( id_karty );

ALTER TABLE PrawoDostepu
    ADD CONSTRAINT prawodostepu_biuro_fk FOREIGN KEY ( biuro_numer )
        REFERENCES Biuro ( numer );

ALTER TABLE Przypisanie
    ADD CONSTRAINT przypisanie_biuro_fk FOREIGN KEY ( biuro_numer )
        REFERENCES Biuro ( numer );

ALTER TABLE Przypisanie
    ADD CONSTRAINT przypisanie_pracownik_fk FOREIGN KEY ( pracownik_pesel )
        REFERENCES Pracownik ( pesel );

ALTER TABLE SprzetWPrzypisaniu
    ADD CONSTRAINT sprwprzyp_przypisanie_fk FOREIGN KEY ( przypisanie_id_przydzialu )
        REFERENCES Przypisanie ( id_przydzialu );

ALTER TABLE SprzetWPrzypisaniu
    ADD CONSTRAINT sprwprzyp_sprzet_fk FOREIGN KEY ( sprzet_numer_ewidencyjny )
        REFERENCES Sprzet ( numer_ewidencyjny );

ALTER TABLE Sprzet
    ADD CONSTRAINT sprzet_magazyn_fk FOREIGN KEY ( magazyn_numer )
        REFERENCES Magazyn ( numer );
