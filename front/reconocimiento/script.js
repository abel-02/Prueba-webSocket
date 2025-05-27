const socket = new WebSocket("ws://127.0.0.1:8000/ws");

socket.onopen = () => {
    console.log("✅ Conectado al servidor WebSocket");

    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            const video = document.getElementById('video');
            video.srcObject = stream;
            video.play();
            console.log("🎥 Cámara activada correctamente");
        })
        .catch(err => console.error("❌ Error al acceder a la cámara:", err));
};

// ✅ Enviar imagen solo cuando se toca el botón
document.getElementById("startRecognition").addEventListener("click", () => {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg').split(',')[1];  // ✅ Elimina el prefijo "data:image/jpeg;base64,"

    console.log("📤 Enviando imagen para reconocimiento...");
    socket.send(JSON.stringify({ nombre: "", imagen: imageData, registrar: false }));
});

// ✅ Manejar respuestas del servidor en una sola función
socket.onmessage = (event) => {
    console.log("📡 Respuesta del servidor:", event.data);

    // 📌 Mostrar mensaje del gesto si se requiere uno
    if (event.data.includes("🔄 Por favor, realiza el gesto")) {
        document.getElementById("mensajeGesto").innerText = event.data;  // ✅ Mostrar mensaje en la UI
    }
};
