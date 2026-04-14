document.addEventListener("DOMContentLoaded", function() {
    // Mejorar usabilidad: Ocultar automáticamente las alertas después de 4 segundos
    // para que no estorben la lectura de la pantalla.
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 4000);
    });
});

/**
 * Función global para mostrar notificaciones tipo Toast de Bootstrap.
 * @param {string} mensaje - El texto a mostrar en el toast.
 * @param {string} tipo - Tipo de alerta ('success', 'danger', 'info', 'warning').
 */
function showToast(mensaje, tipo = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const iconClass = tipo === 'danger' ? 'bi-exclamation-triangle' : 
                      tipo === 'success' ? 'bi-check-circle' : 'bi-info-circle';

    const toastHTML = `
        <div class="toast align-items-center text-white bg-${tipo} border-0 mb-2 shadow" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="bi ${iconClass} me-2"></i>${mensaje}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;

    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = toastContainer.lastElementChild;
    const bsToast = new bootstrap.Toast(toastElement, { delay: 4000 });
    
    bsToast.show();
    
    // Limpiar el DOM cuando se oculte visualmente
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}