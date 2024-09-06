from flask_mail import Mail, Message
from flask import current_app, render_template
from jinja2 import TemplateNotFound


class EmailService:
    def __init__(self):
        self.mail = None
        self.template_folder = "templates/emails/"

    def init_app(self, app):
        """Initialize the email service with the Flask app context."""
        self.mail = Mail(app)
        app.jinja_loader.searchpath.append(self.template_folder)

    def send_confirmation_email(self, recipient, confirmation_token, list_name):
        base_url = current_app.config.get("BASE_URL")
        confirmation_url = f"{base_url}/confirm/{confirmation_token}"
        subject = f"Vahvista uutiskirjeen tilaus {list_name}"
        template = "confirmation_email.html"

        try:
            body = render_template(template, confirmation_url=confirmation_url)
        except TemplateNotFound:
            return {"error": "Email template not found"}, 500

        msg = Message(
            subject=subject,
            sender=current_app.config.get("MAIL_USERNAME"),
            recipients=[recipient],
            html=body,
        )

        return self._send_email(msg)

    def send_thank_you_email(self, recipient, list_name):
        subject = f"Tervetuloa {list_name}n uutiskirjeen tilaajaksi!"
        template = "thank_you_email.html"

        try:
            body = render_template(template, list_name=list_name)
        except TemplateNotFound:
            return {"error": "Email template not found"}, 500

        msg = Message(
            subject=subject,
            sender=current_app.config.get("MAIL_USERNAME"),
            recipients=[recipient],
            html=body,
        )

        return self._send_email(msg)

    def send_custom_email(self, recipient, subject, body):
        print(recipient)
        msg = Message(
            subject=subject,
            sender=current_app.config.get("MAIL_USERNAME"),
            recipients=[recipient],
            html=body,  # FIXME: Actually process html + normal text (if not normal text provided, the client in some cases refuses to take in the email)
        )
        return self._send_email(msg)

    def _send_email(self, msg):
        if not self.mail:
            return {"error": "Email service not initialized"}, 500

        try:
            self.mail.send(msg)
        except Exception as e:
            return {"error": f"Error sending email: {e}"}, 500
        return {"message": "Email sent successfully!"}, 200
