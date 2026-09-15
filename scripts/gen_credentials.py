#!/usr/bin/env python

import sys
import hashlib
import argparse
import secrets
import string

from uuid import uuid4

PASSWD_LEN = 30


# -----------------------------------------------------------------------------

parser = argparse.ArgumentParser(description="Generate and hash a password.")
parser.add_argument("-p", "--password", type=str, default=None,
                    help="Custom password to hash. If omitted, a random password is generated.")
parser.add_argument("-l", "--length", type=int, default=PASSWD_LEN,
                    help=f"Length of the generated password (default: {PASSWD_LEN}).")
args = parser.parse_args()


# -----------------------------------------------------------------------------

if args.password:
    password = args.password
else:
    # Generate a cryptographically secure random password
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for _ in range(args.length))

# -----------------------------------------------------------------------------

username        = uuid4()
hashed_password = hashlib.new("sha256", password.encode("utf-8")).hexdigest()

print()
print("Credentials:")
print(f"          username |{username}|")
print(f"          password |{password}|")
print(f"   hashed password |{hashed_password}|")
print()


# -----------------------------------------------------------------------------

