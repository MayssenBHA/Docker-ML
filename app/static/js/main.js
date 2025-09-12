// JavaScript pour l'application de prédiction de séries temporelles

document.addEventListener('DOMContentLoaded', function() {
    // Animation des cartes au chargement
    animateCards();
    
    // Validation du formulaire
    setupFormValidation();
    
    // Gestion des tooltips
    initializeTooltips();
});

function animateCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });
}

function setupFormValidation() {
    const form = document.getElementById('forecastForm');
    if (!form) return;
    
    const stepsInput = document.getElementById('steps');
    const submitBtn = document.getElementById('predictBtn');
    
    stepsInput.addEventListener('input', function() {
        const value = parseInt(this.value);
        const isValid = value >= 1 && value <= 60;
        
        if (!isValid) {
            this.classList.add('is-invalid');
            submitBtn.disabled = true;
        } else {
            this.classList.remove('is-invalid');
            submitBtn.disabled = false;
        }
    });
    
    form.addEventListener('submit', function(e) {
        const stepsValue = parseInt(stepsInput.value);
        
        if (stepsValue < 1 || stepsValue > 60) {
            e.preventDefault();
            showAlert('Veuillez entrer un nombre entre 1 et 60 mois.', 'warning');
            return;
        }
        
        // Animation du bouton
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Génération en cours...';
        submitBtn.disabled = true;
        
        // Affichage d'un message de chargement
        showLoadingMessage();
    });
}

function initializeTooltips() {
    // Initialisation des tooltips Bootstrap si disponible
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-info-circle me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    container.insertAdjacentHTML('afterbegin', alertHtml);
    
    // Auto-dismiss après 5 secondes
    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            alert.remove();
        }
    }, 5000);
}

function showLoadingMessage() {
    const loadingHtml = `
        <div id="loadingMessage" class="alert alert-info text-center mt-3">
            <div class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></div>
            <strong>Génération des prédictions en cours...</strong>
            <div class="small mt-1">Cela peut prendre quelques secondes</div>
        </div>
    `;
    
    const form = document.getElementById('forecastForm');
    form.insertAdjacentHTML('afterend', loadingHtml);
}

// Fonction pour copier les données dans le presse-papiers
function copyToClipboard(data) {
    const textArea = document.createElement('textarea');
    textArea.value = JSON.stringify(data, null, 2);
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
    
    showAlert('Données copiées dans le presse-papiers!', 'success');
}

// Fonction pour exporter les données en CSV
function exportToCSV(predictions) {
    if (!predictions || !predictions.dates) return;
    
    let csvContent = "Date,Prediction,Lower_CI,Upper_CI\n";
    
    for (let i = 0; i < predictions.dates.length; i++) {
        csvContent += `${predictions.dates[i]},${predictions.values[i].toFixed(2)},${predictions.lower_ci[i].toFixed(2)},${predictions.upper_ci[i].toFixed(2)}\n`;
    }
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `predictions_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
}

// Fonction pour valider l'entrée numérique
function validateNumericInput(input) {
    const value = parseInt(input.value);
    const min = parseInt(input.min);
    const max = parseInt(input.max);
    
    if (isNaN(value) || value < min || value > max) {
        input.classList.add('is-invalid');
        return false;
    } else {
        input.classList.remove('is-invalid');
        return true;
    }
}

// Gestion des erreurs globales
window.addEventListener('error', function(e) {
    console.error('Erreur JavaScript:', e.error);
    showAlert('Une erreur inattendue s\'est produite. Veuillez réessayer.', 'danger');
});

// Fonction pour faire une requête API
async function fetchPredictions(steps) {
    try {
        const response = await fetch(`/api/forecast/${steps}`);
        
        if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Erreur lors de la récupération des prédictions:', error);
        throw error;
    }
}

// Fonction pour vérifier le statut du modèle
async function checkModelStatus() {
    try {
        const response = await fetch('/api/status');
        const status = await response.json();
        return status;
    } catch (error) {
        console.error('Erreur lors de la vérification du statut:', error);
        return { success: false, error: error.message };
    }
}

// Animation smooth scroll
function smoothScrollTo(targetId) {
    const element = document.getElementById(targetId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Utilitaires pour les graphiques
function formatNumber(num) {
    return new Intl.NumberFormat('fr-FR').format(Math.round(num));
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', { 
        year: 'numeric', 
        month: 'long' 
    });
}

// Gestion responsive des tableaux
function makeTablesResponsive() {
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'table-responsive';
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Initialisation des composants responsives
document.addEventListener('DOMContentLoaded', function() {
    makeTablesResponsive();
});
