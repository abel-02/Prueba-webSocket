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

document.getElementById("startRecognition").addEventListener("click", () => {
  const nombre = document.getElementById("nombre").value.trim();

  if (!nombre) {
    alert("⚠️ Debes ingresar un nombre antes de iniciar el reconocimiento.");
    return;
  }

  const video = document.getElementById('video');
  const canvas = document.createElement('canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  const imageData = canvas.toDataURL('image/jpeg').split(',')[1];  // ✅ Elimina el prefijo

  console.log("📤 Enviando datos de registro:", nombre);
  socket.send(JSON.stringify({ nombre: nombre, imagen: imageData, registrar: true }));  // ✅ `registrar: true`
});

socket.onmessage = (event) => {
  console.log("📡 Respuesta del servidor:", event.data);
};