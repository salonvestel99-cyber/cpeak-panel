# -*- coding: utf-8 -*-
"""Geliştirme sunucusunu başlatır."""

import os
from dotenv import load_dotenv
load_dotenv()

from app import app
from models import init_db, seed_admin

if __name__ == "__main__":
    init_db()
    seed_admin()
    print("\n  >>> http://127.0.0.1:5000  adresinden açabilirsiniz.\n")
    app.run(debug=True, host="127.0.0.1", port=5000)
