const socket = new WebSocket("ws://127.0.0.1:8000/ws");

socket.onopen = () => {
  console.log("Conectado al servidor WebSocket");

  navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
      const video = document.getElementById('video');
      video.srcObject = stream;
      video.play();
      console.log("Cámara activada correctamente");

      startStreaming(video); // Aseguramos que la función se ejecuta
      console.log("Iniciando transmisión...");
    })
    .catch(err => console.error("Error al acceder a la cámara:", err));
};

function startStreaming(video) {
  setInterval(() => {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg'); // Convertir a Base64
    console.log("📤 Enviando imagen:", imageData.substring(0, 50)); // Ver los primeros caracteres
    socket.send(imageData);
  }, 500); // Envía cada medio segundo
}

socket.onmessage = (event) => {
  console.log("📡 Respuesta del servidor:", event.data);
};

