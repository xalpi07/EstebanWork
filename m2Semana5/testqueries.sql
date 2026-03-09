INSERT INTO lyfter_car_rental.users (name, email, username, password, date_of_birth, account_status)
VALUES ('Juan Pérez Nuevo', 'juan.perez.nuevo@email.com', 'juanpereznuevo', '$2b$12$abc123hashedpass', '1995-08-20', 'active');

INSERT INTO lyfter_car_rental.cars (brand, model, manufacture_year, status)
VALUES ('Toyota', 'Prius', 2024, 'disponible');

UPDATE lyfter_car_rental.users
SET account_status = 'inactive'
WHERE id = 1;

UPDATE lyfter_car_rental.cars
SET status = 'mantenimiento'
WHERE id = 5;

INSERT INTO lyfter_car_rental.rentals (user_id, automobile_id, status)
VALUES (10, 6, 'activo');

UPDATE lyfter_car_rental.cars
SET status = 'rentado'
WHERE id = 6;

UPDATE lyfter_car_rental.rentals
SET status = 'completado'
WHERE id = 5;

UPDATE lyfter_car_rental.cars
SET status = 'disponible'
WHERE id = 2;

UPDATE lyfter_car_rental.cars
SET status = 'fuera_de_servicio'
WHERE id = 5;

SELECT *
FROM lyfter_car_rental.cars
WHERE status = 'rentado';

SELECT *
FROM lyfter_car_rental.cars
WHERE status = 'disponible';
