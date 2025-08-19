// Variable global para almacenar el producto actual y usarlo en el carrito
let productoActual = null;

/**
 * Renderiza la vista de detalle del producto en la página.
 * @param {object} producto - El objeto del producto obtenido de la API.
 */
function renderizarDetalle(producto) {
    const contenedor = document.getElementById('detalle-producto-contenedor');
    if (!contenedor) return;

    productoActual = producto; // Guardamos el producto para el botón de 'Agregar al carrito'

    // Botón dinámico según el stock
    const botonHTML = producto.stock > 0
        ? `<button id="btnAgregar" class="w-full bg-blue-600 text-white px-6 py-3 rounded-lg mt-6 hover:bg-blue-700 font-bold">Agregar al carrito</button>`
        : `<a href="personalizar.html" class="block text-center w-full bg-gray-500 text-white px-6 py-3 rounded-lg mt-6 hover:bg-gray-600 font-bold">Cotizá el tuyo</a>`;
    
    // Galería de imágenes
    const galeriaHTML = producto.imagenes.map((img, index) => `
        <div class="w-1/4 p-1">
            <img src="${img.url}" alt="Vista ${index + 1}" class="cursor-pointer border-2 border-transparent hover:border-blue-500 rounded-lg" onclick="cambiarImagenPrincipal('${img.url}')">
        </div>
    `).join('');

    contenedor.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
                <div class="mb-4">
                    <img id="imagen-principal" src="${producto.imagenes[0]?.url || 'placeholder.jpg'}" alt="${producto.nombre}" class="w-full h-auto object-cover rounded-lg shadow-md">
                </div>
                <div class="flex flex-wrap -mx-1">
                    ${galeriaHTML}
                </div>
            </div>

            <div>
                <h1 class="text-4xl font-bold mb-4">${producto.nombre}</h1>
                <p class="text-gray-600 mb-6">${producto.descripcion}</p>
                
                ${producto.stock > 0 ? `
                    <p class="text-3xl font-bold text-green-600 mb-2">$${producto.precio.toLocaleString()}</p>
                    <p class="text-sm text-gray-500">Stock disponible: ${producto.stock}</p>
                ` : `
                    <div class="p-4 bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 rounded-lg">
                        <p class="font-bold">Producto sin stock</p>
                        <p>Este cuchillo fue un trabajo personalizado. ¡Podemos crear uno similar para ti!</p>
                    </div>
                `}

                ${botonHTML}
            </div>
        </div>
    `;

    // Añadimos el event listener al botón si existe
    const btnAgregar = document.getElementById('btnAgregar');
    if (btnAgregar) {
        btnAgregar.addEventListener('click', () => {
            if (productoActual) {
                agregarAlCarrito(productoActual);
            }
        });
    }
}

/**
 * Cambia la imagen principal en la galería.
 * @param {string} nuevaSrc - La URL de la nueva imagen a mostrar.
 */
function cambiarImagenPrincipal(nuevaSrc) {
    document.getElementById('imagen-principal').src = nuevaSrc;
}

// --- Lógica principal al cargar la página ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. Obtener el ID del producto de la URL
    const params = new URLSearchParams(window.location.search);
    const productoId = params.get('id');

    if (!productoId) {
        document.getElementById('detalle-producto-contenedor').innerHTML = '<p class="text-red-500 text-center">Error: No se especificó un producto.</p>';
        return;
    }

    // 2. Hacer la petición a la API para obtener los datos del producto
    fetch(`${API_BASE_URL}/api/productos/${productoId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('El producto no fue encontrado.');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                renderizarDetalle(data.producto);
            } else {
                throw new Error(data.error);
            }
        })
        .catch(error => {
            console.error('Error al cargar el producto:', error);
            document.getElementById('detalle-producto-contenedor').innerHTML = `<p class="text-red-500 text-center">Error al cargar el producto: ${error.message}</p>`;
        });
});