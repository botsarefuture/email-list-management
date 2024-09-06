from flask import (
    Blueprint,
    request,
    render_template,
    redirect,
    url_for,
    current_app,
    flash,
)
from flask_pymongo import ObjectId

# Initialize Blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# Access Flask app context for extensions
def get_mongo():
    return current_app.mongo


def get_email_service():
    return current_app.email_service


@admin_bp.route("/lists", methods=["GET"])
def manage_lists():
    mongo = get_mongo()  # Access mongo instance
    lists = list(mongo.db.lists.find())
    return render_template("admin/manage_lists.html", lists=lists)


@admin_bp.route("/lists/create", methods=["GET", "POST"])
def create_list():
    if request.method == "POST":
        data = request.form
        name = data.get("name")
        description = data.get("description", "")
        sender_email = data.get("sender_email")

        if not name:
            return "Missing list name", 400

        mongo = get_mongo()  # Access mongo instance
        if mongo.db.lists.find_one({"name": name}):
            return "List with that name already exists", 400

        new_list = {
            "name": name,
            "description": description,
            "sender_email": sender_email,
        }
        mongo.db.lists.insert_one(new_list)
        return redirect(url_for("admin.manage_lists"))

    return render_template("admin/edit_list.html", title="Create New List")


@admin_bp.route("/lists/<list_id>/edit", methods=["GET", "POST"])
def edit_list(list_id):
    mongo = get_mongo()  # Access mongo instance
    list_data = mongo.db.lists.find_one({"_id": ObjectId(list_id)})

    if request.method == "POST":
        data = request.form
        update_data = {
            "name": data.get("name"),
            "description": data.get("description"),
            "sender_email": data.get("sender_email"),
        }
        mongo.db.lists.update_one({"_id": ObjectId(list_id)}, {"$set": update_data})
        return redirect(url_for("admin.manage_lists"))

    return render_template("admin/edit_list.html", title="Edit List", list=list_data)


@admin_bp.route("/lists/<list_id>/delete", methods=["POST"])
def delete_list(list_id):
    mongo = get_mongo()  # Access mongo instance
    mongo.db.lists.find_one_and_delete({"_id": ObjectId(list_id)})
    return redirect(url_for("admin.manage_lists"))


@admin_bp.route("/send-email", methods=["GET", "POST"])
def send_email():
    if request.method == "POST":
        list_id = request.form.get("list_id")
        subject = request.form.get("subject")
        body = request.form.get("body")

        if not list_id or not subject or not body:
            flash("All fields are required", "error")
            return redirect(url_for("admin.send_email"))

        mongo = get_mongo()
        list_data = mongo.db.lists.find_one({"_id": ObjectId(list_id)})

        if not list_data:
            flash("List not found", "error")
            return redirect(url_for("admin.send_email"))

        subscribers = mongo.db.users.find({"list_id": list_id, "confirmed": True})
        recipient_emails = [user["email"] for user in subscribers]

        email_service = get_email_service()

        for email in recipient_emails:
            try:
                email_service.send_custom_email(email, subject, body)
            except Exception as e:
                current_app.logger.error(f"Error sending email to {email}: {e}")
                flash(f"Error sending email to {email}", "error")

        flash("Emails sent successfully!", "success")
        return redirect(url_for("admin.send_email"))

    mongo = get_mongo()
    lists = list(mongo.db.lists.find())
    return render_template("admin/send_email.html", lists=lists)
