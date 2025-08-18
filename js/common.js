// =======================================================================
//  NUEVO: FUNCIONES AUXILIARES PARA AUTENTICACIÓN (JWT)
// =======================================================================

/**
 * Guarda el token de autenticación y el rol del usuario en el localStorage.
 * @param {string} token - El JWT recibido desde el backend.
 * @param {string} role - El rol del usuario (ej: 'admin' o 'cliente').
 */
function guardarSesion(token, role) {
    localStorage.setItem('supabase_token', token);
    localStorage.setItem('user_role', role);
}

/**
 * Obtiene el token de autenticación del localStorage.
 * @returns {string|null} El token guardado o null si no existe.
 */
function obtenerToken() {
    return localStorage.getItem('supabase_token');
}

/**
 * Elimina el token y el rol del usuario del localStorage al cerrar sesión.
 */
function eliminarSesion() {
    localStorage.removeItem('supabase_token');
    localStorage.removeItem('user_role');
}

/**
 * Construye los headers necesarios para las peticiones a rutas protegidas.
 * @returns {HeadersInit} Un objeto con los headers de autorización.
 */
function getAuthHeaders() {
    const token = obtenerToken();
    const headers = {
        'Content-Type': 'application/json'
    };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

// =======================================================================
//  1. FUNCIONES DE UI (MENSAJES) - SIN CAMBIOS
// =======================================================================

/**
 * Muestra un elemento de mensaje por un tiempo determinado.
 * @param {string} elementoId - El ID del elemento del mensaje a mostrar.
 * @param {number} [duracion=2000] - La duración en milisegundos.
 */
function mostrarMensaje(elementoId, duracion = 2000) {
    const mensaje = document.getElementById(elementoId);
    if (mensaje) {
        mensaje.classList.remove("hidden");
        setTimeout(() => {
            mensaje.classList.add("hidden");
        }, duracion);
    }
}

/**
 * Muestra una notificación flotante (toast) para éxito o error.
 * @param {string} message 
 * @param {string} [type='success'] 
 */
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    const notificationMessage = document.getElementById('notificationMessage');
    
    if (!notification || !notificationMessage) return;

    notificationMessage.textContent = message;
    notification.classList.remove('bg-green-500', 'bg-red-500');
    
    if (type === 'success') {
        notification.classList.add('bg-green-500');
    } else {
        notification.classList.add('bg-red-500');
    }
    
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}


// =======================================================================
//  2. LÓGICA DEL CARRITO DE COMPRAS - SIN CAMBIOS
// =======================================================================

let carrito = [];

function guardarCarrito() {
    localStorage.setItem("carrito", JSON.stringify(carrito));
}

function cargarCarrito() {
    const guardado = localStorage.getItem("carrito");
    carrito = guardado ? JSON.parse(guardado) : [];
    actualizarCarrito();
}

function agregarAlCarrito(producto) {
    const itemEnCarrito = carrito.find(item => item.nombre === producto.nombre);
    if (itemEnCarrito) {
        if (itemEnCarrito.cantidad < producto.stock) {
            itemEnCarrito.cantidad++;
            mostrarMensaje("mensajeAgregado");
        } else {
            mostrarMensaje("mensajeSinStock", 3000);
        }
    } else {
        if (producto.stock > 0) {
            carrito.push({ ...producto, cantidad: 1 });
            mostrarMensaje("mensajeAgregado");
        }
    }
    actualizarCarrito();
}

function actualizarCarrito() {
    const lista = document.getElementById("listaCarrito");
    const total = document.getElementById("totalCarrito");
    const btnWhatsapp = document.getElementById("btnFinalizarWhatsapp");
    const contadorCarrito = document.getElementById("contadorCarrito"); 

    if (!lista || !total) return;

    lista.innerHTML = "";
    let suma = 0;

    carrito.forEach((item, idx) => {
        const subtotal = item.precio * item.cantidad;
        suma += subtotal;
        const li = document.createElement("li");
        li.className = "flex justify-between items-center py-4 border-b border-gray-300";
        li.innerHTML = `
            <div class="flex items-center space-x-4 w-1/2"><img src="${item.imagenes[0]}" alt="${item.nombre}" class="w-16 h-16 object-contain rounded"><span class="font-medium">${item.nombre}</span></div>
            <div class="flex items-center space-x-2"><button class="bg-gray-300 px-2 py-1 rounded" onclick="restarCantidad(${idx})">−</button><span class="mx-2">${item.cantidad}</span><button class="bg-gray-300 px-2 py-1 rounded" onclick="sumarCantidad(${idx})">+</button></div>
            <div class="text-right min-w-[100px]"><span class="block font-bold text-green-600">$${subtotal.toLocaleString()}</span><button class="text-red-600 text-sm mt-1" onclick="eliminarDelCarrito(${idx})">Eliminar</button></div>`;
        lista.appendChild(li);
    });

    total.textContent = suma.toLocaleString();
    if (btnWhatsapp) btnWhatsapp.classList.toggle('hidden', carrito.length === 0);
    
    if (contadorCarrito) {
      const cantidadItems = carrito.reduce((total, item) => total + item.cantidad, 0); // Contar todos los items
      if (cantidadItems > 0) {
        contadorCarrito.textContent = cantidadItems;
        contadorCarrito.classList.remove('hidden');
      } else {
        contadorCarrito.classList.add('hidden');
      }
    }

    guardarCarrito();
}

function restarCantidad(idx) {
    if (carrito[idx].cantidad > 1) {
        carrito[idx].cantidad--;
    } else {
        carrito.splice(idx, 1);
    }
    actualizarCarrito();
}

function sumarCantidad(idx) {
    const productoOriginal = window.productosDB.find(p => p.nombre === carrito[idx].nombre);
    if (productoOriginal && carrito[idx].cantidad < productoOriginal.stock) {
        carrito[idx].cantidad++;
        actualizarCarrito();
    } else {
        mostrarMensaje("mensajeSinStock", 3000);
    }
}

function eliminarDelCarrito(idx) {
    carrito.splice(idx, 1);
    actualizarCarrito();
}

function generarEnlaceWhatsapp() {
    if (carrito.length === 0) return "#";
    let mensaje = "Hola, quisiera finalizar mi compra con los siguientes artículos:\n\n";
    let sumaTotal = 0;
    carrito.forEach(item => {
        const subtotal = item.cantidad * item.precio;
        mensaje += `- ${item.cantidad}x ${item.nombre} - $${subtotal.toLocaleString()}\n`;
        sumaTotal += subtotal;
    });
    mensaje += `\n*Total del Carrito: $${sumaTotal.toLocaleString()}*`;
    const numeroWhatsapp = "5493329577462";
    return `https://wa.me/${numeroWhatsapp}?text=${encodeURIComponent(mensaje)}`;
}


// =======================================================================
//  REFACTORIZADO: LÓGICA DE ESTADO DE AUTENTICACIÓN
// =======================================================================

/**
 * Actualiza los botones del header (Login, Logout, Panel Admin)
 * basándose en el token y el rol guardados en localStorage.
 */
function actualizarEstadoHeader() {
    const token = obtenerToken();
    const role = localStorage.getItem('user_role');

    const btnLogin = document.getElementById('abrirLogin');
    const btnPanelAdmin = document.getElementById('btnPanelAdmin');
    const btnCerrarSesion = document.getElementById('btnCerrarSesion');

    if (token) {
        // Usuario logueado
        btnLogin.classList.add('hidden');
        btnCerrarSesion.classList.remove('hidden');

        // Muestra el panel de admin solo si el rol es 'admin'
        if (role === 'admin') {
            btnPanelAdmin.classList.remove('hidden');
        } else {
            btnPanelAdmin.classList.add('hidden');
        }
    } else {
        // Usuario no logueado
        btnLogin.classList.remove('hidden');
        btnPanelAdmin.classList.add('hidden');
        btnCerrarSesion.classList.add('hidden');
    }
}


// =======================================================================
//  3. INICIALIZACIÓN (EVENT LISTENERS)
// =======================================================================

document.addEventListener("DOMContentLoaded", () => {
    // Carga inicial del estado del header y del carrito
    actualizarEstadoHeader();
    cargarCarrito();

    // --- REFACTORIZADO: LÓGICA PARA CERRAR SESIÓN ---
    const btnCerrarSesion = document.getElementById('btnCerrarSesion');
    if (btnCerrarSesion) {
        btnCerrarSesion.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Elimina los datos de sesión del frontend
            eliminarSesion();
            
            // Opcional: Notificar al backend para invalidar el token si se implementa
            // fetch(`${API_BASE_URL}/logout`, { method: 'POST', headers: getAuthHeaders() });

            // Recarga la página para reflejar el estado de "no logueado"
            location.reload();
        });
    }

    // --- REFACTORIZADO: Lógica de envío del formulario de login ---
    const formLogin = document.querySelector('#loginForm'); // Se cambió el selector para ser más específico
    if (formLogin) {
        formLogin.addEventListener('submit', (e) => {
            e.preventDefault();

            const btnSubmit = formLogin.querySelector('button[type="submit"]');
            const errorDiv = document.getElementById('loginError');
            const formData = new FormData(formLogin);

            btnSubmit.innerText = 'Verificando...';
            btnSubmit.disabled = true;
            errorDiv.classList.add('hidden');

            fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                body: formData,
                // Ya no se necesita 'credentials: include' porque no usamos cookies de sesión
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // ¡Éxito! Guarda el token y el rol del usuario
                    guardarSesion(data.access_token, data.user.role);
                    
                    document.getElementById('modalLogin').classList.add('hidden');
                    actualizarEstadoHeader(); // Actualiza la cabecera inmediatamente
                    // Opcional: recargar la página si es necesario
                    // location.reload();
                } else {
                    errorDiv.innerText = data.error || 'Error desconocido.';
                    errorDiv.classList.remove('hidden');
                }
            })
            .catch(error => {
                console.error('Error en el login:', error);
                errorDiv.innerText = 'No se pudo conectar con el servidor.';
                errorDiv.classList.remove('hidden');
            })
            .finally(() => {
                btnSubmit.innerText = 'Iniciar Sesión';
                btnSubmit.disabled = false;
            });
        });
    }

    // --- LÓGICA DE REGISTRO - SIN CAMBIOS ---
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const btnSubmit = registerForm.querySelector('button[type="submit"]');
            const registerErrorDiv = document.getElementById('registerError');
            btnSubmit.textContent = 'Registrando...';
            btnSubmit.disabled = true;
            registerErrorDiv.classList.add('hidden');

            const formData = {
                nombre: registerForm.nombre.value,
                apellido: registerForm.apellido.value,
                email: registerForm.email.value,
                password: registerForm.password.value,
            };

            fetch(`${API_BASE_URL}/api/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showNotification('¡Usuario registrado con éxito! Ahora puedes iniciar sesión.');
                    document.getElementById('showLogin').click();
                    registerForm.reset();
                } else {
                    registerErrorDiv.textContent = data.error || 'Ocurrió un error desconocido.';
                    registerErrorDiv.classList.remove('hidden');
                }
            })
            .catch(err => {
                console.error('Error en el registro:', err);
                registerErrorDiv.textContent = 'No se pudo conectar con el servidor.';
                registerErrorDiv.classList.remove('hidden');
            })
            .finally(() => {
                btnSubmit.textContent = 'Registrarse';
                btnSubmit.disabled = false;
            });
        });
    }

    // --- LÓGICA DE FINALIZAR COMPRA POR WHATSAPP - SIN CAMBIOS ---
    const btnFinalizar = document.getElementById('btnFinalizarWhatsapp');
    if (btnFinalizar) {
        btnFinalizar.addEventListener('click', (e) => {
            e.preventDefault();
            if (carrito.length > 0) {
                // Este endpoint es público y no requiere token de autenticación
                fetch(`${API_BASE_URL}/api/actualizar-stock`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(carrito)
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.open(generarEnlaceWhatsapp(), '_blank');
                        carrito = [];
                        actualizarCarrito();
                        // alert("¡Pedido enviado! La página se recargará.");
                        showNotification("¡Pedido enviado por WhatsApp! La página se recargará.");
                        setTimeout(() => location.reload(), 2000);
                    } else {
                        alert(`Error: ${data.error}`);
                    }
                })
                .catch(() => alert('Error de conexión al actualizar stock.'));
            }
        });
    }

    // --- LÓGICAS DE UI (MODALES, CONTACTO, ETC.) - SIN CAMBIOS ---

    // Lógica del Modal del Carrito
    const modalCarrito = document.getElementById("modalCarrito");
    if (modalCarrito) {
        document.getElementById("abrirCarrito").addEventListener("click", () => modalCarrito.classList.remove("hidden"));
        document.getElementById("cerrarCarrito").addEventListener("click", () => modalCarrito.classList.add("hidden"));
    }

    // Lógica de la Sección de Contacto
    const btnContacto = document.getElementById("btnContacto");
    const seccionContacto = document.getElementById("contacto");
    if (btnContacto && seccionContacto) {
        btnContacto.addEventListener("click", (e) => {
            e.preventDefault();
            seccionContacto.classList.toggle("hidden");
        });
    }

    // Lógica del Modal de Login
    const modalLogin = document.getElementById("modalLogin");
    if (modalLogin) {
        document.getElementById("abrirLogin").addEventListener("click", () => modalLogin.classList.remove("hidden"));
        document.getElementById("cerrarLogin").addEventListener("click", () => modalLogin.classList.add("hidden"));
    }
    
    // Lógica de Envío del Formulario de Contacto
    const formContacto = document.querySelector("#contacto form");
    if (formContacto) {
        formContacto.addEventListener("submit", (e) => {
            e.preventDefault();
            const btnSubmit = formContacto.querySelector("button[type='submit']");
            btnSubmit.innerText = "Enviando...";
            btnSubmit.disabled = true;

            fetch(`${API_BASE_URL}/contacto`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    nombre: document.getElementById("nombre").value,
                    email: document.getElementById("email").value,
                    mensaje: document.getElementById("mensaje").value,
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    mostrarMensaje("mensajeContacto");
                    formContacto.reset();
                    if (seccionContacto) setTimeout(() => seccionContacto.classList.add("hidden"), 1500);
                } else {
                    alert(`Error: ${data.error || 'No se pudo enviar.'}`);
                }
            })
            .catch(() => alert('No se pudo conectar con el servidor.'))
            .finally(() => {
                btnSubmit.innerText = "Enviar";
                btnSubmit.disabled = false;
            });
        });
    }

    // Lógica para el toggle entre formularios de Login y Registro
    const formContainerLogin = document.getElementById('formContainerLogin');
    const formContainerRegister = document.getElementById('formContainerRegister');
    const showRegisterLink = document.getElementById('showRegister');
    const showLoginLink = document.getElementById('showLogin');

    if (showRegisterLink) {
        showRegisterLink.addEventListener('click', (e) => {
            e.preventDefault();
            formContainerLogin.classList.add('hidden');
            formContainerRegister.classList.remove('hidden');
        });
    }
    if (showLoginLink) {
        showLoginLink.addEventListener('click', (e) => {
            e.preventDefault();
            formContainerRegister.classList.add('hidden');
            formContainerLogin.classList.remove('hidden');
        });
    }
});