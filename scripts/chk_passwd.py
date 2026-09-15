#!/usr/bin/env python

import sys
import hashlib

# -----------------------------------------------------------------------------

if len(sys.argv) == 2:
    password = sys.argv[1]
else:
    password = "Very-Secret"


# -----------------------------------------------------------------------------


hashed_password = hashlib.new("sha256", password.encode("utf-8")).hexdigest()

print()
print(f"          password |{password}|")
print(f"   hashed password |{hashed_password}|")
print()


