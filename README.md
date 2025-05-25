# 🤖 Bot de WhatsApp con WPPConnect

Este proyecto implementa un bot de WhatsApp utilizando [WPPConnect](https://github.com/wppconnect-team/wppconnect), diseñado para:

- 🔁 Automatizar el envío de mensajes a grupos de WhatsApp.
- 📋 Obtener una lista de todos los grupos y sus IDs.
- 🚀 Servir una API HTTP que permite enviar mensajes vía POST.
- 💡 Mantener una sesión activa de WhatsApp de manera robusta.

---

## 📂 Estructura del proyecto

| Archivo            | Descripción                                                                 |
|--------------------|-----------------------------------------------------------------------------|
| `bot-server.js`    | Servidor principal Express que recibe peticiones y envía mensajes a grupos. |
| `index.js`         | Script para listar todos los grupos y sus IDs.                              |
| `Whatsapp.py`      | (Opcional) Script de Python para interacción adicional, si lo usas.         |

---

## 🚀 Instalación

### 1. Clona el repositorio

```bash
git clone https://github.com/wppconnect-team/wppconnect
cd tu_repositorio

## 🚀 Instala dependencias

npm install

⚙️ Uso

Iniciar el bot (Servidor API)

node bot-server.js

El servidor escuchará en:
http://localhost:3000/enviar-mensaje

para poder obtener los id de grupos de whatsapp correr 
node index.js

veras algo asi 
1. Grupo Ventas => ID: 1234567890-123456@g.us
2. Grupo Soporte => ID: 0987654321-654321@g.us

## ⚠️ Archivos importantes (NO incluidos)

### 🔐 `clientes.csv`

Crea un archivo llamado `clientes.csv` con el siguiente formato:

```csv
cliente,estacion,id
Cliente 1,Estación Norte,1234567890-123456@g.us
Cliente 2,Estación Sur,0987654321-654321@g.us

MIT License
Desarrollado por Alberto Hernandez Martinez 
Proyecto basado en WPPConnect
