import { useLocation } from "react-router-dom";

function Perfil() {

  const location = useLocation();
  const usuario = location.state;

  if (!usuario) {
    return <h2>No hay usuario</h2>;
  }

  return (
    <div style={{textAlign:"center", marginTop:"100px"}}>

      <h1>Perfil del Alumno</h1>

      <p><b>Nombre:</b> {usuario.nombre}</p>
      <p><b>Código:</b> {usuario.codigo}</p>
      <p><b>Carrera:</b> {usuario.carrera}</p>
      <p><b>Vehículo:</b> {usuario.vehiculo}</p>

    </div>
  );
}

export default Perfil;