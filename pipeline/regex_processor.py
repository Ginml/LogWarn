import re
def regex_classification(log_message):
    # Clean the message: remove extra quotes and whitespace
    cleaned_message = log_message.strip().strip('"').strip()
    
    patterns = {
        r"User User\d+ logged (in|out).": "User Action",
        r"Backup (started|ended) at .*": "System Notification",
        r"Backup completed successfully.": "System Notification",
        r"System updated to version .*": "System Notification",
        r"File .* uploaded successfully by user .*": "System Notification",
        r"Disk cleanup completed successfully.": "System Notification",
        r"System reboot initiated by user .*": "System Notification",
        r"Account with ID .* created by .*": "User Action",
        r"User \d+ made multiple incorrect login attempts": "Security Alert",
        r"Data replication task (for|failed) .*": "Error",
        r"Account Account(\d+).*login.*": "Security Alert",
        r"Server \d+ experienced potential security incident, review required": "Security Alert"
    }
    for pattern, label in patterns.items():
        if re.match(pattern, cleaned_message, re.IGNORECASE):
            return label
    return None

if __name__ == "__main__":
    test_logs = [
        "User User123 logged in.",
        "Backup started at 2023-10-01 02:00:00.",
        "System updated to version 1.2.3.",
        "File report.pdf uploaded successfully by user Alice.",
        "Disk cleanup completed successfully.",
        "System reboot initiated by user Admin.",
        "Account with ID 456 created by Admin.",
        "User 789 made multiple incorrect login attempts",
        "Data replication task for database XYZ failed due to timeout.",
        "Account Account42 had a failed login attempt from IP 192.168.1.1",
        "Server 12 experienced potential security incident, review required"
    ]
    for log in test_logs:
        print(f"Log: {log}\nClassified as: {regex_classification(log)}\n")