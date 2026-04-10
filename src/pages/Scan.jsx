import { useState, useEffect, useRef } from "react";
import { Html5QrcodeScanner } from "html5-qrcode";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const Scan = () => {
  const [scanned, setScanned] = useState(false);
  const scannerRef = useRef(null);

  useEffect(() => {
    // Inicializar el escáner solo una vez
    if (!scannerRef.current) {
      scannerRef.current = new Html5QrcodeScanner(
        "reader",
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0,
        },
        false
      );
    }

    const onScanSuccess = async (decodedText) => {
      if (scanned) return;
      setScanned(true);

      try {
        // Intentar parsear el JSON del QR
        const data = JSON.parse(decodedText);
        console.log("Datos del QR:", data);

        const token = localStorage.getItem("access_token");
        if (!token) {
          alert("Debes iniciar sesión como vigilante");
          setScanned(false);
          return;
        }

        const res = await fetch(`${API_URL}/acceso/scan`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(data),
        });

        const responseData = await res.json();
        if (!res.ok) throw new Error(responseData.detail || "Error en el servidor");
        alert(responseData.mensaje || "Registro exitoso");
      } catch (err) {
        console.error(err);
        alert("Error: " + err.message);
      } finally {
        setScanned(false);
      }
    };

    const onScanError = (error) => {
      console.warn("Error de escaneo:", error);
    };

    scannerRef.current.render(onScanSuccess, onScanError);

    // Limpiar al desmontar
    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear();
      }
    };
  }, [scanned]);

  return (
    <div>
      <h2>Escanear QR (vigilante)</h2>
      <div id="reader" style={{ width: "100%", maxWidth: "500px", margin: "0 auto" }}></div>
    </div>
  );
};

export default Scan;