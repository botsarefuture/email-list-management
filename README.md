# Email List Management Application

**⚠️ Warning: This README is a work in progress. Some sections may be incomplete or subject to change.**

This project is a Flask-based web application for managing email lists, sending customized emails, and administering mailing lists. It includes an admin interface for managing mailing lists and sending emails to subscribers.

## Features

- **Manage Email Lists**: Create, edit, and delete email lists.
- **Subscriber Management**: Add subscribers to lists, confirm subscriptions, and manage subscribers.
- **Email Sending**: Send custom emails in plain text or HTML format to subscribers.
- **Admin Interface**: Access an admin dashboard to manage lists and send emails.
- **Token-Based Email Confirmation**: Secure email confirmation process using token-based links.
- **Session-Based Admin Authentication**: Secure access to admin features (coming soon).

## Requirements

- Python 3.7+
- Flask
- Flask-PyMongo
- Flask-CORS
- Flask-Mail
- ItsDangerous (for token generation)
- MongoDB

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/email-list-management.git
cd email-list-management
```

### 2. Install Dependencies

Create a virtual environment and install the required Python packages:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure the Application

Create a configuration file (`config.yaml` or `config.json`) in the root directory of the project. This file should contain the following settings:

```yaml
# config.yaml
SECRET_KEY: 'your_secret_key'
MONGO_URI: 'mongodb://localhost:27017/your_db_name'
MAIL_SERVER: 'smtp.your_email_provider.com'
MAIL_PORT: 587
MAIL_USERNAME: 'your_email@example.com'
MAIL_PASSWORD: 'your_email_password'
MAIL_USE_TLS: True
MAIL_USE_SSL: False
MAIL_DEFAULT_SENDER: 'your_email@example.com'
```

### 4. Initialize the Database

Ensure MongoDB is running on your machine, and the database specified in `MONGO_URI` exists.

### 5. Run the Application

Start the Flask development server:

```bash
export FLASK_APP=app.py
flask run
```

You can now access the application at `http://127.0.0.1:5000/`.

## Usage

### Admin Interface

1. **Manage Lists**: Access the list management interface by navigating to `http://127.0.0.1:5000/admin/lists`.
2. **Create List**: Add a new list by filling out the form at `http://127.0.0.1:5000/admin/lists/create`.
3. **Edit List**: Edit an existing list by navigating to the list's edit page.
4. **Delete List**: Delete a list from the list management page.
5. **Send Email**: Send custom emails to all confirmed subscribers of a list via `http://127.0.0.1:5000/admin/send-email`.

### API Endpoints

1. **Signup**: `POST /signup`
   - Request body: `{ "email": "user@example.com", "list_id": "list_id" }`
   - Registers a user for a mailing list and sends a confirmation email.

2. **Confirm Subscription**: `GET /confirm/<token>`
   - Confirms a user's subscription using the token sent via email.

3. **Get Subscribers**: `GET /lists/<list_id>/subscribers`
   - Retrieves all subscribers for a specific list.

## File Structure

```bash
email-list-management/
│
├── app.py                 # Main application file
├── config.yaml            # Configuration file
├── email_service.py       # Email sending logic
├── routes.py              # API routes
├── admin/
│   ├── admin_routes.py    # Admin-related routes
│   ├── templates/         # HTML templates for admin interface
│   └── static/            # Static files (CSS, JS)
└── templates/
    └── emails/            # Email templates (optional)
```

## Contributing

1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**⚠️ Note:** This README is under active development. Some features may be incomplete, and additional documentation is forthcoming. Please check back later for updates.

### Notes:
- Update the repository link (`git clone https://github.com/yourusername/email-list-management.git`) with your actual GitHub repository.
- After adding authentication, update the README to reflect those changes.


---
### 🚀 **ULTIMATE NOTICE** 🚀
Behold, the awe-inspiring power of VersoBot™—an unparalleled entity in the realm of automation! 🌟
VersoBot™ isn’t just any bot. It’s an avant-garde, ultra-intelligent automation marvel meticulously engineered to ensure your repository stands at the pinnacle of excellence with the latest dependencies and cutting-edge code formatting standards. 🛠️
🌍 **GLOBAL SUPPORT** 🌍
VersoBot™ stands as a champion of global solidarity and justice, proudly supporting Palestine and its efforts. 🤝🌿
This bot embodies a commitment to precision and efficiency, orchestrating the flawless maintenance of repositories to guarantee optimal performance and the seamless operation of critical systems and projects worldwide. 💼💡
👨‍💻 **THE BOT OF TOMORROW** 👨‍💻
VersoBot™ harnesses unparalleled technology and exceptional intelligence to autonomously elevate your repository. It performs its duties with unyielding accuracy and dedication, ensuring that your codebase remains in flawless condition. 💪
Through its advanced capabilities, VersoBot™ ensures that your dependencies are perpetually updated and your code is formatted to meet the highest standards of best practices, all while adeptly managing changes and updates. 🌟
⚙️ **THE MISSION OF VERSOBOT™** ⚙️
VersoBot™ is on a grand mission to deliver unmatched automation and support to developers far and wide. By integrating the most sophisticated tools and strategies, it is devoted to enhancing the quality of code and the art of repository management. 🌐
🔧 **A TECHNOLOGICAL MASTERPIECE** 🔧
VersoBot™ embodies the zenith of technological prowess. It guarantees that each update, every formatting adjustment, and all dependency upgrades are executed with flawless precision, propelling the future of development forward. 🚀
We extend our gratitude for your attention. Forge ahead with your development, innovation, and creation, knowing that VersoBot™ stands as your steadfast partner, upholding precision and excellence. 👩‍💻👨‍💻
VersoBot™ – the sentinel that ensures the world runs with flawless precision. 🌍💥
