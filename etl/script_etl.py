import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Definimos una lista con los archivos que necesitamos descargar
ARCHIVOS_A_DESCARGAR = [
    {
        "nombre": "precios_surtidor_actual.csv",
        "url": "http://datos.energia.gob.ar/dataset/1c181390-5045-475e-94dc-410429be4b17/resource/80ac25de-a44a-4445-9215-090cf55cfda5/download/precios-en-surtidor-resolucin-3142016.csv"
    },
    {
        "nombre": "importaciones-exportaciones-a-partir-del-2016-.csv",
        "url": "http://datos.energia.gob.ar/dataset/5bdc436c-60d4-4c86-98ab-59834d047700/resource/ea145b70-c78f-4c94-8df0-27e3acfda3fc/download/importaciones-exportaciones-a-partir-del-2016-.csv"
    }
]

DIR_RAW = "data/raw"

def crear_carpetas():
    os.makedirs(DIR_RAW, exist_ok=True)

def descargar_csv_robusto(url, nombre_archivo):
    crear_carpetas()
    ruta_salida = os.path.join(DIR_RAW, nombre_archivo)
    
    print(f"\nIniciando descarga de: {nombre_archivo}")
    print(f"Desde: {url}")
    
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=2, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        response = session.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        tamano_total = int(response.headers.get('content-length', 0))
        descargado = 0
        
        with open(ruta_salida, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192*4):
                if chunk:
                    f.write(chunk)
                    descargado += len(chunk)
                    if tamano_total > 0:
                        porcentaje = (descargado / tamano_total) * 100
                        print(f"Descargando {nombre_archivo}... {porcentaje:.2f}% completado", end='\r')
                        
        print(f"\n¡Descarga exitosa! Archivo guardado en: {ruta_salida}")
        return True

    except Exception as e:
        print(f"\nError al descargar {nombre_archivo}: {e}")
        return False

if __name__ == "__main__":
    for item in ARCHIVOS_A_DESCARGAR:
        # Validar por si quedó pendiente pegar el enlace del segundo archivo
        if "AQUÍ_PEGAS" in item["url"]:
            print(f"\n[Aviso] Saltando '{item['nombre']}' porque aún no configuraste su URL.")
            continue
        descargar_csv_robusto(item["url"], item["nombre"])
