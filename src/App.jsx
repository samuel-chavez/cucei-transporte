import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Perfil from "./pages/Perfil";
import Registro from "./pages/Registro";
import Scan from "./pages/Scan"; 


function App() {
  return (

    <BrowserRouter>

      <Routes>

        <Route path="/" element={<Login />} />

        <Route path="/login" element={<Login />} />

        <Route path="/perfil" element={<Perfil />} />

        <Route path="/registro" element={<Registro />} />

        <Route path="/scan" element={<Scan />} />


      </Routes>

    </BrowserRouter>

  );
}

export default App;