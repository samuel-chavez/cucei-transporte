import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { QRCodeCanvas } from "qrcode.react";
import * as XLSX from "xlsx";
import { saveAs } from "file-saver";
import "../styless/Perfil.css";
 
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function Perfil() {
  const [usuario, setUsuario] = useState(null);
  const [bicicletas, setBicicletas] = useState([]);
  const [registros, setRegistros] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  // --- Funciones auxiliares ---
  const formatearFecha = (fecha) => {
  if (!fecha) return "—";
  try {
    // Si es un string ISO (ej. "2026-03-26T16:37:21.123Z") o sin Z, asumir UTC
    let date;
    if (typeof fecha === "string") {
      // Añadir 'Z' si no tiene zona horaria explícita
      const isoString = fecha.includes("Z") ? fecha : fecha + "Z";
      date = new Date(isoString);
    } else {
      date = new Date(fecha);
    }
    // Verificar si es válido
    if (isNaN(date.getTime())) {
      return fecha;
    }
    // Mostrar en la zona horaria del navegador
    return date.toLocaleString();
  } catch {
    return fecha;
  }
};


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

  // --- Manejo de entrada/salida manual ---
  const cambiarEstado = async (biciId, tipo) => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      alert("No hay sesión activa");
      return;
    }

    const endpoint = tipo === "entrada" ? "entrada" : "salida";
    try {
      const res = await fetch(`${API_URL}/registros/${endpoint}?bici_id=${biciId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        alert(`${tipo === "entrada" ? "Entrada" : "Salida"} registrada correctamente`);
        // Recargar historial
        const regRes = await fetch(`${API_URL}/registros/mi-historial`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (regRes.ok) {
          const nuevosRegistros = await regRes.json();
          setRegistros(nuevosRegistros);
        }
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail || "No se pudo registrar"}`);
      }
    } catch (err) {
      console.error(err);
      alert("Error de conexión");
    }
  };

  // --- Exportar a Excel ---
  const handleExport = async () => {
  if (bicicletas.length === 0 && registros.length === 0) {
    alert("No hay datos para exportar");
    return;
  }

  // 1. Hoja de bicicletas (existente)
  const bicisData = bicicletas.map((bici) => ({
    Marca: bici.marca,
    Modelo: bici.modelo,
    Color: bici.color,
    Serial: bici.serial,
    "Fecha Registro": formatearFecha(bici.fecha_registro || bici.created_at),
  }));
  const worksheetBicis = XLSX.utils.json_to_sheet(bicisData);

  // 2. Hoja de historial de accesos (con lógica difusa)
  const historialData = registros.map((reg) => {
    let hora = null;
    let categoriaDifusa = "No definida";
    if (reg.fecha_entrada) {
      const date = new Date(reg.fecha_entrada);
      hora = date.getHours();
      // Clasificación difusa por hora (rangos con solapamiento)
      if (hora >= 4 && hora <= 8) categoriaDifusa = "Madrugada / Inicio Mañana";
      else if (hora >= 8 && hora <= 12) categoriaDifusa = "Mañana";
      else if (hora >= 12 && hora <= 18) categoriaDifusa = "Tarde";
      else categoriaDifusa = "Noche";
    }
    return {
      "Fecha Entrada": formatearFecha(reg.fecha_entrada),
      "Fecha Salida": reg.fecha_salida ? formatearFecha(reg.fecha_salida) : "—",
      "Bicicleta ID": reg.bicicleta_id || "—",
      "Hora Ingreso (rango difuso)": categoriaDifusa,
      "Activo": reg.activo ? "Dentro" : "Fuera",
    };
  });
  const worksheetHistorial = XLSX.utils.json_to_sheet(historialData);

  // 3. Hoja de resumen para gráfica (conteo por categoría difusa)
  const conteoDifuso = {};
  historialData.forEach((item) => {
    const cat = item["Hora Ingreso (rango difuso)"];
    if (cat !== "No definida") {
      conteoDifuso[cat] = (conteoDifuso[cat] || 0) + 1;
    }
  });
  const resumenData = Object.entries(conteoDifuso).map(([categoria, count]) => ({
    "Categoría Horaria": categoria,
    "Número de Ingresos": count,
  }));
  const worksheetResumen = XLSX.utils.json_to_sheet(resumenData);

  // Crear libro y agregar hojas
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheetBicis, "Mis Bicicletas");
  XLSX.utils.book_append_sheet(workbook, worksheetHistorial, "Historial Accesos");
  XLSX.utils.book_append_sheet(workbook, worksheetResumen, "Resumen Difuso");

  // Generar archivo
  const excelBuffer = XLSX.write(workbook, { bookType: "xlsx", type: "array" });
  const file = new Blob([excelBuffer], { type: "application/octet-stream" });
  saveAs(file, "datos_completos_biciaccess.xlsx");
};


  // --- Carga inicial de datos ---
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    const fetchData = async () => {
      try {
        // Usuario
        const userRes = await fetch(`${API_URL}/users/me`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!userRes.ok) {
          if (userRes.status === 401) {
            localStorage.removeItem("access_token");
            navigate("/login");
            return;
          }
          throw new Error("Error al obtener perfil");
        }
        const userData = await userRes.json();
        setUsuario(userData);

        // Bicicletas
        const biciRes = await fetch(`${API_URL}/bicicletas/mis-bicicletas`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (biciRes.ok) {
          const biciData = await biciRes.json();
          setBicicletas(biciData);
        } else if (biciRes.status !== 404) {
          console.warn("Error al obtener bicicletas:", biciRes.status);
        }

        // Historial
        const regRes = await fetch(`${API_URL}/registros/mi-historial`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (regRes.ok) {
          const regData = await regRes.json();
          setRegistros(regData);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  // --- Estados de carga y error ---
  if (loading) return <div>Cargando perfil...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!usuario) return <div>No se pudo cargar el perfil</div>;

  return (
    <div>
      <div className="navbar">BICI-ACCESS</div>
      <div className="perfil-container">
        <div className="perfil-card">
          <h1>Perfil del Alumno</h1>
          <p className="perfil-info"><b>Nombre:</b> {usuario.nombre}</p>
          <p className="perfil-info"><b>Código:</b> {usuario.codigo}</p>
          <p className="perfil-info"><b>Rol:</b> {usuario.rol}</p>

          <hr />

          <h2>Mi QR de acceso</h2>
          <div style={{ textAlign: "center", marginTop: "20px" }}>
            <QRCodeCanvas value={generarQR()} size={220} />
            <p>Escanea este código para registrar entrada o salida</p>
          </div>

          {usuario.rol === "cuidador" && (
             <div style={{ textAlign: "center", marginTop: "20px" }}>
                <button onClick={() => navigate("/scan")}>
                  📷 Escanear QR (vigilante)
                </button>
              </div>
          )}
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
                  <th>Fecha Registro</th>
                  <th>Acción</th>
                </tr>
              </thead>
              <tbody>
                {bicicletas.map((bici) => {
                  const activo = registros.some(
                    reg => reg.bicicleta_id === (bici.id || bici._id) && reg.activo === true
                  );
                  return (
                    <tr key={bici.id || bici._id}>
                      <td>{bici.marca}</td>
                      <td>{bici.modelo}</td>
                      <td>{bici.color}</td>
                      <td>{bici.serial}</td>
                      <td>{formatearFecha(bici.fecha_registro || bici.created_at)}</td>
                      <td>
                        {activo ? (
                          <button onClick={() => cambiarEstado(bici.id || bici._id, "salida")}>
                            Registrar salida
                          </button>
                        ) : (
                          <button onClick={() => cambiarEstado(bici.id || bici._id, "entrada")}>
                            Registrar entrada
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          )}

          <button className="export-excel" onClick={handleExport}>
            Exportar mis bicicletas a Excel
          </button>

          <hr />

          <h2>Historial de accesos</h2>
          {registros.length === 0 ? (
            <p>No hay registros de entrada/salida.</p>
          ) : (
            <>
              <p><b>Último ingreso:</b> {formatearFecha(registros[0]?.fecha_entrada)}</p>
              {registros[0]?.fecha_salida && (
                <p><b>Última salida:</b> {formatearFecha(registros[0].fecha_salida)}</p>
              )}
              <details>
                <summary>Ver historial completo ({registros.length})</summary>
                <ul>
                  {registros.map((reg, idx) => (
                    <li key={reg.id || idx}>
                      Entrada: {formatearFecha(reg.fecha_entrada)}
                      {reg.fecha_salida ? ` | Salida: ${formatearFecha(reg.fecha_salida)}` : " (Dentro del ciclopuerto)"}
                    </li>
                  ))}
                </ul>
              </details>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default Perfil;