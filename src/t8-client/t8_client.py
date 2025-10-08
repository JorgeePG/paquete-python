import json
import os
from datetime import datetime

import requests
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar BASE_URL con fallback
T8_HOST = os.getenv("T8_HOST", "https://lzfs45.mirror.twave.io/lzfs45")
BASE_URL = T8_HOST + "/rest/"

class T8ApiClient:
    
    def __init__(self) -> None:
        self.session = requests.Session()
        self.token = None

    def login_with_credentials(self, username: str, password: str) -> bool:
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
            if (response.status_code == 200 and 
                "Invalid Username or Password" not in response.text):
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

    def check_ok_response(self, response: requests.Response) -> dict | None:
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

    def list_available_waves(self) -> None:
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
                parts = wave_url.rstrip("/").split("/")
                if len(parts) >= 3:
                    machine = parts[-3]
                    point = parts[-2] 
                    mode = parts[-1]
                    print(f"{i:2d}. Machine: {machine}, Point: {point}, Mode: {mode}")
                    print(f"    URL: {wave_url}")
                else:
                    print(f"{i:2d}. URL: {wave_url}")

    def list_waves(self, machine: str, point: str, procMode: str) -> None:
        url = BASE_URL + "waves/" + machine + "/" + point + "/" + procMode
        response = self.session.get(url)
        data = self.check_ok_response(response)
        if not data:
            return 
        for wave in data.get("_items", []):
            print(self.getFormatedWaveDate(wave))

    def list_spectra(self, machine: str, point: str, procMode: str) -> None:
        url = BASE_URL + "spectra/" + machine + "/" + point + "/" + procMode
        response = self.session.get(url)
        data = self.check_ok_response(response)
        if not data:
            return 
        for wave in data.get("_items", []):
            print(self.getFormatedWaveDate(wave))

    def get_wave(self, machine: str, point: str, procMode: str, 
                 date: int | None = 0) -> None:
        """
        Obtiene una onda específica o la más reciente si no se especifica fecha.
        Guarda la onda en un archivo JSON.
        
        Args:
            machine: ID de la máquina
            point: Punto de medida
            procMode: Modo de procesamiento
            date: Fecha en formato ISO 8601, timestamp, o None para la más reciente
        """
        try:
            if "T" in str(date):
                dt = datetime.fromisoformat(str(date))
                date = int(dt.timestamp())
            else:
                date = int(date)
        except ValueError:
            print("Error de formato:ISO 8601 (YYYY-MM-DDTHH:MM:SS) o timestamp entero.")
            return
        
        # Construir URL para obtener la onda específica
        url = (BASE_URL + "waves/" + machine + "/" + point + "/" + 
               procMode + "/" + str(date))
        response = self.session.get(url)
        data = self.check_ok_response(response)
        
        if not data:
            return
        
        # Guardar en archivo JSON
        self._save_wave_to_file(data, machine, point, procMode, date)
        
        # Mostrar información básica
        formatted_date = datetime.fromtimestamp(date).strftime("%Y-%m-%dT%H:%M:%S")
        print("Onda descargada exitosamente:")
        print(f"   Machine: {machine}")
        print(f"   Point: {point}")
        print(f"   Mode: {procMode}")
        print(f"   Timestamp: {date}")
        print(f"   Fecha: {formatted_date}")

    def get_latest_wave_timestamp(
        self, machine: str, point: str, procMode: str
    ) -> int | None:
        """Obtiene el timestamp de la onda más reciente 
        para la máquina/punto/modo especificados."""
        url = BASE_URL + "waves/" + machine + "/" + point + "/" + procMode
        response = self.session.get(url)
        data = self.check_ok_response(response)
        
        if not data or "_items" not in data:
            return None
            
        waves = data["_items"]
        if not waves:
            return None
            
        # Extraer todos los timestamps y encontrar el más reciente
        timestamps = []
        for wave in waves:
            wave_url = wave.get("_links", {}).get("self", "")
            if wave_url:
                try:
                    timestamp = int(wave_url.rstrip("/").split("/")[-1])
                    timestamps.append(timestamp)
                except (ValueError, IndexError):
                    continue
        
        return max(timestamps) if timestamps else None

    def save_wave_to_file(
        self, wave_data: dict, machine: str, point: str, procMode: str, timestamp: int
    ) -> None:
        """Guarda los datos de la onda en un archivo JSON."""
        import os
        
        # Crear directorio data/waves si no existe
        waves_dir = "data/waves"
        os.makedirs(waves_dir, exist_ok=True)
        
        # Crear nombre del archivo: wave_<MACHINE>_<POINT>_<PROC_MODE>_<TIMESTAMP>.json
        filename = f"wave_{machine}_{point}_{procMode}_{timestamp}.json"
        filepath = os.path.join(waves_dir, filename)
        
        # Guardar datos en archivo JSON
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(wave_data, f, indent=4, ensure_ascii=False)
            print(f"   Archivo guardado: {filepath}")
        except Exception as e:
            print(f"Error al guardar el archivo: {e}")

    def get_formatted_wave_date(self, wave: dict) -> str | None:
        url = wave.get("_links", {}).get("self")
        #ahora parseo el url y saco la fecha
        url_parts=url.split("/")
        fecha=url_parts[-1]  # Sabiendo que la fecha es el timestamp del final
        #Ahora se le da un formato ISO 8601 al timestamp 
        # como esta de ejemplo: 2025-01-01T12:00:00
        try:
            # Convertir timestamp a entero y luego a datetime
            timestamp = int(fecha)
            fecha_formateada = datetime.fromtimestamp(timestamp).strftime(
                "%Y-%m-%dT%H:%M:%S"
            )
        except (ValueError, OSError):
            # Si hay error en la conversión, retornar el timestamp original
            fecha_formateada = fecha
        return fecha_formateada