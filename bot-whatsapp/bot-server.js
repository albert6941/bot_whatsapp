const express = require('express');
const bodyParser = require('body-parser');
const { create } = require('@wppconnect-team/wppconnect');

let client;
let clienteIniciando = false;

// Función para iniciar el cliente
async function iniciarCliente() {
  if (clienteIniciando) return;
  clienteIniciando = true;

  try {
    console.log('🔄 Iniciando cliente de WhatsApp...');
    client = await create({
      session: 'mi_sesion',
      headless: true,
      browserArgs: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-extensions',
        '--disable-infobars',
        '--window-size=1280,800'
      ],
      puppeteerOptions: {
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu',
          '--disable-extensions',
          '--disable-infobars',
          '--window-size=1280,800'
        ]
      }
    });

    console.log('✅ Bot de WhatsApp listo');
    clienteIniciando = false;

    // Manejo de cambios de estado
    client.onStateChange((state) => {
      console.log('🔄 Estado del cliente:', state);
      if (['DISCONNECTED', 'UNPAIRED'].includes(state)) {
        console.log('⚠️ Cliente desconectado. Reiniciando...');
        reiniciarCliente();
      }
    });

  } catch (error) {
    console.error('❌ Error al iniciar cliente:', error.message);
    clienteIniciando = false;
    setTimeout(iniciarCliente, 5000);
  }
}

// Función para reiniciar el cliente
function reiniciarCliente() {
  if (client) {
    client.close().catch(() => {});
    client = null;
  }
  setTimeout(iniciarCliente, 5000);
}

iniciarCliente();

// Configuración del servidor Express
const app = express();
app.use(bodyParser.json());

// Ruta para enviar mensajes
app.post('/enviar-mensaje', async (req, res) => {
  const { grupo_id, mensaje } = req.body;

  console.log("📨 Mensaje recibido:");
  console.log("➡️ Grupo ID:", grupo_id);
  console.log("📝 Contenido:", mensaje);

  if (!client) {
    console.error("❌ Cliente no inicializado. Reintentando...");
    iniciarCliente(); // Intentamos reiniciar
     return res.status(200).json({ ok: false, error: 'Cliente no inicializado' });
  }

  try {
    await client.sendText(grupo_id, mensaje);
    console.log(`📤 Mensaje enviado al grupo ${grupo_id}`);
    res.status(200).json({ ok: true });
  } catch (error) {
    console.error('❌ Error al enviar mensaje:', error.message);
    reiniciarCliente(); // Reiniciamos cliente en error
    res.status(200).json({ ok: false, error: error.message });
  }
});

// Puerto del servidor
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`🚀 Servidor escuchando en http://localhost:${PORT}`);
});
