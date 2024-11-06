import dns.resolver
import logging
import time
from DatabaseManager import DatabaseManager  # Ensure you import DatabaseManager for DB access
from usermodel import User  # Ensure you import User model for user handling

# Configure logging
logging.basicConfig(filename='dns_check.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_fresh_resolver():
    resolver = dns.resolver.Resolver()
    resolver.cache = None  # Disable cache
    resolver.nameservers = ['8.8.8.8']  # Specify alternative DNS server
    return resolver

def main(users):
    db = DatabaseManager().get_instance().get_db()  # Get the database instance

    for user in users:
        user._init_domains()
        domains = user.domains

        for domain in domains:
            results = check_dns_records(domain, user.txt_record)
            print(results)

            # If both TXT and SPF checks are successful, update the database
            if results['TXT'] and results['SPF']:
                update_domain_confirmation(db, domain)

def update_domain_confirmation(db, domain):
    # Update the confirmed status in the database for the specified domain
    try:
        db["db.domains"].update_one(
            {"domain": domain},  # Filter for the domain
            {"$set": {"confirmed": True}}  # Set confirmed to True
        )
        logging.info(f"Domain '{domain}' confirmed successfully.")
    except Exception as e:
        logging.error(f"Failed to update domain confirmation for {domain}: {e}")

def _any(iterable: list, value: str):
    for i in iterable:
        if i == value:
            return True
    
    return False

def check_dns_records(domain, txt_record):
    results = {
        'TXT': False,
        'SPF': False
    }

    try:
        # Check TXT record for luovamailist-auth
        resolver = get_fresh_resolver()
        txt_answers = resolver.resolve(f'luovamailist-auth.{domain}', 'TXT', raise_on_no_answer=False)
        length = len(list(txt_answers))
        if length == 0:
            raise
        actual_txt_values = [str(answer).strip('"') for answer in txt_answers]
        # Check if user's txt_record matches the found TXT records
        results['TXT'] = _any(actual_txt_values, txt_record)
        if results['TXT']:
            logging.info(f"TXT record '{txt_record}' is correctly set for luovamailist-auth.{domain}.")
        else:
            logging.warning(f"TXT record '{txt_record}' is missing or incorrect for luovamailist-auth.{domain}. Found: {actual_txt_values}")

    except Exception as e:
        logging.error(f"Failed to check TXT records for luovamailist-auth.{domain}: {e}")

    try:
        # Check SPF record for the domain
        spf_answers = dns.resolver.resolve(domain, 'TXT', raise_on_no_answer=False)
        spf_record = [str(answer) for answer in spf_answers if 'v=spf1' in str(answer)]
        length = len(list(spf_answers))
        if length == 0:
            raise
        # Check if include:mailist.luova.club exists in the SPF record
        results['SPF'] = any('include:mailist.luova.club' in record for record in spf_record)
        if results['SPF']:
            logging.info(f"SPF record is correctly set for {domain}.")
        else:
            logging.warning(f"SPF record 'include:mailist.luova.club' is missing or incorrect for {domain}. Found: {spf_record}")

    except Exception as e:
        logging.error(f"Failed to check SPF records for {domain}: {e}")

    return results
    
if __name__ == "__main__":
    users = list(DatabaseManager().get_instance().get_db()["service_users"].find())
    _users = [User.get_user_by_username(user["username"]) for user in users]  
    main(_users)
