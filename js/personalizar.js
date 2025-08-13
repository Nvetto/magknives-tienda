document.addEventListener('DOMContentLoaded', () => {
    // --- INICIO: NUEVA LÓGICA PARA PRECARGAR EL FORMULARIO ---
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
    const resumenDiv = document.getElementById('resumen-cotizacion');

    if (!form) return;

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const formData = new FormData(form);
        
        let resumenHTML = '<h3 class="text-2xl font-bold mb-4">Resumen de tu Pieza Personalizada</h3><ul class="list-disc pl-5 space-y-2">';
        let whatsappText = 'Hola, quisiera cotizar un cuchillo personalizado con las siguientes características:%0A%0A';

        for (let [key, value] of formData.entries()) {
            if (key !== 'Agregados' && key !== 'Agregados Vaina') {
                resumenHTML += `<li><strong>${key}:</strong> ${value}</li>`;
                whatsappText += `*${key}:* ${value}%0A`;
            }
        }
        
        const agregadosMango = formData.getAll('Agregados');
        if (agregadosMango.length > 0) {
            const agregadosList = agregadosMango.join(', ');
            resumenHTML += `<li><strong>Agregados al Mango:</strong> ${agregadosList}</li>`;
            whatsappText += `*Agregados al Mango:* ${agregadosList}%0A`;
        }

        const agregadosVaina = formData.getAll('Agregados Vaina');
        if (agregadosVaina.length > 0) {
            const agregadosVainaList = agregadosVaina.join(', ');
            resumenHTML += `<li><strong>Agregados a la Vaina:</strong> ${agregadosVainaList}</li>`;
            whatsappText += `*Agregados a la Vaina:* ${agregadosVainaList}%0A`;
        }

        resumenHTML += '</ul>';
        
        const numeroWhatsapp = "5493329577462";
        const linkWhatsapp = `https://wa.me/${numeroWhatsapp}?text=${whatsappText}`;
        
        resumenHTML += `
            <div class="mt-6 border-t pt-4 text-center">
                <p class="mb-4">¡Gracias por diseñar tu cuchillo! Para recibir tu cotización final, por favor contáctame por WhatsApp con este resumen.</p>
                <a href="${linkWhatsapp}" target="_blank" class="inline-block bg-green-500 text-white px-6 py-3 rounded-lg font-bold hover:bg-green-600 transition-colors">
                    Contactar por WhatsApp para Cotizar
                </a>
            </div>
        `;

        resumenDiv.innerHTML = resumenHTML;
        resumenDiv.classList.remove('hidden');
        resumenDiv.scrollIntoView({ behavior: 'smooth' });
    });
});