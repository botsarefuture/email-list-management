from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from DatabaseManager import DatabaseManager
from functions import generate_txt_record
from bson.objectid import ObjectId


# Initialize the database manager instance
db = DatabaseManager().get_instance().get_db()


class User(UserMixin):
    def __init__(self, _id, username, password, hashed=False):
        """Initialize a User instance.

        Args:
            _id (str): User's unique identifier.
            username (str): User's username.
            password (str): User's password (raw or hashed).
            hashed (bool): Indicates if the password is already hashed. Default is False.
        """
        self._id = str(_id)
        self.username = username
        self.password_hash = self.set_password(password, hashed)
        self.domains = []  # List to hold the user's domains
        self.txt_record = generate_txt_record(self._id)
        self._init_domains()

    def _init_domains(self):
        self.domains = [domain["domain"] for domain in list(db.db.domains.find({"user": ObjectId(self._id)}))]

    def set_password(self, password, hashed):
        """Set the user's password hash.

        Args:
            password (str): User's password (raw or hashed).
            hashed (bool): Indicates if the password is already hashed.

        Returns:
            str: Hashed password.
        """
        if not hashed:
            return generate_password_hash(password)
        return password

    def get_id(self):
        """Get the user's unique identifier.

        Returns:
            str: User's unique identifier.
        """
        return self._id

    def verify_password(self, password):
        """Verify the provided password against the stored hash.

        Args:
            password (str): The password to verify.

        Returns:
            bool: True if the password matches the stored hash, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

    def add_domain(self, domain):
        """Add a domain to the user's list of domains if not already present.

        Args:
            domain (str): The domain to add.

        Returns:
            bool: True if domain was added, False if it already exists.
        """
        if domain not in self.domains:
            self.domains.append(domain)
            self.update_domains_in_db()
            return True
        return False

    def remove_domain(self, domain):
        """Remove a domain from the user's list of domains if present.

        Args:
            domain (str): The domain to remove.

        Returns:
            bool: True if domain was removed, False if it didn't exist.
        """
        if domain in self.domains:
            self.domains.remove(domain)
            self.update_domains_in_db()
            return True
        return False

    def update_domains_in_db(self):
        """Update the user's domains in the database."""
        db.users.update_one({"username": self.username}, {"$set": {"domains": self.domains}})

    @staticmethod
    def get_user_by_username(username):
        """Fetch a user by their username.

        Args:
            username (str): The username of the user.

        Returns:
            User: An instance of User if found, otherwise None.
        """
        user_data = db.service_users.find_one({"username": username})
        if user_data:
            user = User(user_data['_id'], user_data['username'], user_data['password'], hashed=True)
            user.domains = user_data.get('domains', [])
            return user
        return None
