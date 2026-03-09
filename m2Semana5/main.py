from flask import Flask, request, jsonify
import psycopg2
import os

from db import PgManager
from repositories import UserRepository, CarRepository, RentalRepository

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "xalpielite051217"),
    "dbname": os.getenv("DB_NAME", "postgres"),
}


def get_db():
    return PgManager(
        db_name=DB_CONFIG["dbname"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        host=DB_CONFIG["host"],
        port=DB_CONFIG["port"],
    )


def success_response(data=None, message=None, status=200):
    response = {"success": True}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return jsonify(response), status


def error_response(error, status=400):
    return jsonify({"success": False, "error": error}), status


@app.route("/users", methods=["GET"])
def list_users():
    db = None
    try:
        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)
        filters = request.args.to_dict()
        results = UserRepository(db).find_all(filters)
        return success_response(data=[dict(r) for r in results])
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


@app.route("/cars", methods=["GET"])
def list_cars():
    db = None
    try:
        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)
        filters = request.args.to_dict()
        results = CarRepository(db).find_all(filters)
        return success_response(data=[dict(r) for r in results])
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


@app.route("/rentals", methods=["GET"])
def list_rentals():
    db = None
    try:
        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)
        filters = request.args.to_dict()
        results = RentalRepository(db).find_all(filters)
        return success_response(data=[dict(r) for r in results])
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


@app.route("/users", methods=["POST"])
def create_user():
    db = None
    try:
        data = request.get_json()
        if not data:
            return error_response("JSON body is required", 400)

        required = ["name", "email", "username", "password", "date_of_birth"]
        for field in required:
            if field not in data or (isinstance(data[field], str) and not data[field].strip()):
                return error_response(f"Field '{field}' is required", 400)

        account_status = data.get("account_status", "active")
        if account_status not in ("active", "inactive", "suspended", "pending"):
            return error_response(
                "account_status must be one of: active, inactive, suspended, pending",
                400,
            )

        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)

        repo = UserRepository(db)
        user = repo.create(
            name=data["name"],
            email=data["email"],
            username=data["username"],
            password=data["password"],
            date_of_birth=data["date_of_birth"],
            account_status=account_status,
        )

        return success_response(data=dict(user), message="User created", status=201)
    except psycopg2.IntegrityError as e:
        if "users_email_key" in str(e) or "duplicate key" in str(e).lower():
            return error_response("Email or username already exists", 400)
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


@app.route("/cars", methods=["POST"])
def create_car():
    db = None
    try:
        data = request.get_json()
        if not data:
            return error_response("JSON body is required", 400)

        required = ["brand", "model", "manufacture_year"]
        for field in required:
            if field not in data:
                return error_response(f"Field '{field}' is required", 400)

        try:
            year = int(data["manufacture_year"])
        except (ValueError, TypeError):
            return error_response("manufacture_year must be an integer", 400)

        status = data.get("status", "disponible")
        valid_status = ("disponible", "rentado", "mantenimiento", "reservado", "fuera_de_servicio")
        if status not in valid_status:
            return error_response(
                f"status must be one of: {', '.join(valid_status)}",
                400,
            )

        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)

        repo = CarRepository(db)
        car = repo.create(
            brand=data["brand"],
            model=data["model"],
            manufacture_year=year,
            status=status,
        )

        return success_response(data=dict(car), message="Car created", status=201)
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


@app.route("/rentals", methods=["POST"])
def create_rental():
    db = None
    try:
        data = request.get_json()
        if not data:
            return error_response("JSON body is required", 400)

        if "user_id" not in data or "automobile_id" not in data:
            return error_response("user_id and automobile_id are required", 400)

        try:
            user_id = int(data["user_id"])
            automobile_id = int(data["automobile_id"])
        except (ValueError, TypeError):
            return error_response("user_id and automobile_id must be integers", 400)

        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)

        user_repo = UserRepository(db)
        car_repo = CarRepository(db)
        rental_repo = RentalRepository(db)

        car = car_repo.find_by_id(automobile_id)
        if not car:
            return error_response("Car not found", 404)
        if car["status"] != "disponible":
            return error_response(f"Car is not available (status: {car['status']})", 400)

        user = user_repo.find_by_id(user_id)
        if not user:
            return error_response("User not found", 404)

        rental = rental_repo.create(user_id, automobile_id)
        car_repo.update_status(automobile_id, "rentado")

        return success_response(data=dict(rental), message="Rental created", status=201)
    except psycopg2.IntegrityError:
        return error_response("Invalid user_id or automobile_id", 400)
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


VALID_CAR_STATUS = ("disponible", "rentado", "mantenimiento", "reservado", "fuera_de_servicio")
VALID_USER_STATUS = ("active", "inactive", "suspended", "pending", "moroso")
VALID_RENTAL_STATUS = ("activo", "completado", "cancelado", "vencido")


@app.route("/cars/<int:car_id>", methods=["PATCH"])
def update_car_status(car_id):
    db = None
    try:
        data = request.get_json()
        if not data or "status" not in data:
            return error_response("JSON body with 'status' is required", 400)

        status = data["status"]
        if status not in VALID_CAR_STATUS:
            return error_response(
                f"status must be one of: {', '.join(VALID_CAR_STATUS)}",
                400,
            )

        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)

        car_repo = CarRepository(db)
        car = car_repo.find_by_id(car_id)
        if not car:
            return error_response("Car not found", 404)

        car_repo.update_status(car_id, status)
        updated = car_repo.find_by_id(car_id)
        return success_response(data=dict(updated), message="Car status updated")
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


@app.route("/users/<int:user_id>", methods=["PATCH"])
def update_user_status(user_id):
    db = None
    try:
        data = request.get_json()
        if not data or "account_status" not in data:
            return error_response("JSON body with 'account_status' is required", 400)

        account_status = data["account_status"]
        if account_status not in VALID_USER_STATUS:
            return error_response(
                f"account_status must be one of: {', '.join(VALID_USER_STATUS)}",
                400,
            )

        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)

        user_repo = UserRepository(db)
        user = user_repo.find_by_id(user_id)
        if not user:
            return error_response("User not found", 404)

        user_repo.update_account_status(user_id, account_status)
        updated = user_repo.find_by_id(user_id)
        return success_response(data=dict(updated), message="User status updated")
    except psycopg2.IntegrityError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


@app.route("/rentals/<int:rental_id>/complete", methods=["POST"])
def complete_rental(rental_id):
    db = None
    try:
        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)

        rental_repo = RentalRepository(db)
        car_repo = CarRepository(db)

        rental = rental_repo.find_by_id(rental_id)
        if not rental:
            return error_response("Rental not found", 404)
        if rental["status"] == "completado":
            return error_response("Rental is already completed", 400)

        automobile_id = rental["automobile_id"]
        rental_repo.update_status(rental_id, "completado")
        car_repo.update_status(automobile_id, "disponible")

        updated = rental_repo.find_by_id(rental_id)
        return success_response(data=dict(updated), message="Rental completed")
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


@app.route("/rentals/<int:rental_id>", methods=["PATCH"])
def update_rental_status(rental_id):
    db = None
    try:
        data = request.get_json()
        if not data or "status" not in data:
            return error_response("JSON body with 'status' is required", 400)

        status = data["status"]
        if status not in VALID_RENTAL_STATUS:
            return error_response(
                f"status must be one of: {', '.join(VALID_RENTAL_STATUS)}",
                400,
            )

        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)

        rental_repo = RentalRepository(db)
        rental = rental_repo.find_by_id(rental_id)
        if not rental:
            return error_response("Rental not found", 404)

        rental_repo.update_status(rental_id, status)
        if status == "completado":
            car_repo = CarRepository(db)
            car_repo.update_status(rental["automobile_id"], "disponible")

        updated = rental_repo.find_by_id(rental_id)
        return success_response(data=dict(updated), message="Rental status updated")
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


@app.route("/users/<int:user_id>/flag-moroso", methods=["POST"])
def flag_user_moroso(user_id):
    db = None
    try:
        db = get_db()
        if not db.connection:
            return error_response("Database connection failed", 500)

        user_repo = UserRepository(db)
        user = user_repo.find_by_id(user_id)
        if not user:
            return error_response("User not found", 404)

        user_repo.flag_moroso(user_id)
        updated = user_repo.find_by_id(user_id)
        return success_response(data=dict(updated), message="User flagged as moroso")
    except psycopg2.IntegrityError as e:
        return error_response(
            "Cannot flag as moroso. Run 5_alter_users_moroso.sql to add 'moroso' status.",
            400,
        )
    except Exception as e:
        return error_response(str(e), 500)
    finally:
        if db and db.connection:
            db.close_connection()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
