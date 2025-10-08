import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar BASE_URL con fallback
T8_HOST = os.getenv("T8_HOST", "https://lzfs45.mirror.twave.io/lzfs45")
BASE_URL = T8_HOST + "/rest/"

class T8ApiClient:
    
    def __init__(self):
        self.session = requests.Session()
        self.token = None

    def login_with_credentials(self, username, password):
        # Primero obtenemos la página de login para obtener cualquier token CSRF
        login_page_url = "https://lzfs45.mirror.twave.io/lzfs45/signin"
        
        # Hacemos login usando form data como el navegador
        payload = {
            "username": username, 
            "password": password,
            "signin": "Sign In"
        }
        
        try:
            response = self.session.post(login_page_url, data=payload)
            # Si el login es exitoso, probablemente nos redirige o nos da una cookie
            if response.status_code == 200 and "Invalid Username or Password" not in response.text:
                return True
            elif "Invalid Username or Password" in response.text:
                print("Error: Credenciales inválidas")
                return False
            else:
                print(f"Error de login: {response.status_code} - {response.text[:100]}")
                return False
        except Exception as e:
            print(f"Error en la petición de login: {e}")
            return False

    def check_ok_response(self, response):
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                print(f"Error parsing JSON: {e}")
                print(f"Full response: {response.text}")
                return None
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return None

    def list_available_waves(self):
        url = BASE_URL + "waves/"
        response = self.session.get(url)
        data = self.check_ok_response(response)
        if not data:
            return 
        
        # Saco los url de las máquinas con sus puntos y modos de procesamiento 
        waves = data.get("_items", [])
        print(f"\nEncontradas {len(waves)} ondas disponibles:\n")
        
        for i, wave in enumerate(waves, 1):
            # Extraer información del URL
            wave_url = wave.get("_links", {}).get("self", "")
            if wave_url:
                # Extraer machine, point, mode del URL
                # Formato esperado: .../waves/MACHINE/POINT/MODE/
                parts = wave_url.rstrip('/').split('/')
                if len(parts) >= 3:
                    machine = parts[-3]
                    point = parts[-2] 
                    mode = parts[-1]
                    print(f"{i:2d}. Machine: {machine}, Point: {point}, Mode: {mode}")
                    print(f"    URL: {wave_url}")
                else:
                    print(f"{i:2d}. URL: {wave_url}")

    def listWaves(self, machine, point, procMode):
        url = BASE_URL + "waves/"+machine+"/"+point+"/"+procMode
        response = self.session.get(url)
        data = self.check_ok_response(response)
        if not data:
            return 
        for wave in data.get("_items", []):
            print(wave.get("_links", {}).get("self", "No URL found")+" - "+self.getFormatedWaveDate(wave))
            print("#========================================#")

    def getFormatedWaveDate(self, wave) :
        url=wave.get("_links", {}).get("self")
        #ahora parseo el url y saco la fecha
        url_parts=url.split('/')
        fecha=url_parts[-1]  # Sabiendo que la fecha es el timestamp del final
        #Ahora se le da un formato ISO 8601 al timestamp como esta de ejemplo: 2025-01-01T12:00:00
        try:
            # Convertir timestamp a entero y luego a datetime
            timestamp = int(fecha)
            fecha_formateada = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%dT%H:%M:%S')
        except (ValueError, OSError):
            # Si hay error en la conversión, retornar el timestamp original
            fecha_formateada = fecha
        return fecha_formateada