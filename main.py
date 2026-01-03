import streamlit as st
import sys
import os

# Redirect or Import from frontend
# This ensures that 'streamlit run main.py' uses the new architecture
cur_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_dir, "frontend"))

from frontend.main import main

if __name__ == "__main__":
    main()
