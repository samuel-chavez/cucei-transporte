const usuariosIniciales = [
  {
    codigo: "123456789",
    password: "1234",
    nombre: "Samuel Chavez",
    carrera: "Ingeniería en Computación",
    vehiculo: "bicicleta"
  },
  {
    codigo: "987654321",
    password: "abcd",
    nombre: "Alan Muro",
    carrera: "Ingeniería Informática",
    vehiculo: "patin electrico"
  }
];

// Si existe localStorage, cargarlo; si no, usar los iniciales
export let usuarios = JSON.parse(localStorage.getItem("usuarios")) || usuariosIniciales;

// Función para agregar usuario nuevo
export const agregarUsuario = (usuario) => {
  usuarios.push(usuario);
  localStorage.setItem("usuarios", JSON.stringify(usuarios));
};