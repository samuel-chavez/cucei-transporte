import { QrReader } from "react-qr-reader";

const Scan = () => {

  const handleScan = async (result) => {
    if (result) {
      try {
        const data = JSON.parse(result?.text);

        await fetch("http://localhost:8000/acceso/scan", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(data),
        });

        alert("Registro exitoso");
      } catch (err) {
        console.error(err);
        alert("Error al escanear");
      }
    }
  };

  return (
    <div>
      <h2>Escanear QR</h2>
      <QrReader onResult={(result) => handleScan(result)} />
    </div>
  );
};

export default Scan;