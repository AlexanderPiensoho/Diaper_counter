CREATE TABLE sleep_sessions (
    sleep_id INT PRIMARY KEY AUTO_INCREMENT,
    baby_id INT NOT NULL,
    adult_id INT NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP NULL,
    notes VARCHAR(255),
    FOREIGN KEY (baby_id) REFERENCES baby(baby_id),
    FOREIGN KEY (adult_id) REFERENCES adults(adult_id)
);

CREATE TABLE food_intake (
    food_id INT PRIMARY KEY AUTO_INCREMENT,
    baby_id INT NOT NULL,
    adult_id INT NOT NULL,
    food_type VARCHAR(20) NOT NULL CHECK (food_type IN ('breast', 'bottle', 'solid')),
    amount_ml INT NULL,
    logged_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes VARCHAR(255),
    FOREIGN KEY (baby_id) REFERENCES baby(baby_id),
    FOREIGN KEY (adult_id) REFERENCES adults(adult_id)
);
