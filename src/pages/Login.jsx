import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { usuarios } from "../data/usuarios";

function Login() {

  const [codigo, setCodigo] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const iniciarSesion = (e) => {
    e.preventDefault();

    const usuario = usuarios.find(
      (u) => u.codigo === codigo && u.password === password
    );

    if (usuario) {
      navigate("/perfil", { state: usuario });
    } else {
      alert("Código o contraseña incorrectos");
    }
  };

  return (
    <div style={{textAlign:"center", marginTop:"100px"}}>

      <h1>CUCEI Transporte</h1>

      <form onSubmit={iniciarSesion}>

        <div>
          <input
            type="text"
            placeholder="Código de alumno"
            maxLength="9"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
          />
        </div>

        <br/>

        <div>
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <br/>

        <button type="submit">
          Iniciar sesión
        </button>

      </form>

    </div>
  );
}

export default Login;