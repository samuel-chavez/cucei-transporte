    import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { QRCodeCanvas } from "qrcode.react";
import "../styless/Perfil.css";

const API_URL = "http://localhost:8000";

function Perfil() {

  const [usuario, setUsuario] = useState(null);
  const [bicicletas, setBicicletas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  // Generar QR único
  const generarQR = () => {
    if (!usuario) return "";

    const datosQR = {
      nombre: usuario.nombre,
      codigo: usuario.codigo,
      email: usuario.email,
      rol: usuario.rol
    };

    return JSON.stringify(datosQR);
  };

  useEffect(() => {
  // 1. Pequeña espera para asegurar que el storage sincronizó
  const timer = setTimeout(() => {
    const token = localStorage.getItem("access_token");
    console.log("Token leído en Perfil:", token);

    if (!token) {
      console.warn("No hay token todavía...");
      // navigate("/login"); // Comenta esto un momento para que no te bote
      return;
    }

    const fetchPerfil = async () => {
      try {
        const userRes = await fetch(`${API_URL}/users/me`, {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });

            if (userRes.ok) {
          const userData = await userRes.json();
          setUsuario(userData);
        } else {
          console.error("Error en respuesta:", userRes.status);
          // COMENTA ESTO: No borres el token hasta estar 100% seguros
          // if (userRes.status === 401) { localStorage.removeItem("access_token"); navigate("/login"); }
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPerfil();
  }, 100);

  return () => clearTimeout(timer);
}, [navigate]);


  const handleExport = () => {

    if (bicicletas.length > 0) {

      alert("Función exportToExcel no implementada");

    } else {

      alert("No hay bicicletas para exportar");

    }

  };


  if (loading) return <div>Cargando perfil...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!usuario) return <div>No se pudo cargar el perfil</div>;


  return (

    <div>

      <div className="navbar">BICI-ACCESS</div>

      <div className="perfil-container">

        <div className="perfil-card">

          <h1>Perfil del Alumno</h1>

          <p className="perfil-info">
            <b>Nombre:</b> {usuario.nombre}
          </p>

          <p className="perfil-info">
            <b>Código:</b> {usuario.codigo}
          </p>

          <p className="perfil-info">
            <b>Email:</b> {usuario.email}
          </p>

          <p className="perfil-info">
            <b>Rol:</b> {usuario.rol}
          </p>

          <hr />

          <h2>Mi QR de acceso</h2>

          <div style={{ textAlign: "center", marginTop: "20px" }}>

            <QRCodeCanvas
              value={generarQR()}
              size={220}
            />

            <p>Escanea este código para registrar entrada o salida</p>

          </div>

          <hr />

          <h2>Mis Bicicletas</h2>

          {bicicletas.length === 0 ? (

            <p>No tienes bicicletas registradas.</p>

          ) : (

            <table className="bicicletas-tabla">

              <thead>

                <tr>
                  <th>Marca</th>
                  <th>Modelo</th>
                  <th>Color</th>
                  <th>Serial</th>
                </tr>

              </thead>

              <tbody>

                {bicicletas.map((bici) => (

                  <tr key={bici.id}>

                    <td>{bici.marca}</td>
                    <td>{bici.modelo}</td>
                    <td>{bici.color}</td>
                    <td>{bici.serial}</td>

                  </tr>

                ))}

              </tbody>

            </table>

          )}

          <button className="export-excel" onClick={handleExport}>
            Exportar mis bicicletas a Excel
          </button>

        </div>

      </div>

    </div>

  );

}

export default Perfil;