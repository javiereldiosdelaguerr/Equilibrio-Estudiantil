const API = "http://localhost:5000";

/* MENSAJES */
function mostrarMensaje(msg) {
  alert(msg);
}

/* LOGIN */
function login() {
  const correo = document.getElementById("correo").value.trim();
  const password = document.getElementById("contrasena").value.trim();

  if (!correo || !password) {
    mostrarMensaje("Completa todos los campos");
    return;
  }

  fetch(`${API}/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: correo,
      password: password
    })
  })
    .then(async res => {
      const data = await res.json();
      if (!res.ok) throw data;
      return data;
    })
    .then(data => {
      localStorage.setItem("usuario", JSON.stringify(data.data));
      window.location.href = "dashboard.html";
    })
    .catch(err => {
      mostrarMensaje(err.message || "Error en login");
    });
}


/* REGISTRO (SOLO SI USAS PROMPT) */
function registrar() {
  const nombre = prompt("Tu nombre:");
  const email = prompt("Tu correo:");
  const password = prompt("Tu contraseña:");

  if (!nombre || !email || !password) {
    mostrarMensaje("Completa todos los campos");
    return;
  }

  fetch(`${API}/usuarios`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ nombre, email, password })
  })
    .then(async res => {
      const data = await res.json();
      if (!res.ok) throw data;
      return data;
    })
    .then(() => {
      mostrarMensaje("Usuario creado correctamente");
    })
    .catch(err => {
      mostrarMensaje(err.message || "Error creando usuario");
    });
}


/* REGISTRO DESDE registro.html (PROFESIONAL) */
function registrarDesdeFormulario() {
  const nombre = document.getElementById("nombre").value.trim();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  if (!nombre || !email || !password) {
    mostrarMensaje("Completa todos los campos");
    return;
  }

  fetch(`${API}/usuarios`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ nombre, email, password })
  })
    .then(async res => {
      const data = await res.json();
      if (!res.ok) throw data;
      return data;
    })
    .then(() => {
      mostrarMensaje("Usuario creado correctamente");
      window.location.href = "index.html";
    })
    .catch(err => {
      mostrarMensaje(err.message || "Error creando usuario");
    });
}


/* DASHBOARD */
function cargarDashboard() {
  const usuario = JSON.parse(localStorage.getItem("usuario"));

  if (!usuario) {
    window.location.href = "index.html";
    return;
  }

  document.getElementById("nombreUsuario").innerText = usuario.nombre;
}


/* MOOD */
function crearMood(estado) {
  const usuario = JSON.parse(localStorage.getItem("usuario"));

  if (!usuario) {
    mostrarMensaje("Debes iniciar sesión");
    return;
  }

  fetch(`${API}/mood`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      estado: estado,
      usuario_id: usuario.id
    })
  })
    .then(async res => {
      const data = await res.json();
      if (!res.ok) throw data;
      return data;
    })
    .then(() => {
      mostrarMensaje("Estado guardado");
    })
    .catch(err => {
      mostrarMensaje(err.message || "Error guardando estado");
    });
}


/* LOGOUT */
function logout() {
  localStorage.removeItem("usuario");
  window.location.href = "index.html";
}