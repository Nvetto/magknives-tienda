// Variable global para que otros scripts (como common.js) puedan acceder a la lista completa de productos
let productosDB = [];

/**
 * Analiza un producto para generar un enlace al cotizador con parámetros pre-cargados.
 * @param {object} producto - El objeto del producto.
 * @returns {string} - La URL para el botón de cotización.
 */
function generarEnlaceCotizador(producto) {
    const textoBusqueda = (producto.nombre + ' ' + producto.descripcion).toLowerCase();
    const params = new URLSearchParams();

    // Palabras clave para el Tipo de Diseño
    if (textoBusqueda.includes('cazador')) params.set('diseno', 'Cazador');
    else if (textoBusqueda.includes('verijero')) params.set('diseno', 'Verijero');
    else if (textoBusqueda.includes('facón')) params.set('diseno', 'Facón');
    else if (textoBusqueda.includes('bowie')) params.set('diseno', 'Bowie');
    else if (textoBusqueda.includes('cocina')) params.set('diseno', 'Cocina');

    // Palabras clave para el Tipo de Acero
    if (textoBusqueda.includes('damasco')) params.set('acero', 'Damasco (Consultar)');
    else if (textoBusqueda.includes('5160')) params.set('acero', '5160');
    else if (textoBusqueda.includes('1095') || textoBusqueda.includes('w1')) params.set('acero', '1095');

    // Palabras clave para el Material del Mango
    if (textoBusqueda.includes('coral') || textoBusqueda.includes('resina')) params.set('mango', 'Resina (colores a elección)');
    else if (textoBusqueda.includes('asta') || textoBusqueda.includes('ciervo')) params.set('mango', 'Asta de Ciervo');
    else if (['burl', 'imbuia', 'lenga', 'nigra', 'wengue', 'itin'].some(madera => textoBusqueda.includes(madera))) {
        params.set('mango', 'Madera (a elección)');
    }
    
    return `personalizar.html?${params.toString()}`;
}

function configurarBusqueda() {
    const barraBusqueda = document.getElementById("barraBusqueda");
    const productos = document.querySelectorAll(".producto");
    const mensajeSinResultados = document.getElementById("sinResultados");

    if (barraBusqueda && productos.length > 0) {
        barraBusqueda.addEventListener("input", () => {
            const texto = barraBusqueda.value.toLowerCase();
            productos.forEach(producto => {
                const titulo = producto.querySelector(".titulo-producto")?.textContent.toLowerCase() || "";
                producto.style.display = titulo.includes(texto) ? "flex" : "none";
            });
        });
    }
}

function renderizarDisponibles(productos) {
    window.productosDB = productos; // Guardar productos para referencia global
    const contenedorPrincipal = document.getElementById("disponiblesCompleto");
    if (!contenedorPrincipal) return;

    // Lógica para completar hasta 8 productos (sin cambios)
    let productosAMostrar;
    const productosEnStock = productos.filter(prod => prod.stock > 0);
    productosAMostrar = [...productosEnStock];

    if (productosAMostrar.length < 8) {
        const cantidadNecesaria = 8 - productosAMostrar.length;
        const nombresYaMostrados = new Set(productosAMostrar.map(p => p.nombre));
        const productosDeRelleno = productos
            .filter(prod => prod.categoria === 'personalizados' && !nombresYaMostrados.has(prod.nombre))
            .slice(0, cantidadNecesaria);
        productosAMostrar.push(...productosDeRelleno);
    }

    // Limpieza y renderizado
    contenedorPrincipal.innerHTML = '';
    if (productosAMostrar.length === 0) {
        contenedorPrincipal.innerHTML = '<h2 class="text-3xl font-bold text-center mb-8">Destacados</h2><p class="text-center text-gray-600">No hay productos disponibles por el momento.</p>';
        return;
    }

    contenedorPrincipal.innerHTML = '<h2 class="text-3xl font-bold text-center mb-8">Destacados</h2>';
    const grid = document.createElement('div');
    grid.className = 'grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4';

    productosAMostrar.forEach(prod => {
        // --- CAMBIO 1: El div principal ya no es un contenedor flex ---
        const productoDiv = document.createElement('div');
        productoDiv.className = 'producto bg-white shadow-lg rounded p-4'; // Se quitó flex, flex-col, etc.

        const botonHTML = prod.stock > 0
            ? `<button data-nombre-producto="${prod.nombre}" class="add-to-cart-btn bg-blue-600 text-white px-3 py-2 rounded mt-4 hover:bg-blue-700 w-full">Agregar al carrito</button>`
            : `<a href="${generarEnlaceCotizador(prod)}" class="block text-center bg-gray-500 text-white px-3 py-2 rounded mt-4 hover:bg-gray-600 w-full">Cotizá el tuyo</a>`;

        const carruselHTML = prod.imagenes.map(imgSrc => `<li><img src="${imgSrc}" alt="${prod.nombre}"></li>`).join('');

        // --- CAMBIO 2: La estructura interior ahora contiene el layout flex ---
        productoDiv.innerHTML = `
            ${prod.stock === 0 ? '<div class="sin-stock-banner">Sin Stock</div>' : ''}
            <div class="h-full flex flex-col justify-between">
                <div>
                    <div class="slider-box rounded mb-4">
                        <ul>${carruselHTML}</ul>
                    </div>
                    <h3 class="titulo-producto text-lg font-semibold">${prod.nombre}</h3>
                    <p class="text-sm text-gray-600 my-2">${prod.descripcion}</p>
                    ${prod.stock > 0 ? `
                        <p class="text-xl font-bold text-green-600">$${prod.precio.toLocaleString()}</p>
                        <p class="text-sm text-gray-500">Stock: ${prod.stock}</p>
                    ` : `
                        <p class="text-xl font-bold invisible">&nbsp;</p>
                        <p class="text-sm invisible">&nbsp;</p>
                    `}
                </div>
                ${botonHTML}
            </div>
        `;
        grid.appendChild(productoDiv);
    });

    contenedorPrincipal.appendChild(grid);

    document.querySelectorAll('.add-to-cart-btn').forEach(button => {
        button.addEventListener('click', () => {
            const nombreProd = button.getAttribute('data-nombre-producto');
            const productoAAgregar = productos.find(p => p.nombre === nombreProd);
            if (productoAAgregar) {
                agregarAlCarrito(productoAAgregar);
            }
        });
    });
}

// El resto del archivo (DOMContentLoaded) no cambia
document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("disponiblesCompleto")) {
        fetch('http://127.0.0.1:5000/api/productos')
            .then(response => response.json())
            .then(productos => {
                renderizarDisponibles(productos);
                configurarBusqueda();
            })
            .catch(error => {
                console.error('Error al cargar los productos:', error);
                document.getElementById("disponiblesCompleto").innerHTML = '<p class="text-center text-red-600">No se pudieron cargar los productos. Asegúrate de que el servidor esté funcionando.</p>';
            });
    }
});

document.addEventListener("DOMContentLoaded", () => {
    if (document.getElementById("disponiblesCompleto")) {
        fetch('http://127.0.0.1:5000/api/productos')
            .then(response => response.json())
            .then(productos => {
                renderizarDisponibles(productos);
                configurarBusqueda();
            })
            .catch(error => {
                console.error('Error al cargar los productos:', error);
                document.getElementById("disponiblesCompleto").innerHTML = '<p class="text-center text-red-600">No se pudieron cargar los productos. Asegúrate de que el servidor esté funcionando.</p>';
            });
    }
});