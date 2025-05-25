const socket = new WebSocket("ws://127.0.0.1:8000/ws");

socket.onopen = () => {
  console.log("Conectado al servidor WebSocket");

  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      const video = document.getElementById('video');
      video.srcObject = stream;
      video.play();
    })
    .catch(err => console.error("Error al acceder a la cámara:", err));
};

document.getElementById("startRecognition").addEventListener("click", async () => {
  const nombre = document.getElementById("nombre").value.trim();

  if (!nombre) {
    alert("⚠️ Debes ingresar un nombre antes de iniciar el reconocimiento.");
    return;
  }

  const video = document.getElementById('video');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const ctx = canvas.getContext('2d');

  // Función para capturar una imagen y devolverla en formato base64
  const capturarImagen = () => {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL('image/jpeg').split(',')[1];  // ✅ Elimina el prefijo "data:image/jpeg;base64,"
  };

  alert("📸 Capturando imagen normal... Mantén tu rostro relajado.");
  const imagenNormal = capturarImagen();

  alert("😃 Capturando imagen sonriendo... Sonríe!");
  await new Promise(resolve => setTimeout(resolve, 2000));  // Espera 2 segundos para que el usuario sonría
  const imagenSonrisa = capturarImagen();

  alert("↩️ Capturando imagen girando... Gira levemente la cabeza.");
  await new Promise(resolve => setTimeout(resolve, 2000));  // Espera 2 segundos para el giro
  const imagenGiro = capturarImagen();

  console.log("📤 Enviando datos de registro:", nombre);

  socket.send(JSON.stringify({
    id_empleado: nombre,
    imagen_normal: imagenNormal,
    imagen_sonrisa: imagenSonrisa,
    imagen_giro: imagenGiro,
    registrar: true
  }));
});
