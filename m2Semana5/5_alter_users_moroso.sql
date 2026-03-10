ALTER TABLE lyfter_car_rental.users DROP CONSTRAINT IF EXISTS users_account_status_check;
ALTER TABLE lyfter_car_rental.users ADD CONSTRAINT users_account_status_check
    CHECK (account_status IN ('active', 'inactive', 'suspended', 'pending', 'moroso'));
