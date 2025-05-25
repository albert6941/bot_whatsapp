# 🤖 Bot de WhatsApp Automatizado con Python y Node.js

Este proyecto monitorea nuevas órdenes desde una base de datos MySQL y envía notificaciones automáticas a grupos de WhatsApp, según el cliente o estación detectada.

---

## 📁 Estructura del Proyecto

bot-whatsapp/
│
├── bot-server.js # Servidor Node.js que conecta con WhatsApp
├── Whatsapp.py # Script principal en Python
├── Clientes_Grupos.csv # Archivo CSV que relaciona clientes con grupos
├── historial_ordenes.json # Historial de órdenes notificadas
├── package.json # Dependencias Node.js
├── tokens/ # Carpeta que guarda la sesión de WhatsApp (evita reescanear QR)
├── README.md # Este archivo


---

## 🚀 Requisitos

- Node.js (v16+)
- Python 3.9+
- pip (gestor de paquetes Python)

---

## 🧰 Instalación

1. **Clona o descomprime el proyecto en tu máquina:**

   ```bash
   git clone https://github.com/tu-usuario/bot-whatsapp.git
   cd bot-whatsapp
2. **Instala dependencias de Node.js:**
   npm install

3. **Instala dependencias de Python:**
pip install pandas mysql-connector-python requests

**📝 Notas**
Si el archivo historial_ordenes.json no existe, se crea automáticamente.

La sesión de WhatsApp se guarda en la carpeta tokens/. Puedes copiarla a otra máquina, pero si cambia mucho el entorno podrías tener que escanear el QR nuevamente.

El archivo Clientes_Grupos.csv debe contener al menos las columnas: Cliente, Estacion, Id (que es el ID del grupo de WhatsApp).


