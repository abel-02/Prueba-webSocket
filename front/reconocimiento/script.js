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

const intentos = {
    sonrisa: 0,
    giro: 0,
    cejas: 0
};

const gestosMostrados = {
    sonrisa: false,
    giro: false,
    cejas: false
};

document.getElementById("startRecognition").addEventListener("click", () => {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = canvas.toDataURL('image/jpeg').split(',')[1];

    console.log("📤 Enviando imagen para reconocimiento...");
    socket.send(JSON.stringify({ nombre: "", imagen: imageData, registrar: false }));
});

socket.onmessage = (event) => {
    const mensaje = event.data;
    console.log("📡 Respuesta del servidor:", mensaje);

    const mostrarAlertaGesto = (gesto, textoInicial) => {
        if (!gestosMostrados[gesto]) {
            gestosMostrados[gesto] = true;
            alert(textoInicial);
        } else {
            alert(`⚠️ Intenta hacer el gesto '${gesto}' nuevamente con más claridad.`);
        }
        intentos[gesto]++;
    };

    if (mensaje.includes("sonrisa")) {
        mostrarAlertaGesto("sonrisa", "😊 Por favor, realiza el gesto: sonrisa");
    } else if (mensaje.includes("giro")) {
        mostrarAlertaGesto("giro", "↩️ Por favor, realiza el gesto: giro de cabeza");
    } else if (mensaje.includes("cejas")) {
        mostrarAlertaGesto("cejas", "😯 Por favor, realiza el gesto: levantar cejas");
    } else if (mensaje.includes("✅")) {
        alert(mensaje);  // Éxito
        // Reiniciar para permitir nuevo reconocimiento más adelante
        intentos.sonrisa = 0;
        intentos.giro = 0;
        intentos.cejas = 0;
        gestosMostrados.sonrisa = false;
        gestosMostrados.giro = false;
        gestosMostrados.cejas = false;
    } else if (mensaje.includes("❌") || mensaje.includes("🚫") || mensaje.includes("⚠️")) {
        alert("⚠️ " + mensaje);
    }
};
