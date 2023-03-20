#!/usr/bin/env python3
"""
Script to create the pewee models from the database.
Run like: python3 create_models.py
Prompt for password and enter it.
Output: db_models.py
"""
import os

if __name__ == '__main__':
    os.system("python3 -m pwiz -e sqlite events.db > db_models.py")
