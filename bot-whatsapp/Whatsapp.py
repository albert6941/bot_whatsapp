import mysql.connector
from mysql.connector import Error
import pandas as pd
import time
import json
import os
import requests
from datetime import datetime, timedelta
import unicodedata

# Configuración
DB_CONFIG = {
    'host': 'ip_de_la_base',
    'port': 3306,
    'database': 'Nombre_db',
    'user': 'usuario_db',
    'password': 'contraseña_db'
}

INTERVALO_SEGUNDOS = 30
DIAS_ATRAS = 1
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORIAL_FILE = os.path.join(SCRIPT_DIR, "historial_ordenes.json")
CSV_CLIENTES_GRUPOS = os.path.join(SCRIPT_DIR, "Clientes_Grupos.csv")
TECNICOS_JSON = os.path.join(SCRIPT_DIR, "tecnicos_remotos.json")

ESTATUS_PERMITIDOS = [
    "Incidencia escalada a IR",
    "Intervencion Remota"
]

# 🔤 Función para normalizar texto (elimina acentos y pone en minúsculas)
def normalizar(texto):
    if not texto:
        return ""
    texto = texto.strip().lower()
    texto = ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )
    texto = ' '.join(texto.split())  # elimina espacios múltiples
    return texto

# Función para convertir fecha YYYYMMDD a formato dd/mm/yyyy legible
def fecha_legible(fecha_str):
    try:
        fecha_dt = datetime.strptime(str(fecha_str), "%Y%m%d")
        return fecha_dt.strftime("%d/%m/%Y")
    except Exception:
        return fecha_str  # si no puede convertir, regresa el original

# Función para enviar mensaje al bot de WhatsApp
def enviar_mensaje_whatsapp(grupo_id, mensaje):
    try:
        response = requests.post("http://localhost:3000/enviar-mensaje", json={
            "grupo_id": grupo_id,
            "mensaje": mensaje
        })

        if response.status_code == 200:
            data = response.json()
            if data.get("ok") == True:
                print("✅ Mensaje enviado correctamente a WhatsApp.")
                return True  # Solo aquí consideramos que se envió
            else:
                print(f"❌ Error al enviar mensaje desde servidor: {data.get('error')}")
                return False
        else:
            print(f"❌ Error HTTP al enviar mensaje: {response.status_code}")
            return False
    except Exception as e:
        print("❌ Error en la conexión con el bot de WhatsApp:", e)
        return False

# Cargar técnicos remotos desde JSON
def cargar_tecnicos_remotos():
    try:
        with open(TECNICOS_JSON, 'r') as f:
            data = json.load(f)
            return [normalizar(nombre) for nombre in data.get("tecnicos", [])]
    except Exception as e:
        print("⚠️ Error al cargar técnicos remotos desde JSON:", e)
        return []

# Cargar historial
def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r") as f:
            return json.load(f)
    return []

# Guardar historial
def guardar_historial(historial):
    with open(HISTORIAL_FILE, "w") as f:
        json.dump(historial[-200:], f)

# Validar si ya fue notificado
def ya_notificado(historial, orden_id, tecnico, estatus):
    clave = f"{orden_id}-{tecnico}-{estatus}"
    return clave in historial

# Obtener grupo de WhatsApp desde CSV
def obtener_grupo_id(cliente, estacion, df):
    cliente = normalizar(cliente)
    estacion = normalizar(estacion)

    for _, row in df.iterrows():
        cliente_csv = normalizar(str(row['Cliente']))
        estacion_csv = normalizar(str(row['Estacion']))
        if cliente and cliente == cliente_csv:
            return row['Id']
        elif not cliente and estacion and estacion == estacion_csv:
            return row['Id']
    return None

# Obtener fecha en formato YYYYMMDD
def fecha_formato_mysql(date_obj):
    return date_obj.strftime("%Y%m%d")

# Obtener órdenes recientes
def obtener_ordenes_recientes():
    fecha_limite = fecha_formato_mysql(datetime.now() - timedelta(days=DIAS_ATRAS))
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            cursor = connection.cursor()
            query = f"""
                SELECT
                    o.IdOrden,
                    c.NoIdentidad AS Estacion,
                    c.Nombre AS Cliente,
                    t.Nombre AS NombreTecnico,
                    t.ApellidoPaterno AS ApellidoTecnico,
                    e.Descripcion AS Estatus,
                    o.FechaCaptura,
                    o.FechaAsignaTecnico
                FROM srv_ordenes_servicio o
                LEFT JOIN clientes c ON o.IdCliente = c.IdCliente
                LEFT JOIN srv_tecnicos t ON o.IdTecnico = t.IdTecnico
                LEFT JOIN srv_estatus e ON o.Estatus = e.IdStatus
                WHERE o.FechaAsignaTecnico >= '{fecha_limite}'
                ORDER BY o.IdOrden DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
    except Error as e:
        print("❌ Error al conectar o consultar MySQL:", e)
        return []
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()

# Construir mensaje
def construir_mensaje(orden_id, estacion, cliente, tecnico, estatus):
    mensaje = "📢 "
    
    if cliente and cliente.strip() and estacion and estacion.strip():
        mensaje += f"Estimado cliente {cliente.strip()} de la estación {estacion.strip()},\n\n "
    elif cliente and cliente.strip():
        mensaje += f"Estimado cliente {cliente.strip()}, \n\n "
    elif estacion and estacion.strip():
        mensaje += f"Estimado de la estación {estacion.strip()},\n\n "
    else:
        mensaje += "Estimado cliente, \n\n"
    
    mensaje += f"Le informamos que la **Orden de Servicio #{orden_id}** ha sido asignada al área de **Intervenciones Remotas** 🛠️. "
    mensaje += f"Actualmente está siendo gestionada por **{tecnico}**.\n\n"
    
    mensaje += "El incidente reportado requiere un análisis más detallado para identificar su causa raíz y aplicar la solución más adecuada. "
    mensaje += "Nuestro equipo está trabajando en ello y le mantendremos informado tan pronto contemos con una actualización. ✅\n\n"
    
    mensaje += "Agradecemos su comprensión y quedamos atentos para cualquier consulta adicional. 🙌"

    return mensaje

# Main
def main():
    print("🚀 Iniciando monitoreo de órdenes modificadas cada 30 segundos...")
    historial = cargar_historial()
    tecnicos_remotos = cargar_tecnicos_remotos()

    try:
        df_grupos = pd.read_csv(CSV_CLIENTES_GRUPOS)
    except Exception as e:
        print("❌ Error al leer el archivo CSV:", e)
        return

    while True:
      
        ordenes = obtener_ordenes_recientes()
        
        # --- GUARDAR TODO EL DETALLE EN UN ARCHIVO PARA DEBUG ---
        with open("debug_ordenes.txt", "w", encoding="utf-8") as f:
            for orden in ordenes:
                orden_id, estacion, cliente, nombre_tec, apellido_tec, estatus, fecha_captura, fecha_asigna = orden
                tecnico_completo = f"{nombre_tec or ''} {apellido_tec or ''}".strip()
                tecnico_normalizado = normalizar(tecnico_completo)
                estatus_normalizado = normalizar(estatus)

                fecha_captura_legible = f"{str(fecha_captura)[:4]}/{str(fecha_captura)[4:6]}/{str(fecha_captura)[6:]}"
                fecha_asigna_legible = f"{str(fecha_asigna)[:4]}/{str(fecha_asigna)[4:6]}/{str(fecha_asigna)[6:]}"

                linea = (f"Orden #{orden_id} | Técnico: '{tecnico_completo}' → '{tecnico_normalizado}' | "
                         f"Estatus: '{estatus_normalizado}' | FechaCaptura: {fecha_captura_legible} | FechaAsignaTecnico: {fecha_asigna_legible}\n")
                f.write(linea)
        # --- FIN DE DEBUG ---
        

def main():
    print("🚀 Iniciando monitoreo de órdenes modificadas cada 30 segundos...")
    historial = cargar_historial()
    tecnicos_remotos = cargar_tecnicos_remotos()

    try:
        df_grupos = pd.read_csv(CSV_CLIENTES_GRUPOS)
    except Exception as e:
        print("❌ Error al leer el archivo CSV:", e)
        return

    while True:
        ordenes = obtener_ordenes_recientes()

        # --- GUARDAR TODO EL DETALLE EN UN ARCHIVO PARA DEBUG ---
        with open("debug_ordenes.txt", "w", encoding="utf-8") as f:
            for orden in ordenes:
                orden_id, estacion, cliente, nombre_tec, apellido_tec, estatus, fecha_captura, fecha_asigna = orden
                tecnico_completo = f"{nombre_tec or ''} {apellido_tec or ''}".strip()
                tecnico_normalizado = normalizar(tecnico_completo)
                estatus_normalizado = normalizar(estatus)

                fecha_captura_legible = f"{str(fecha_captura)[:4]}/{str(fecha_captura)[4:6]}/{str(fecha_captura)[6:]}"
                fecha_asigna_legible = f"{str(fecha_asigna)[:4]}/{str(fecha_asigna)[4:6]}/{str(fecha_asigna)[6:]}"

                linea = (f"Orden #{orden_id} | Técnico: '{tecnico_completo}' → '{tecnico_normalizado}' | "
                         f"Estatus: '{estatus_normalizado}' | FechaCaptura: {fecha_captura_legible} | FechaAsignaTecnico: {fecha_asigna_legible}\n")
                f.write(linea)
        # --- FIN DE DEBUG ---

        for orden in ordenes:
            orden_id, estacion, cliente, nombre_tec, apellido_tec, estatus, fecha_captura, fecha_asigna = orden
            tecnico_completo = f"{nombre_tec or ''} {apellido_tec or ''}".strip()
            tecnico_normalizado = normalizar(tecnico_completo)
            estatus_normalizado = normalizar(estatus)

            # 🧪 Depuración con fechas legibles
            print(f"\n🔍 Orden #{orden_id} | Técnico: '{tecnico_completo}' → '{tecnico_normalizado}' | Estatus: '{estatus_normalizado}'")
            print(f"   📅 FechaCaptura: {fecha_legible(fecha_captura)} | FechaAsignaTecnico: {fecha_legible(fecha_asigna)}")

            if tecnico_normalizado in tecnicos_remotos and estatus_normalizado in [normalizar(e) for e in ESTATUS_PERMITIDOS]:
                clave_historial = f"{orden_id}-{tecnico_normalizado}-{estatus_normalizado}"

                if not ya_notificado(historial, orden_id, tecnico_normalizado, estatus_normalizado):
                    mensaje = construir_mensaje(
                        orden_id,
                        estacion,
                        cliente,
                        tecnico_completo,
                        estatus
                    )
                    grupo_id = obtener_grupo_id(cliente, estacion, df_grupos)

                    print("\n📲 Mensaje generado:\n", mensaje)

                    if grupo_id:
                        print(f"✅ Enviando al grupo ID: {grupo_id}")
                        enviado = enviar_mensaje_whatsapp(grupo_id, mensaje)
                        if enviado:
                            historial.append(clave_historial)
                            guardar_historial(historial)
                        else:
                            print("⚠️ No se guardó en historial porque el envío falló.")
                    else:
                        print("⚠️ Grupo no encontrado para esta orden.")
                else:
                    print(f"⏩ Orden #{orden_id} ya notificada.")
            else:
                print(f"🔄 Orden #{orden_id} aún no cumple condiciones para enviar mensaje.")

        time.sleep(INTERVALO_SEGUNDOS)

if __name__ == "__main__":
    main()
