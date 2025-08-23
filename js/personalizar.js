document.addEventListener('DOMContentLoaded', () => {
    // --- INICIO: LÓGICA PARA PRECARGAR EL FORMULARIO ---
    try {
        const params = new URLSearchParams(window.location.search);
        
        // Obtenemos los valores de la URL
        const diseno = params.get('diseno');
        const acero = params.get('acero');
        const mango = params.get('mango');

        // Si los valores existen, los asignamos a los campos del formulario
        if (diseno) document.getElementById('tipo-diseno').value = diseno;
        if (acero) document.getElementById('tipo-acero').value = acero;
        if (mango) document.getElementById('material-mango').value = mango;

    } catch (error) {
        console.error("Error al intentar precargar el formulario:", error);
    }
    // --- FIN DE LÓGICA DE PRECARGA ---

    const form = document.getElementById('form-personalizado');
    const modalResumen = document.getElementById('modalResumen');
    const contenidoResumen = document.getElementById('contenidoResumen');
    const cerrarResumen = document.getElementById('cerrarResumen');

    // Elementos del modal de contacto
    const modalContacto = document.getElementById('modalContacto');
    const btnContacto = document.getElementById('btnContacto');
    const cerrarContacto = document.getElementById('cerrarContacto');
    const cancelarContacto = document.getElementById('cancelarContacto');
    const formContacto = document.getElementById('formContacto');

    if (!form) return;

    // =======================================================================
    // LÓGICA DEL MODAL DE CONTACTO
    // =======================================================================

    // Abrir modal de contacto
    btnContacto.addEventListener('click', (e) => {
        e.preventDefault();
        modalContacto.classList.remove('hidden');
    });

    // Cerrar modal de contacto - Botón X
    cerrarContacto.addEventListener('click', () => {
        modalContacto.classList.add('hidden');
        formContacto.reset(); // Limpiar formulario
    });

    // Cerrar modal de contacto - Botón Cancelar
    cancelarContacto.addEventListener('click', () => {
        modalContacto.classList.add('hidden');
        formContacto.reset(); // Limpiar formulario
    });

    // Cerrar modal de contacto - Clic fuera
    modalContacto.addEventListener('click', (e) => {
        if (e.target === modalContacto) {
            modalContacto.classList.add('hidden');
            formContacto.reset(); // Limpiar formulario
        }
    });

    // Cerrar modal de contacto - Tecla ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (!modalResumen.classList.contains('hidden')) {
                modalResumen.classList.add('hidden');
            }
            if (!modalContacto.classList.contains('hidden')) {
                modalContacto.classList.add('hidden');
                formContacto.reset(); // Limpiar formulario
            }
        }
    });

    // Procesar formulario de contacto
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

        // Aquí podrías enviar el formulario al backend
        // Por ahora, simulamos el envío exitoso
        console.log('Datos del formulario de contacto:', { nombre, email, mensaje });
        
        // Mostrar mensaje de éxito
        mostrarMensaje('mensajeContacto', '¡Mensaje enviado con éxito!');
        
        // Cerrar modal y limpiar formulario
        modalContacto.classList.add('hidden');
        formContacto.reset();
    });

    // =======================================================================
    // LÓGICA DEL MODAL DE RESUMEN
    // =======================================================================

    // Event listener para cerrar el modal de resumen
    cerrarResumen.addEventListener('click', () => {
        modalResumen.classList.add('hidden');
    });

    // Cerrar modal de resumen al hacer clic fuera de él
    modalResumen.addEventListener('click', (e) => {
        if (e.target === modalResumen) {
            modalResumen.classList.add('hidden');
        }
    });

    // Procesar formulario de personalización
    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        
        let resumenHTML = '<h3 class="text-xl md:text-2xl font-bold mb-6 text-center text-gray-800">Resumen de tu Pieza Personalizada</h3>';
        resumenHTML += '<div class="bg-gray-50 p-4 md:p-6 rounded-lg mb-6">';
        resumenHTML += '<ul class="space-y-3">';
        let whatsappText = 'Hola, quisiera cotizar un cuchillo personalizado con las siguientes características:%0A%0A';

        for (let [key, value] of formData.entries()) {
            if (key !== 'Agregados' && key !== 'Agregados Vaina') {
                resumenHTML += `<li class="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                    <span class="font-semibold text-gray-700">${key}:</span>
                    <span class="text-gray-900">${value}</span>
                </li>`;
                whatsappText += `*${key}:* ${value}%0A`;
            }
        }
        
        const agregadosMango = formData.getAll('Agregados');
        if (agregadosMango.length > 0) {
            const agregadosList = agregadosMango.join(', ');
            resumenHTML += `<li class="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                <span class="font-semibold text-gray-700">Agregados al Mango:</span>
                <span class="text-gray-900">${agregadosList}</span>
            </li>`;
            whatsappText += `*Agregados al Mango:* ${agregadosList}%0A`;
        }

        const agregadosVaina = formData.getAll('Agregados Vaina');
        if (agregadosVaina.length > 0) {
            const agregadosVainaList = agregadosVaina.join(', ');
            resumenHTML += `<li class="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                <span class="font-semibold text-gray-700">Agregados a la Vaina:</span>
                <span class="text-gray-900">${agregadosVainaList}</span>
            </li>`;
            whatsappText += `*Agregados a la Vaina:* ${agregadosVainaList}%0A`;
        }

        resumenHTML += '</ul></div>';
        
        const numeroWhatsapp = "5493329577462";
        const linkWhatsapp = `https://wa.me/${numeroWhatsapp}?text=${whatsappText}`;
        
        resumenHTML += `
            <div class="text-center space-y-4">
                <div class="p-3 md:p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <p class="text-blue-800 font-medium text-sm md:text-base">¡Perfecto! Tu diseño está listo</p>
                    <p class="text-blue-600 text-xs md:text-sm mt-1">Para recibir tu cotización final, contáctame por WhatsApp con este resumen</p>
                </div>
                <div class="flex flex-col gap-3 justify-center">
                    <a href="${linkWhatsapp}" target="_blank" class="inline-flex items-center justify-center bg-green-500 text-white px-4 py-3 md:px-6 md:py-3 rounded-lg font-bold hover:bg-green-600 transition-colors text-sm md:text-base">
                        <svg class="w-4 h-4 md:w-5 md:h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893A11.821 11.821 0 0020.885 3.488"/>
                        </svg>
                        Contactar por WhatsApp
                    </a>
                    <button onclick="document.getElementById('modalResumen').classList.add('hidden')" class="inline-flex items-center justify-center bg-gray-500 text-white px-4 py-3 md:px-6 md:py-3 rounded-lg font-bold hover:bg-gray-600 transition-colors text-sm md:text-base">
                        <svg class="w-4 h-4 md:w-5 md:h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                        </svg>
                        Editar Diseño
                    </button>
                </div>
            </div>
        `;

        contenidoResumen.innerHTML = resumenHTML;
        modalResumen.classList.remove('hidden');
    });
});