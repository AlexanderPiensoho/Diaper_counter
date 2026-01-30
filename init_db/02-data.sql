USE diaper_counter;

-- Mock data for adults

SET AUTOCOMMIT=0;
INSERT INTO adults VALUES   (1, 'alexander piensoho', '1995-08-02'),
                            (2, 'elin piensoho', '1995-12-31'),
                            (3, 'helena piensoho', '1965-02-22'),
                            (4, 'niklas piensoho', '1964-10-14'),
                            (5, 'emilia piensoho', '1992-04-17'),
                            (6, 'monica berglund', '1969-10-12'),
                            (7, 'mikael berglund', '1970-02-16');
          COMMIT;

-- Mock data for baby

SET AUTOCOMMIT=0;
INSERT INTO baby VALUES   (1, 'henning piensoho', '2026-01-01');
            COMMIT;

-- Mock data for change_types

SET AUTOCOMMIT=0;
INSERT INTO change_types (change_type) VALUES   ('pee'),
                                                ('poo'),
                                                ('routine');
            COMMIT;

-- Mock data for diaper_changes
SET AUTOCOMMIT=0;
INSERT INTO diaper_changes (baby_id, change_type_id, accident, adult_id ) VALUES  (1, 1, FALSE, 1),
                                                                                  (1, 1, FALSE, 1);
            COMMIT;
