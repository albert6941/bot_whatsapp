const wppconnect = require('@wppconnect-team/wppconnect');

wppconnect
  .create({
    session: 'mi_sesion',
    headless: true
    //autoClose: 300
  })
  .then((client) => listarGrupos(client))
  .catch((error) => console.error('❌ Error al iniciar sesión:', error));

async function listarGrupos(client) {
  console.log('✅ Sesión iniciada con éxito');

  setTimeout(async () => {
    try {
      const chats = await client.listChats(); 
      const grupos = chats.filter(chat => chat.isGroup);

      if (grupos.length === 0) {
        console.warn('⚠️ No se encontraron grupos. Asegúrate de que la cuenta esté en al menos un grupo.');
        return;
      }

      console.log(`📋 Se encontraron ${grupos.length} grupos:\n`);
      grupos.forEach((grupo, index) => {
        console.log(`${index + 1}. ${grupo.name} => ID: ${grupo.id._serialized}`);
      });

    } catch (error) {
      console.error('❌ Error al obtener los grupos:', error);
    }
  }, 10000); // Esperamos un poco para que la sesión se estabilice
}
