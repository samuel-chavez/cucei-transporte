import { useState } from "react";
import { QrReader } from "react-qr-reader";

const API_URL = import.meta.env.VITE_API_URL;

const Scan = () => {
  const [scanned, setScanned] = useState(false);

  const handleScan = async (result) => {
    if (result && !scanned) {
      setScanned(true);

      try {
        const data = JSON.parse(result?.text);

        const token = localStorage.getItem("access_token");

        if (!token) {
          alert("Debes iniciar sesión");
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
    }
  };

  return (
    <div>
      <h2>Escanear QR</h2>
      <QrReader
        constraints={{ facingMode: "environment" }}
        onResult={(result) => handleScan(result)}
      />
    </div>
  );
};

export default Scan;