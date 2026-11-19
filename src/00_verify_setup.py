
import sqlite3

import pandas as pd
import numpy as np
from faker import Faker
import openpyxl
import pytest

print("FINANCEOPS SENTINEL - ENVIRONMENT CHECK")
print("-" * 45)

print("Pandas:", pd.__version__)
print("NumPy:", np.__version__)
print("Faker:", Faker.__module__)
print("OpenPyXL:", openpyxl.__version__)
print("Pytest:", pytest.__version__)
print("SQLite:", sqlite3.sqlite_version)

print("-" * 45)
print("SUCCESS: All libraries imported successfully!")
