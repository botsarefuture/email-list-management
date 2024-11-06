from flask_mail import Mail, Message
from flask import current_app, render_template
from jinja2 import TemplateNotFound
import dns.resolver
from bson.objectid import ObjectId

class EmailService:
    def __init__(self):
        self.mail = None
        self.template_folder = 'templates/emails/'

    def init_app(self, app):
        """Initialize the email service with the Flask app context."""
        self.mail = Mail(app)
        app.jinja_loader.searchpath.append(self.template_folder)

    def send_confirmation_email(self, recipient, confirmation_token, list):
        """Send a confirmation email to the recipient."""
        base_url = current_app.config.get('BASE_URL')
        confirmation_url = f"{base_url}/confirm/{confirmation_token}"
        subject = f"Vahvista uutiskirjeen tilaus {list['name']}"
        template = 'confirmation_email.html'

        return self._send_email_from_template(template, recipient, subject, sender=list["sender_email"], confirmation_url=confirmation_url)

    def send_thank_you_email(self, recipient, list_name):
        """Send a thank-you email to the recipient."""
        subject = f"Tervetuloa {list_name}n uutiskirjeen tilaajaksi!"
        template = 'thank_you_email.html'

        return self._send_email_from_template(template, recipient, subject, list_name=list_name)

    def send_custom_email(self, recipient, subject, body):
        """Send a custom email with the specified subject and body."""
        msg = Message(
            subject=subject,
            sender=current_app.config.get("MAIL_USERNAME"),
            recipients=[recipient],
            html=body
        )
        return self._send_email(msg)

    def _send_email_from_template(self, template, recipient, subject, sender=None, **context):
        """Helper function to render an email template and send the email."""
        try:
            body = render_template(template, **context)
        except TemplateNotFound:
            return {"error": "Email template not found"}, 500

        msg = Message(
            subject=subject,
            sender=current_app.config.get("MAIL_USERNAME") if sender is None else sender,
            recipients=[recipient],
            html=body
        )

        return self._send_email(msg)

    def _send_email(self, msg):
        """Send the email message using Flask-Mail."""
        if not self.mail:
            return {"error": "Email service not initialized"}, 500

        try:
            self.mail.send(msg)
        except Exception as e:
            return {"error": f"Error sending email: {e}"}, 500

        return {"message": "Email sent successfully!"}, 200

    def check_dns_record(self, domain, expected_value):
        """Check if the expected DNS TXT record exists for the domain."""
        try:
            answers = dns.resolver.resolve(domain, 'TXT')
            for rdata in answers:
                if expected_value in rdata.to_text():
                    return True
        except Exception as e:
            print(f"DNS lookup failed: {e}")
        return False

    def add_email_address(self, user_id, email_address):
        """Add an email address for the user."""
        # Store the email and set its verification status to False initially
        current_app.mongo.db.users.update_one(
            {"_id": user_id},
            {"$set": {"email": email_address, "verified": False}}
        )
        # Generate verification token and send instructions
        self.send_verification_instructions(email_address)

    def send_verification_instructions(self, email_address):
        """Send email with instructions to add a DNS record for verification."""
        # Implementation to send an email with DNS instructions
        subject = "Please verify your email address"
        body = f"Please add the following TXT record to your DNS: 'your_expected_txt_record_value'."
        self.send_custom_email(email_address, subject, body)

    def verify_email(self, user_id, email_address):
        return current_app.mongo.db.users.find({"_id": ObjectId(user_id)})
        """Check DNS records to verify user's email address."""
        # Extract domain from the email address
        domain = email_address.split('@')[-1]

        # Define expected DNS value (you need to customize this)
        expected_value = "your-expected-dns-value"  # Set this as per your verification logic

        if self.check_dns_record(domain, expected_value):
            # Update user record to mark the email as verified
            current_app.mongo.db.users.update_one(
                {"_id": user_id},
                {"$set": {"verified": True}}
            )
            return {"message": "Email address verified successfully."}, 200
        else:
            return {"error": "Email verification failed. Please check your DNS records."}, 400
