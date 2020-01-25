-- Usunięcie starych kluczy obcych
ALTER TABLE Biuro
    DROP FOREIGN KEY biuro_budynek_fk;

ALTER TABLE Budynek
    DROP FOREIGN KEY budynek_oddzial_fk;

ALTER TABLE Dzial
    DROP FOREIGN KEY dzial_oddzial_fk;

ALTER TABLE KartaDostepu
    DROP FOREIGN KEY kartadostepu_pracownik_fk;

ALTER TABLE Magazyn
    DROP FOREIGN KEY magazyn_oddzial_fk;

ALTER TABLE OprogramowanieNaSprzecie
    DROP FOREIGN KEY oprognasprzecie_oprog_fk;

ALTER TABLE OprogramowanieNaSprzecie
    DROP FOREIGN KEY oprognasprzecie_sprzet_fk;

ALTER TABLE Pracownik
    DROP FOREIGN KEY  pracownik_biuro_fk;

ALTER TABLE Pracownik
    DROP FOREIGN KEY pracownik_dzial_fk;

ALTER TABLE PrawoDostepu
    DROP FOREIGN KEY prawodostepu_kartadostepu_fk;

ALTER TABLE PrawoDostepu
    DROP FOREIGN KEY prawodostepu_biuro_fk;

ALTER TABLE Przypisanie
    DROP FOREIGN KEY przypisanie_biuro_fk;

ALTER TABLE Przypisanie
    DROP FOREIGN KEY przypisanie_pracownik_fk;

ALTER TABLE SprzetWPrzypisaniu
    DROP FOREIGN KEY sprwprzyp_przypisanie_fk;

ALTER TABLE SprzetWPrzypisaniu
    DROP FOREIGN KEY  sprwprzyp_sprzet_fk;

ALTER TABLE Sprzet
    DROP FOREIGN KEY  sprzet_magazyn_fk;

-- Dodanie kluczy obcych
ALTER TABLE Biuro
    ADD CONSTRAINT biuro_budynek_fk FOREIGN KEY ( budynek_adres )
        REFERENCES Budynek ( adres )
        ON UPDATE CASCADE;

ALTER TABLE Budynek
    ADD CONSTRAINT budynek_oddzial_fk FOREIGN KEY ( oddzial_adres )
        REFERENCES Oddzial ( adres )
        ON UPDATE CASCADE;

ALTER TABLE Dzial
    ADD CONSTRAINT dzial_oddzial_fk FOREIGN KEY ( oddzial_adres )
        REFERENCES Oddzial ( adres )
        ON UPDATE CASCADE;

ALTER TABLE KartaDostepu
    ADD CONSTRAINT kartadostepu_pracownik_fk FOREIGN KEY ( pracownik_pesel )
        REFERENCES Pracownik ( pesel )
        ON UPDATE CASCADE
        ON DELETE CASCADE;

ALTER TABLE Magazyn
    ADD CONSTRAINT magazyn_oddzial_fk FOREIGN KEY ( oddzial_adres )
        REFERENCES Oddzial ( adres )
        ON UPDATE CASCADE;

ALTER TABLE OprogramowanieNaSprzecie
    ADD CONSTRAINT oprognasprzecie_oprog_fk FOREIGN KEY ( oprogramowanie_numer )
        REFERENCES Oprogramowanie ( numer_ewidencyjny )
        ON UPDATE CASCADE
        ON DELETE CASCADE;

ALTER TABLE OprogramowanieNaSprzecie
    ADD CONSTRAINT oprognasprzecie_sprzet_fk FOREIGN KEY ( sprzet_numer )
        REFERENCES Sprzet ( numer_ewidencyjny )
        ON UPDATE CASCADE
        ON DELETE CASCADE;

ALTER TABLE Pracownik
    ADD CONSTRAINT pracownik_biuro_fk FOREIGN KEY ( biuro_numer )
        REFERENCES Biuro ( numer )
        ON UPDATE CASCADE;

ALTER TABLE Pracownik
    ADD CONSTRAINT pracownik_dzial_fk FOREIGN KEY ( dzial_nazwa )
        REFERENCES Dzial ( nazwa )
        ON UPDATE CASCADE;

ALTER TABLE PrawoDostepu
    ADD CONSTRAINT prawodostepu_kartadostepu_fk FOREIGN KEY ( kartadostepu_id_karty )
        REFERENCES KartaDostepu ( id_karty )
        ON UPDATE CASCADE
        ON DELETE CASCADE;

ALTER TABLE PrawoDostepu
    ADD CONSTRAINT prawodostepu_biuro_fk FOREIGN KEY ( biuro_numer )
        REFERENCES Biuro ( numer )
        ON UPDATE CASCADE
        ON DELETE CASCADE;

ALTER TABLE Przypisanie
    ADD CONSTRAINT przypisanie_biuro_fk FOREIGN KEY ( biuro_numer )
        REFERENCES Biuro ( numer )
        ON UPDATE CASCADE
        ON DELETE CASCADE;

ALTER TABLE Przypisanie
    ADD CONSTRAINT przypisanie_pracownik_fk FOREIGN KEY ( pracownik_pesel )
        REFERENCES Pracownik ( pesel )
        ON UPDATE CASCADE
        ON DELETE CASCADE;

ALTER TABLE SprzetWPrzypisaniu
    ADD CONSTRAINT sprwprzyp_przypisanie_fk FOREIGN KEY ( przypisanie_id_przydzialu )
        REFERENCES Przypisanie ( id_przydzialu )
        ON UPDATE CASCADE
        ON DELETE CASCADE;

ALTER TABLE SprzetWPrzypisaniu
    ADD CONSTRAINT sprwprzyp_sprzet_fk FOREIGN KEY ( sprzet_numer_ewidencyjny )
        REFERENCES Sprzet ( numer_ewidencyjny )
        ON UPDATE CASCADE
        ON DELETE CASCADE;

ALTER TABLE Sprzet
    ADD CONSTRAINT sprzet_magazyn_fk FOREIGN KEY ( magazyn_numer )
        REFERENCES Magazyn ( numer )
        ON UPDATE CASCADE;
