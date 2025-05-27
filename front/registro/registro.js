const socket = new WebSocket("ws://127.0.0.1:8000/ws");

socket.onopen = () => {
  console.log("✅ Conectado al servidor WebSocket");

  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      const video = document.getElementById('video');
      video.srcObject = stream;
      video.play();
    })
    .catch(err => console.error("❌ Error al acceder a la cámara:", err));
};

document.getElementById("startRecognition").addEventListener("click", async () => {
  const nombre = document.getElementById("nombre").value.trim();
  if (!nombre) {
    alert("⚠️ Debes ingresar un nombre antes de iniciar el registro.");
    return;
  }

  const video = document.getElementById('video');
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');

  const capturarImagen = () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg').split(',')[1];  // Quitar prefijo base64
  };

  // Enviar primer mensaje con ID de empleado
  socket.send(JSON.stringify({ id_empleado: nombre, registrar: true }));

  let intentos = {
    sonrisa: 0,
    giro: 0
  };

  const esperar = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  socket.onmessage = async (event) => {
    const mensaje = event.data;
    console.log("📩 Mensaje del servidor:", mensaje);

    if (mensaje.includes("normal")) {
      alert("📸 Capturando imagen normal... Mantén tu rostro relajado.");
      await esperar(500);
      const imagen = capturarImagen();
      socket.send(JSON.stringify({ imagen_normal: imagen }));
    }

    else if (mensaje.includes("sonrisa")) {
      intentos.sonrisa++;
      if (intentos.sonrisa > 1) {
        alert("😅 Intenta sonreír más claramente. Capturando nuevamente...");
      } else {
        alert("😃 Capturando imagen sonriendo... Sonríe!");
      }
      await esperar(500);
      const imagen = capturarImagen();
      socket.send(JSON.stringify({ imagen_sonrisa: imagen }));
    }

    else if (mensaje.includes("giro")) {
      intentos.giro++;
      if (intentos.giro > 1) {
        alert("↩️ Intenta girar más claramente tu cabeza. Capturando nuevamente...");
      } else {
        alert("↩️ Capturando imagen girando... Gira levemente la cabeza.");
      }
      await esperar(500);
      const imagen = capturarImagen();
      socket.send(JSON.stringify({ imagen_giro: imagen }));
    }

    else if (mensaje.includes("registrada correctamente")) {
      alert("✅ Registro completado con éxito.");
      intentos = { sonrisa: 0, giro: 0 };
    }

    else if (mensaje.includes("Error") || mensaje.includes("❌") || mensaje.includes("🚫")) {
      alert("⚠️ " + mensaje);
    }
  };
});
