import os
import certifi
from pymongo import MongoClient
from dotenv import load_dotenv
import sys

# Redirect stdout/stderr to file
log_file = open("db_test_log.txt", "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

load_dotenv()

uri = os.getenv("MONGO_URI")
print(f"Testing URI: {uri.split('@')[1] if '@' in uri else 'HIDDEN'}", flush=True)

def test_connection(name, client):
    print(f"\n--- Testing {name} ---", flush=True)
    try:
        # Force a connection check with timeout
        client.admin.command('ismaster')
        print("✅ Connection Successful!", flush=True)
        print("Server Info:", client.server_info()['version'], flush=True)
        return True
    except Exception as e:
        print(f"❌ Connection Failed: {e}", flush=True)
        return False

# Attempt 1: Standard + Certifi
print("\nAttempt 1: Certifi", flush=True)
try:
    client = MongoClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    test_connection("Certifi", client)
except Exception as e:
    print(f"Init Failed: {e}", flush=True)

# Attempt 2: Insecure
print("\nAttempt 2: tlsAllowInvalidCertificates=True", flush=True)
try:
    client = MongoClient(uri, tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=5000)
    test_connection("Insecure", client)
except Exception as e:
    print(f"Init Failed: {e}", flush=True)

log_file.close()
