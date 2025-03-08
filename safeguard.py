import subprocess
import platform
import re
import time
import logging
from collections import defaultdict
from datetime import datetime, timedelta
import os

# Set up logging to log the actions
logging.basicConfig(filename="fail2ban_simulator.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Configuration
MAX_FAILED_ATTEMPTS = 5  # Max number of failed attempts before blocking
BLOCK_TIME = 300  # Block time in seconds (5 minutes)
WINDOW_TIME = 600  # Time window in seconds (10 minutes)
LOG_FILES = ["/var/log/auth.log", "/var/log/apache2/access.log", "/var/log/nginx/access.log"]  # Multiple log files to monitor

# Custom rules for different services (SSH, Apache, Nginx, etc.)
CUSTOM_RULES = {
    "ssh": {
        "regex": r"Failed\s+password\s+for\s+invalid\s+user\s+(\S+)",
        "max_attempts": 5
    },
    "apache": {
        "regex": r"(\d+\.\d+\.\d+\.\d+) - - \[.\] \"(GET|POST|HEAD).*HTTP/.\" 401",
        "max_attempts": 3
    },
    "nginx": {
        "regex": r"(\d+\.\d+\.\d+\.\d+) - - \[.\] \"(GET|POST|HEAD).*HTTP/.\" 401",
        "max_attempts": 3
    }
}

# Dictionary to store failed attempts and block times
failed_attempts = defaultdict(list)


def is_valid_ip(ip):
    """Check if the IP address is valid."""
    regex = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    return re.match(regex, ip) is not None


def block_ip(ip_address):
    """Block an IP address."""
    os_type = platform.system().lower()
    
    if not is_valid_ip(ip_address):
        print(f"Error: {ip_address} is not a valid IP address.")
        logging.error(f"Invalid IP address attempted: {ip_address}")
        return

    try:
        if os_type == "windows":
            subprocess.run(["powershell", "-Command", f"New-NetFirewallRule -DisplayName 'Block IP' -Direction Inbound -Action Block -RemoteAddress {ip_address}"], check=True)
            print(f"Successfully blocked IP: {ip_address} on Windows")
            logging.info(f"Blocked IP: {ip_address} on Windows")
        
        elif os_type == "linux":
            subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip_address, "-j", "DROP"], check=True)
            print(f"Successfully blocked IP: {ip_address} on Linux")
            logging.info(f"Blocked IP: {ip_address} on Linux")
        
        else:
            print(f"Unsupported OS: {os_type}")
            logging.error(f"Unsupported OS: {os_type}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while blocking IP: {e}")
        logging.error(f"Error blocking IP {ip_address}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.error(f"Unexpected error: {e}")


def unblock_ip(ip_address):
    """Unblock an IP address."""
    os_type = platform.system().lower()

    if not is_valid_ip(ip_address):
        print(f"Error: {ip_address} is not a valid IP address.")
        logging.error(f"Invalid IP address attempted: {ip_address}")
        return

    try:
        if os_type == "windows":
            subprocess.run(["powershell", "-Command", f"Remove-NetFirewallRule -DisplayName 'Block IP' -RemoteAddress {ip_address}"], check=True)
            print(f"Successfully unblocked IP: {ip_address} on Windows")
            logging.info(f"Unblocked IP: {ip_address} on Windows")
        
        elif os_type == "linux":
            subprocess.run(["sudo", "iptables", "-D", "INPUT", "-s", ip_address, "-j", "DROP"], check=True)
            print(f"Successfully unblocked IP: {ip_address} on Linux")
            logging.info(f"Unblocked IP: {ip_address} on Linux")
        
        else:
            print(f"Unsupported OS: {os_type}")
            logging.error(f"Unsupported OS: {os_type}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while unblocking IP: {e}")
        logging.error(f"Error unblocking IP {ip_address}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        logging.error(f"Unexpected error: {e}")


def monitor_logs():
    """Monitor multiple log files for suspicious activity and block IPs if necessary."""
    global failed_attempts
    
    try:
        for log_file in LOG_FILES:
            if not os.path.exists(log_file):
                logging.error(f"Log file {log_file} does not exist!")
                continue

            with open(log_file, "r") as file:
                lines = file.readlines()
                for line in lines:
                    for service, rule in CUSTOM_RULES.items():
                        # Match the regex rule for the service
                        ip_match = re.search(rule["regex"], line)
                        if ip_match:
                            ip_address = ip_match.group(1)
                            timestamp = datetime.now()

                            # Keep track of failed attempts and their timestamps
                            failed_attempts[ip_address].append(timestamp)

                            # Clean up old failed attempts
                            failed_attempts[ip_address] = [time for time in failed_attempts[ip_address] if (timestamp - time).seconds < WINDOW_TIME]

                            # Block IP if the threshold is reached
                            if len(failed_attempts[ip_address]) >= rule["max_attempts"]:
                                # Check if IP is already blocked
                                current_time = datetime.now()
                                block_time = current_time + timedelta(seconds=BLOCK_TIME)
                                block_ip(ip_address)
                                logging.info(f"Blocking IP {ip_address} due to {len(failed_attempts[ip_address])} failed attempts in {service} logs.")
                                failed_attempts[ip_address] = []  # Clear attempts after blocking

                                # Wait for the block time to pass
                                time.sleep(BLOCK_TIME)
                                unblock_ip(ip_address)  # Unblock after block time passes
                                logging.info(f"Unblocked IP {ip_address} after {BLOCK_TIME} seconds.")
    
    except Exception as e:
        print(f"Error while monitoring logs: {e}")
        logging.error(f"Error while monitoring logs: {e}")


if _name_ == "_main_":
    monitor_logs()
