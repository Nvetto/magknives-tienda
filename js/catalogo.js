let productosDB = [];

function capitalizarPrimeraLetra(texto) { return texto.charAt(0).toUpperCase() + texto.slice(1); }

// =======================================================================
// LÓGICA DEL MODAL DE CONTACTO PARA CATALOGO.HTML
// =======================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Elementos del modal de contacto
    const modalContacto = document.getElementById('modalContacto');
    const btnContacto = document.getElementById('btnContacto');
    const cerrarContacto = document.getElementById('cerrarContacto');
    const cancelarContacto = document.getElementById('cancelarContacto');
    const formContacto = document.getElementById('formContacto');

    // Abrir modal de contacto
    if (btnContacto) {
        btnContacto.addEventListener('click', (e) => {
            e.preventDefault();
            modalContacto.classList.remove('hidden');
        });
    }

    // Cerrar modal de contacto - Botón X
    if (cerrarContacto) {
        cerrarContacto.addEventListener('click', () => {
            modalContacto.classList.add('hidden');
            formContacto.reset(); // Limpiar formulario
        });
    }

    // Cerrar modal de contacto - Botón Cancelar
    if (cancelarContacto) {
        cancelarContacto.addEventListener('click', () => {
            modalContacto.classList.add('hidden');
            formContacto.reset(); // Limpiar formulario
        });
    }

    // Cerrar modal de contacto - Clic fuera
    if (modalContacto) {
        modalContacto.addEventListener('click', (e) => {
            if (e.target === modalContacto) {
                modalContacto.classList.add('hidden');
                formContacto.reset(); // Limpiar formulario
            }
        });
    }

    // Cerrar modal de contacto - Tecla ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modalContacto && !modalContacto.classList.contains('hidden')) {
            modalContacto.classList.add('hidden');
            formContacto.reset(); // Limpiar formulario
        }
    });

    // Procesar formulario de contacto
    if (formContacto) {
        formContacto.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const formData = new FormData(formContacto);
            const nombre = formData.get('nombre');
            const email = formData.get('email');
            const mensaje = formData.get('mensaje');

            // Validación básica
            if (!nombre || !email || !mensaje) {
                mostrarMensaje('mensajeContacto', 'Por favor, completa todos los campos.');
                return;
            }

            // Enviar formulario al backend
            fetch(`${API_BASE_URL}/contacto`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nombre, email, mensaje })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    // Mostrar mensaje de éxito
                    mostrarMensaje('mensajeContacto', '¡Mensaje enviado con éxito!');
                    // Cerrar modal y limpiar formulario
                    modalContacto.classList.add('hidden');
                    formContacto.reset();
                } else {
                    // Mostrar mensaje de error
                    mostrarMensaje('mensajeContacto', data.error || 'Error al enviar el mensaje.');
                }
            })
            .catch(error => {
                console.error('Error al enviar mensaje:', error);
                mostrarMensaje('mensajeContacto', 'Error de conexión. Inténtalo de nuevo.');
            });
        });
    }
});

// =======================================================================
// FUNCIÓN PARA GENERAR ENLACE COTIZADOR (MANTENER LA EXISTENTE)
// =======================================================================

function generarEnlaceCotizador(producto) {
    const params = new URLSearchParams();
    const textoBusqueda = (producto.nombre + ' ' + (producto.descripcion || '')).toLowerCase();
    
    // Palabras clave para el Tipo de Diseño
    if (textoBusqueda.includes('bowie')) params.set('diseno', 'Bowie');
    else if (textoBusqueda.includes('verijero')) params.set('diseno', 'Verijero');
    else if (textoBusqueda.includes('cazador')) params.set('diseno', 'Cazador');
    else if (textoBusqueda.includes('facon')) params.set('diseno', 'Facón');
    else if (textoBusqueda.includes('cocina')) params.set('diseno', 'Cocina');
    else if (textoBusqueda.includes('hachuela')) params.set('diseno', 'Hachuela');
    
    // Palabras clave para el Tipo de Acero
    if (textoBusqueda.includes('damasco')) params.set('acero', 'Damasco (Consultar)');
    else if (textoBusqueda.includes('5160')) params.set('acero', '5160');
    else if (textoBusqueda.includes('1095') || textoBusqueda.includes('w1')) params.set('acero', '1095');
    if (textoBusqueda.includes('coral') || textoBusqueda.includes('resina')) params.set('mango', 'Resina (colores a elección)');
    else if (textoBusqueda.includes('asta') || textoBusqueda.includes('ciervo')) params.set('mango', 'Asta de Ciervo');
    else if (['burl', 'imbuia', 'lenga', 'nigra', 'wengue', 'itin'].some(madera => textoBusqueda.includes(madera))) {
        params.set('mango', 'Madera (a elección)');
    }
    return `personalizar.html?${params.toString()}`;
}

function filtrarYRenderizar() {
    const barraBusqueda = document.getElementById("barraBusqueda");
    const texto = (barraBusqueda.value || "").toLowerCase();
    const contenedorPrincipal = document.getElementById("catalogoCompleto");
    const mensajeSinResultados = document.getElementById("sinResultados");

    contenedorPrincipal.innerHTML = '';
    let totalProductosMostrados = 0;

    const productosFiltrados = productosDB.filter(prod => {
        const titulo = prod.nombre.toLowerCase();
        const descripcion = (prod.descripcion || '').toLowerCase(); // Asegurarse que descripción no sea null
        return titulo.includes(texto) || descripcion.includes(texto);
    });

    const productosPorCategoria = productosFiltrados.reduce((acc, prod) => {
        const categoria = prod.categoria || 'Sin Categoría';
        (acc[categoria] = acc[categoria] || []).push(prod);
        return acc;
    }, {});

    for (const categoria in productosPorCategoria) {
        totalProductosMostrados += productosPorCategoria[categoria].length;
        const divCategoria = document.createElement('div');
        divCategoria.className = 'mb-10';
        divCategoria.innerHTML = `<h2 class="text-2xl font-bold mb-4">${capitalizarPrimeraLetra(categoria)}</h2>`;
        const grid = document.createElement('div');
        grid.className = 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4';

        productosPorCategoria[categoria].forEach(prod => {
            const productoDiv = document.createElement('div');
            productoDiv.className = 'producto bg-white shadow-lg rounded p-4 flex flex-col justify-between';
            const botonHTML = prod.stock > 0
                ? `<button data-nombre-producto="${prod.nombre}" class="add-to-cart-btn bg-blue-600 text-white px-3 py-2 rounded mt-4 hover:bg-blue-700 w-full">Agregar al carrito</button>`
                : `<a href="${generarEnlaceCotizador(prod)}" class="block text-center bg-gray-500 text-white px-3 py-2 rounded mt-4 hover:bg-gray-600 w-full">Cotizá el tuyo</a>`;
            const carruselHTML = (prod.imagenes || []).slice(0, 4).map(imgSrc => `<li><img src="${imgSrc}" alt="${prod.nombre}"></li>`).join('');

            productoDiv.innerHTML = `
                <div>
                    <a href="producto.html?id=${prod.id}" class="cursor-pointer">
                        ${prod.stock === 0 ? '<div class="sin-stock-banner">Sin Stock</div>' : ''}
                        <div class="slider-box rounded mb-4"><ul>${carruselHTML}</ul></div>
                        <h3 class="titulo-producto text-lg font-semibold hover:text-blue-600 transition-colors">${prod.nombre}</h3>
                    </a>
                    <p class="descripcion text-sm text-gray-600 my-2">${prod.descripcion || ''}</p>
                    ${prod.stock > 0 ? `<p class="text-xl font-bold text-green-600">$${prod.precio.toLocaleString()}</p><p class="text-sm text-gray-500">Stock: ${prod.stock}</p>` : `<p class="text-xl font-bold invisible">&nbsp;</p><p class="text-sm invisible">&nbsp;</p>`}
                </div>
                ${botonHTML}
            `;
            grid.appendChild(productoDiv);
        });
        divCategoria.appendChild(grid);
        contenedorPrincipal.appendChild(divCategoria);
    }

    mensajeSinResultados.classList.toggle("hidden", totalProductosMostrados > 0);
    
    // Volvemos a asignar los listeners a los botones del carrito
    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', () => {
            const nombreProd = button.getAttribute('data-nombre-producto');
            const productoAAgregar = productosDB.find(p => p.nombre === nombreProd);
            if (productoAAgregar) {
                agregarAlCarrito(productoAAgregar);
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("catalogoCompleto")) {
        fetch(`${API_BASE_URL}/api/productos`)
            .then(response => response.json())
            .then(productos => {
                productosDB = productos; // Guardamos todos los productos
                
                const terminoGuardado = localStorage.getItem('terminoBusqueda');
                if (terminoGuardado) {
                    document.getElementById("barraBusqueda").value = terminoGuardado;
                    localStorage.removeItem('terminoBusqueda'); // Limpiamos para futuras visitas
                }
                
                filtrarYRenderizar(); // Renderizamos con el filtro aplicado (o sin filtro si no hay término)
                
                // Añadimos el listener para búsquedas en tiempo real DENTRO de la página de catálogo
                document.getElementById("barraBusqueda").addEventListener('input', filtrarYRenderizar);
            })
            .catch(error => {
                console.error('Error al cargar los productos:', error);
                document.getElementById("catalogoCompleto").innerHTML = '<p class="text-center text-red-600">No se pudieron cargar los productos.</p>';
            });
    }
});