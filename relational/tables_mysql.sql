CREATE TABLE biuro (
    numer             INTEGER NOT NULL,
    liczbastanowisk   INTEGER NOT NULL,
    pietro            INTEGER NOT NULL,
    budynek_adres     VARCHAR(20) NOT NULL
);

ALTER TABLE biuro ADD CONSTRAINT biuro_pk PRIMARY KEY ( numer );

CREATE TABLE budynek (
    adres           VARCHAR(20) NOT NULL,
    nazwa           VARCHAR(20) NOT NULL,
    iloscpieter     INTEGER NOT NULL,
    oddzial_adres   VARCHAR(20) NOT NULL
);

ALTER TABLE budynek ADD CONSTRAINT budynek_pk PRIMARY KEY ( adres );

CREATE TABLE dostepdobiura (
    prawdos_kartados_idkarty   INTEGER NOT NULL,
    biuro_numer                INTEGER NOT NULL
);

ALTER TABLE dostepdobiura ADD CONSTRAINT relation_6_pk PRIMARY KEY ( prawdos_kartados_idkarty,
                                                                     biuro_numer );

CREATE TABLE dzial (
    nazwa           VARCHAR(20) NOT NULL,
    skrot           VARCHAR(5) NOT NULL,
    oddzial_adres   VARCHAR(20) NOT NULL
);

ALTER TABLE dzial ADD CONSTRAINT dzial_pk PRIMARY KEY ( nazwa );

CREATE TABLE kartadostepu (
    idkarty           INTEGER NOT NULL,
    dataprzyznania    DATE NOT NULL,
    pracownik_pesel   VARCHAR(11) NOT NULL
);

CREATE UNIQUE INDEX kartadostepu__idx ON
    kartadostepu (
        pracownik_pesel
    ASC );

ALTER TABLE kartadostepu ADD CONSTRAINT kartadostepu_pk PRIMARY KEY ( idkarty );

CREATE TABLE magazyn (
    numer           INTEGER NOT NULL,
    pojemnosc       INTEGER NOT NULL,
    oddzial_adres   VARCHAR(20) NOT NULL
);

ALTER TABLE magazyn ADD CONSTRAINT magazyn_pk PRIMARY KEY ( numer );

CREATE TABLE oddzial (
    adres   VARCHAR(20) NOT NULL,
    nazwa   VARCHAR(20) NOT NULL
);

ALTER TABLE oddzial ADD CONSTRAINT oddzial_pk PRIMARY KEY ( adres );

CREATE TABLE oprogramowanie (
    numerewidencyjny   INTEGER NOT NULL,
    nazwa              VARCHAR(30) NOT NULL,
    producent          VARCHAR(20) NOT NULL,
    datazakupu         DATE NOT NULL,
    datawygasniecia    DATE,
    ilosclicencji      INTEGER,
    uwagi              VARCHAR(150)
);

ALTER TABLE oprogramowanie ADD CONSTRAINT oprogramowanie_pk PRIMARY KEY ( numerewidencyjny );

CREATE TABLE oprogramowanienasprzecie (
    sprzet_numer           INTEGER NOT NULL,
    oprogramowanie_numer   INTEGER NOT NULL
);

ALTER TABLE oprogramowanienasprzecie ADD CONSTRAINT relation_10_pk PRIMARY KEY ( sprzet_numer,
                                                                                 oprogramowanie_numer );

CREATE TABLE pracownik (
    pesel             VARCHAR(11) NOT NULL,
    imie              VARCHAR(20) NOT NULL,
    nazwisko          VARCHAR(20) NOT NULL,
    numertelefonu     VARCHAR(9) NOT NULL,
    czynadalpracuje   CHAR(1) NOT NULL,
    adresemail        VARCHAR(30) NOT NULL,
    dzial_nazwa       VARCHAR(20) NOT NULL,
    biuro_numer       INTEGER NOT NULL
);

ALTER TABLE pracownik ADD CONSTRAINT pracownik_pk PRIMARY KEY ( pesel );

CREATE TABLE prawodostepu (
    dataprzyznania         DATE NOT NULL,
    datawygasniecia        DATE NOT NULL,
    kartadostepu_idkarty   INTEGER NOT NULL
);

ALTER TABLE prawodostepu ADD CONSTRAINT prawodostepu_pk PRIMARY KEY ( kartadostepu_idkarty );

CREATE TABLE przypisanie (
    idprzydzialu      INTEGER NOT NULL,
    dataprzydzialu    DATE NOT NULL,
    terminzwrotu      DATE,
    pracownik_pesel   VARCHAR(11),
    biuro_numer       INTEGER
);

ALTER TABLE przypisanie ADD CONSTRAINT przypisanie_pk PRIMARY KEY ( idprzydzialu );

CREATE TABLE sprzet (
    numerewidencyjny   INTEGER NOT NULL,
    datazakupu         DATE NOT NULL,
    nazwa              VARCHAR(30) NOT NULL,
    typ                VARCHAR(20) NOT NULL,
    producent          VARCHAR(20) NOT NULL,
    uwagi              VARCHAR(150),
    magazyn_numer      INTEGER
);

ALTER TABLE sprzet ADD CONSTRAINT sprzet_pk PRIMARY KEY ( numerewidencyjny );

CREATE TABLE sprzetwprzypisaniu (
    sprzet_numerewidencyjny    INTEGER NOT NULL,
    przypisanie_idprzydzialu   INTEGER NOT NULL
);

ALTER TABLE sprzetwprzypisaniu ADD CONSTRAINT sprzetwprzypisaniu_pk PRIMARY KEY ( sprzet_numerewidencyjny,
                                                                                  przypisanie_idprzydzialu );

ALTER TABLE biuro
    ADD CONSTRAINT biuro_budynek_fk FOREIGN KEY ( budynek_adres )
        REFERENCES budynek ( adres );

ALTER TABLE budynek
    ADD CONSTRAINT budynek_oddzial_fk FOREIGN KEY ( oddzial_adres )
        REFERENCES oddzial ( adres );

ALTER TABLE dostepdobiura
    ADD CONSTRAINT dostepdobiura_biuro_fk FOREIGN KEY ( biuro_numer )
        REFERENCES biuro ( numer );

ALTER TABLE dostepdobiura
    ADD CONSTRAINT dostepdobiura_prawodostepu_fk FOREIGN KEY ( prawdos_kartados_idkarty )
        REFERENCES prawodostepu ( kartadostepu_idkarty );

ALTER TABLE dzial
    ADD CONSTRAINT dzial_oddzial_fk FOREIGN KEY ( oddzial_adres )
        REFERENCES oddzial ( adres );

ALTER TABLE kartadostepu
    ADD CONSTRAINT kartadostepu_pracownik_fk FOREIGN KEY ( pracownik_pesel )
        REFERENCES pracownik ( pesel );

ALTER TABLE magazyn
    ADD CONSTRAINT magazyn_oddzial_fk FOREIGN KEY ( oddzial_adres )
        REFERENCES oddzial ( adres );

ALTER TABLE pracownik
    ADD CONSTRAINT pracownik_biuro_fk FOREIGN KEY ( biuro_numer )
        REFERENCES biuro ( numer );

ALTER TABLE pracownik
    ADD CONSTRAINT pracownik_dzial_fk FOREIGN KEY ( dzial_nazwa )
        REFERENCES dzial ( nazwa );

ALTER TABLE prawodostepu
    ADD CONSTRAINT prawodostepu_kartadostepu_fk FOREIGN KEY ( kartadostepu_idkarty )
        REFERENCES kartadostepu ( idkarty );

ALTER TABLE przypisanie
    ADD CONSTRAINT przypisanie_biuro_fk FOREIGN KEY ( biuro_numer )
        REFERENCES biuro ( numer );

ALTER TABLE przypisanie
    ADD CONSTRAINT przypisanie_pracownik_fk FOREIGN KEY ( pracownik_pesel )
        REFERENCES pracownik ( pesel );

ALTER TABLE oprogramowanienasprzecie
    ADD CONSTRAINT relation_10_oprogramowanie_fk FOREIGN KEY ( oprogramowanie_numer )
        REFERENCES oprogramowanie ( numerewidencyjny );

ALTER TABLE oprogramowanienasprzecie
    ADD CONSTRAINT relation_10_sprzet_fk FOREIGN KEY ( sprzet_numer )
        REFERENCES sprzet ( numerewidencyjny );

ALTER TABLE sprzetwprzypisaniu
    ADD CONSTRAINT sprwprzyp_przypisanie_fk FOREIGN KEY ( przypisanie_idprzydzialu )
        REFERENCES przypisanie ( idprzydzialu );

ALTER TABLE sprzetwprzypisaniu
    ADD CONSTRAINT sprwprzyp_sprzet_fk FOREIGN KEY ( sprzet_numerewidencyjny )
        REFERENCES sprzet ( numerewidencyjny );

ALTER TABLE sprzet
    ADD CONSTRAINT sprzet_magazyn_fk FOREIGN KEY ( magazyn_numer )
        REFERENCES magazyn ( numer );
