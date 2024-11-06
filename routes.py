from flask import Blueprint, request, jsonify, current_app
from flask_pymongo import ObjectId
from itsdangerous import URLSafeTimedSerializer
from email_service import EmailService
from functions import convert_object_ids_to_strings
from DatabaseManager import DatabaseManager

# Initialize Blueprint
bp = Blueprint('main', __name__)

# Access Flask app context for extensions
def get_mongo():
    db_man = DatabaseManager().get_instance()
    db = db_man.get_db()
    return db

# Initialize EmailService
def get_email_service():
    return current_app.email_service


# Secret key for generating confirmation tokens
def get_serializer():
    return URLSafeTimedSerializer(current_app.config.get("SECRET_KEY"))

@bp.route("/signup", methods=["POST"])
def signup():
    mongo = get_mongo()  # Access mongo instance
    email_service = get_email_service()  # Access email service
    serializer = get_serializer()  # Access serializer

    data = request.get_json()
    email = data.get("email")
    list_id = data.get("list_id")
    domain = data.get("domain")

    if not email:
        return jsonify({"error": "Missing email address"}), 400

    if mongo.users.find_one({"email": email, "domain": domain}):
        return jsonify({"error": "Email address already exists for this domain"}), 400

    if not list_id or not mongo["db.lists"].find_one({"_id": ObjectId(list_id)}): # "domain": domain}):
        return jsonify({"error": "Invalid list ID for this domain"}), 400

    confirmation_token = serializer.dumps({"email": email, "list_id": list_id})#, "domain": domain})

    list_data = mongo["db.lists"].find_one({"_id": ObjectId(list_id)})#, "domain": domain})
    response = email_service.send_confirmation_email(email, confirmation_token, list_data)

    if response[1] != 200:
        return jsonify(response[0]), response[1]

    mongo.users.insert_one({
        "email": email,
        "confirmed": False,
        "list_id": list_id,
        "domain": domain
    })

    return jsonify({"message": "Confirmation email sent. Please check your inbox!"}), 201

@bp.route("/confirm/<token>", methods=["GET"])
def confirm_subscription(token):
    mongo = get_mongo()  # Access mongo instance
    email_service = get_email_service()  # Access email service
    serializer = get_serializer()  # Access serializer

    try:
        data = serializer.loads(token)
        email = data["email"]
        list_id = data["list_id"]
        domain = data["domain"]
    except Exception as e:
        current_app.logger.error(f"Token decoding error: {e}")
        return jsonify({"error": "Invalid confirmation token"}), 400

    user = mongo.users.find_one({"email": email, "list_id": list_id, "domain": domain})
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user["confirmed"]:
        return jsonify({"message": "Email already confirmed"}), 200

    mongo.users.update_one({"email": email, "list_id": list_id, "domain": domain}, {"$set": {"confirmed": True}})

    list_data = mongo.lists.find_one({"_id": ObjectId(list_id), "domain": domain})
    response = email_service.send_thank_you_email(email, list_data['name'])

    if response[1] != 200:
        return jsonify(response[0]), response[1]

    return jsonify({"message": "Subscription confirmed successfully!"}), 200

@bp.route("/lists", methods=["GET", "POST", "PUT", "DELETE"])
def manage_lists():
    mongo = get_mongo()  # Access mongo instance
    domain = request.headers.get("Domain")  # Get the domain from request headers

    if request.method == "GET":
        lists = list(mongo.db.lists.find({"domain": domain}))
        return jsonify(convert_object_ids_to_strings(lists)), 200

    elif request.method == "POST":
        data = request.get_json()
        name = data.get("name")
        description = data.get("description", "")
        sender_email = data.get("sender_email", current_app.config["MAIL_USERNAME"])

        if not name:
            return jsonify({"error": "Missing list name"}), 400

        if mongo.db.lists.find_one({"name": name, "domain": domain}):
            return jsonify({"error": "List with that name already exists for this domain"}), 400

        new_list = {
            "name": name,
            "description": description,
            "sender_email": sender_email,
            "domain": domain  # Associate list with domain
        }
        mongo.db.lists.insert_one(new_list)

        return jsonify(new_list), 201

    elif request.method == "PUT":
        data = request.get_json()
        list_id = request.args.get("_id")

        if not list_id:
            return jsonify({"error": "Missing list ID"}), 400

        update_data = {
            "name": data.get("name"),
            "description": data.get("description"),
            "sender_email": data.get("sender_email")
        }
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            return jsonify({"error": "Missing update data"}), 400

        updated_list = mongo.db.lists.find_one_and_update(
            {"_id": ObjectId(list_id), "domain": domain},
            {"$set": update_data},
            return_document=True
        )

        if not updated_list:
            return jsonify({"error": "List not found"}), 404

        return jsonify(updated_list), 200

    elif request.method == "DELETE":
        list_id = request.args.get("_id")

        if not list_id:
            return jsonify({"error": "Missing list ID"}), 400

        deleted_list = mongo.db.lists.find_one_and_delete({"_id": ObjectId(list_id), "domain": domain})

        if not deleted_list:
            return jsonify({"error": "List not found"}), 404

        return jsonify({"message": "List deleted successfully"}), 200

    else:
        return jsonify({"error": "Unsupported method"}), 405

@bp.route("/lists/<list_id>/subscribers", methods=["GET"])
def get_subscribers(list_id):
    mongo = get_mongo()  # Access mongo instance
    domain = request.headers.get("Domain")  # Get the domain from request headers

    if not list_id:
        return jsonify({"error": "Missing list ID"}), 400

    try:
        list_data = mongo.db.lists.find_one({"_id": ObjectId(list_id), "domain": domain})
    except Exception as e:
        current_app.logger.error(f"Error finding list: {e}")
        return jsonify({"error": "Invalid list ID"}), 400

    if not list_data:
        return jsonify({"error": "List not found"}), 404

    subscribers = list(mongo.db.users.find({"list_id": list_id, "domain": domain}))
    subscribers = convert_object_ids_to_strings(subscribers)

    return jsonify(subscribers), 200
