import { useState, useEffect, useRef } from "react";
import { Html5QrcodeScanner } from "html5-qrcode";

const API_URL = import.meta.env.VITE_API_URL;

const Scan = () => {
  const [scanned, setScanned] = useState(false);
  const scannerRef = useRef(null);

  useEffect(() => {
    // Inicializar el scanner solo una vez
    if (!scannerRef.current) {
      scannerRef.current = new Html5QrcodeScanner(
        "qr-reader-container",
        { fps: 10, qrbox: { width: 250, height: 250 } },
        false
      );
    }

    const onScanSuccess = async (decodedText) => {
      if (scanned) return; // Evita múltiples escaneos
      setScanned(true);

      try {
        const data = JSON.parse(decodedText);
        const token = localStorage.getItem("access_token");

        if (!token) {
          alert("Debes iniciar sesión");
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

        if (!res.ok) throw new Error("Error en el servidor");

        alert("Registro exitoso");
      } catch (err) {
        console.error(err);
        alert("Error al escanear");
        setScanned(false);
      }
    };

    const onScanError = (error) => {
      console.warn(error);
    };

    scannerRef.current.render(onScanSuccess, onScanError);

    // Cleanup al desmontar
    return () => {
      if (scannerRef.current) {
        scannerRef.current.clear();
      }
    };
  }, [scanned]); // Dependencia para resetear si se permite reescanear

  return (
    <div>
      <h2>Escanear QR</h2>
      <div id="qr-reader-container" style={{ width: "100%", maxWidth: "500px" }}></div>
    </div>
  );
};

export default Scan;