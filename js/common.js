// =======================================================================
//  1. FUNCIONES DE UI (MENSAJES)
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

// =======================================================================
//  2. LÓGICA DEL CARRITO DE COMPRAS
// =======================================================================

let carrito = [];

function guardarCarrito() {
    localStorage.setItem("carrito", JSON.stringify(carrito));
}

function cargarCarrito() {
    const guardado = localStorage.getItem("carrito");
    carrito = guardado ? JSON.parse(guardado) : [];
    actualizarCarrito(); // Llama a actualizar aquí para asegurar que la UI esté sincronizada al cargar.
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
    const contadorCarrito = document.getElementById("contadorCarrito"); // <-- 1. Obtenemos el nuevo contador

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
    
    // --- INICIO: LÓGICA PARA ACTUALIZAR EL CONTADOR ---
    if (contadorCarrito) {
      const cantidadItems = carrito.length;
      if (cantidadItems > 0) {
        contadorCarrito.textContent = cantidadItems;
        contadorCarrito.classList.remove('hidden');
      } else {
        contadorCarrito.classList.add('hidden');
      }
    }
    // --- FIN: LÓGICA PARA ACTUALIZAR EL CONTADOR ---

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
//  3. CÓDIGO DE INICIALIZACIÓN (EVENT LISTENERS)
// =======================================================================

document.addEventListener("DOMContentLoaded", () => {
    cargarCarrito();

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

    // Lógica de Envío del Formulario de Contacto
    const formContacto = document.querySelector("#contacto form");
    if (formContacto) {
        formContacto.addEventListener("submit", (e) => {
            e.preventDefault();
            const btnSubmit = formContacto.querySelector("button[type='submit']");
            btnSubmit.innerText = "Enviando...";
            btnSubmit.disabled = true;

            fetch('http://127.0.0.1:5000/contacto', {
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

    // Lógica para Finalizar Compra por WhatsApp
    const btnFinalizar = document.getElementById('btnFinalizarWhatsapp');
    if (btnFinalizar) {
        btnFinalizar.addEventListener('click', (e) => {
            e.preventDefault();
            if (carrito.length > 0) {
                // ... (toda la lógica del fetch para actualizar stock)
                fetch('http://127.0.0.1:5000/api/actualizar-stock', {
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
                        alert("¡Pedido enviado! La página se recargará.");
                        location.reload();
                    } else {
                        alert(`Error: ${data.error}`);
                    }
                })
                .catch(() => alert('Error de conexión al actualizar stock.'));
            }
        });
    }
});