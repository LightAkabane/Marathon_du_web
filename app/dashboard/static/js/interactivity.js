// Gestion du plein écran sur la carte ou sur les autres éléments
function toggleFullscreen(button) {
    const card = button.closest('.chart-card');
    card.classList.toggle('fullscreen');
    // Si vous aviez un graphique principal à redimensionner, c'est ici qu'on l'appellerait.
}

// Export PDF (nécessite pdfmake)
function exportChart(button) {
    // On recherche le conteneur parent contenant le diagramme à exporter
    const card = button.closest('.chart-card');
    if (!card) {
        console.error("Aucun conteneur .chart-card trouvé pour l'export.");
        return;
    }
    
    // Optionnel : ajouter un indicateur de chargement
    card.style.opacity = 0.5;
    
    html2canvas(card, {scale: 2}).then(canvas => {
        const imgData = canvas.toDataURL('image/png');
        const docDefinition = {
            content: [
                {
                    image: imgData,
                    width: 500 // Ajuste la largeur si nécessaire
                }
            ]
        };
        pdfMake.createPdf(docDefinition).download('diagram.pdf');
        card.style.opacity = 1; // Réinitialiser l'opacité après l'export
    }).catch(err => {
        console.error("Erreur lors de la conversion en canvas : ", err);
        card.style.opacity = 1;
    });
}


// Navigation fluide pour les boutons de navigation
document.querySelectorAll('.nav-button').forEach(button => {
    button.addEventListener('click', () => {
        const targetSection = button.textContent.toLowerCase();
        const targetElem = document.querySelector(`#${targetSection}`);
        if (targetElem) {
            targetElem.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Fonction pour filtrer les cases à cocher dans un groupe donné
function filterCheckboxes(inputId, checkboxContainerId) {
    const input = document.getElementById(inputId);
    const filterValue = input.value.toLowerCase();
    const container = document.getElementById(checkboxContainerId);
    const labels = container.querySelectorAll('.checkbox-label');

    labels.forEach(label => {
        const text = label.textContent.toLowerCase();
        label.style.display = text.includes(filterValue) ? 'block' : 'none';
    });
}

// Écouteurs sur les champs de recherche
document.getElementById('lyceeSearch').addEventListener('input', () => {
    filterCheckboxes('lyceeSearch', 'lyceeCheckboxes');
});

document.getElementById('profileSearch').addEventListener('input', () => {
    filterCheckboxes('profileSearch', 'profileCheckboxes');
});

document.querySelectorAll('.nav-button').forEach(button => {
    button.addEventListener('click', function() {
        const targetId = this.getAttribute('data-target');
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
