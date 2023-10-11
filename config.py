from dotenv import load_dotenv
import os

load_dotenv()

MONGOPASS = os.getenv("MONGOPASS")
MONGOUSER = os.getenv("MONGOUSER")
PRUEBA = os.getenv("PRUEBA")