// Variable globale pour le lycée sélectionné via la carte
let selectedLyceeFromMap = null;
// Variable globale pour stocker le type sélectionné dans le camembert (null = aucune sélection)
let selectedProfileFromPie = null;

window.lyceesMarkers = [];

// Permet de basculer l'affichage fullscreen du diagramme
function toggleFullscreen(button) {
    // On recherche le conteneur parent (par exemple, l'élément avec la classe 'chart-card')
    const card = button.closest('.chart-card');
    if (card) {
      card.classList.toggle('fullscreen');
    }
  }
  
  // Permet d'exporter le diagramme en PDF
  function exportChart(button) {
    // On recherche le conteneur parent contenant le diagramme à exporter
    const card = button.closest('.chart-card');
    if (!card) return;
    
    // Utilise html2canvas pour capturer le contenu du conteneur
    html2canvas(card).then(canvas => {
      // Convertir le canvas en image dataURL
      const imgData = canvas.toDataURL('image/png');
      // Créer le document PDF avec pdfMake
      const docDefinition = {
        content: [
          {
            image: imgData,
            width: 500 // Ajuste la taille selon tes besoins
          }
        ]
      };
      // Télécharger le PDF
      pdfMake.createPdf(docDefinition).download('diagram.pdf');
    });
  }
  

function updateMapMarkers(filteredData) {
    // Construire un ensemble des noms de lycées à afficher
    const filteredNames = new Set(filteredData.map(item => item.lycee_name));
    
    window.lyceesMarkers.forEach(item => {
        // Vérifier si le lycée de ce marqueur est dans l'ensemble filtré
        if (filteredNames.has(item.data.lycee_name)) {
            // Si le marqueur n'est pas déjà sur la carte, l'ajouter
            if (!window.map.hasLayer(item.marker)) {
                item.marker.addTo(window.map);
            }
        } else {
            // S'il est sur la carte mais ne doit pas l'être, le retirer
            if (window.map.hasLayer(item.marker)) {
                window.map.removeLayer(item.marker);
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM entièrement chargé");

    // Attacher les écouteurs sur les filtres :
    document.querySelectorAll('#lyceeCheckboxes input[type="checkbox"]').forEach(chk => {
        chk.addEventListener('change', updateUI);
    });
    document.querySelectorAll('#profileCheckboxes input[type="checkbox"]').forEach(chk => {
        chk.addEventListener('change', updateUI);
    });
    document.querySelectorAll('#timeRangeCheckboxes input[type="checkbox"]').forEach(chk => {
        chk.addEventListener('change', updateUI);
    });

    // Attacher les écouteurs sur les champs de recherche
    document.getElementById('lyceeSearch').addEventListener('input', debounce(() => {
        filterCheckboxes('lyceeSearch', 'lyceeCheckboxes');
        updateUI();
    }, 300));

    document.getElementById('profileSearch').addEventListener('input', debounce(() => {
        filterCheckboxes('profileSearch', 'profileCheckboxes');
        updateUI();
    }, 300));

    // Appel initial de updateUI pour afficher tout
    updateUI();

    function debounce(func, delay) {
        let debounceTimer;
        return function(...args) {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => func.apply(this, args), delay);
        };
    }
    



    // Initialisation de la carte Leaflet
    // Initialisation de la carte Leaflet (rendre la variable globale)
    window.map = L.map('heatmapChart').setView([46.5, 2.5], 6);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
        attribution: '© OpenStreetMap, © CARTO',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(window.map);
    
    console.log("Carte initialisée");

    

    
    // Ajout des marqueurs pour chaque lycée à partir de lyceesData
    window.lyceesMarkers = [];
    lyceesData.forEach(lycee => {
        let markerColor = getColorByProfileType(lycee.profile_type);
        let markerIcon = L.circleMarker([lycee.latitude, lycee.longitude], {
            radius: 8,
            fillColor: markerColor,
            color: markerColor,
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        }).addTo(map);
    
        markerIcon.bindPopup(`
            <b>${lycee.lycee_name}</b><br>
            Profil : ${lycee.profile_type}<br>
            Usage : ${lycee.usage_purpose}<br>
            Pages vues : ${lycee.page_views}
        `);
    
        // Ajout d'un écouteur d'événement sur le clic
        markerIcon.on('click', () => {
            // Met à jour la variable globale avec le lycée cliqué
            selectedLyceeFromMap = lycee.lycee_name;
            console.log("Lycée sélectionné via la carte :", selectedLyceeFromMap);
            // Appel de updateUI pour actualiser les autres diagrammes
            updateUI();
        });
    
        window.lyceesMarkers.push({
            marker: markerIcon,
            data: lycee
        });
    });
    
    console.log("Marqueurs ajoutés :", window.lyceesMarkers);

    // Attacher les écouteurs aux checkboxes pour déclencher updateUI
    const checkboxes = document.querySelectorAll('.lycee-list input[name="lycee"]');
    checkboxes.forEach(chk => {
        chk.addEventListener('change', updateUI);
    });

    // Appel initial de updateUI (aucune case cochée => toutes les données)
    updateUI();
});

// Fonction utilitaire pour obtenir une couleur selon le profile_type
function getColorByProfileType(profileType) {
    switch (profileType) {
        case 'Environnement': return 'green';
        case 'Politique': return 'blue';
        case 'Scientifique': return 'purple';
        default: return 'gray';
    }
}

// Récupère les lycées sélectionnés selon les checkboxes
function getSelectedLycees() {
    const checkboxes = document.querySelectorAll('.lycee-list input[name="lycee"]:checked');
    const selectedValues = Array.from(checkboxes).map(chk => chk.value);
    console.log("Valeurs sélectionnées :", selectedValues);
    // Si aucune case n'est cochée, renvoyer toutes les données
    if (selectedValues.length === 0) {
        console.log("Aucune case cochée, utilisation de toutes les données");
        return lyceesData;
    }
    const filtered = lyceesData.filter(lycee => selectedValues.includes(lycee.lycee_name));
    console.log("Données filtrées :", filtered);
    return filtered;
}

function getFilters() {
    // Récupérer les lycées cochés dans le groupe identifié par "lyceeCheckboxes"
    const lyceeCheckboxes = document.querySelectorAll('#lyceeCheckboxes input[name="lycee"]:checked');
    const selectedLycees = Array.from(lyceeCheckboxes).map(chk => chk.value);

    // Récupérer les types de profil cochés dans le groupe identifié par "profileCheckboxes"
    const profileCheckboxes = document.querySelectorAll('#profileCheckboxes input[name="profile"]:checked');
    const selectedProfiles = Array.from(profileCheckboxes).map(chk => chk.value);

    // Récupérer les plages horaires cochées dans le groupe identifié par "timeRangeCheckboxes"
    const timeRangeCheckboxes = document.querySelectorAll('#timeRangeCheckboxes input[name="timeRange"]:checked');
    const selectedTimeRanges = Array.from(timeRangeCheckboxes).map(chk => chk.value);

    console.log("Filtres récupérés :", { lycees: selectedLycees, profiles: selectedProfiles, timeRanges: selectedTimeRanges });
    return {
        lycees: selectedLycees,
        profiles: selectedProfiles,
        timeRanges: selectedTimeRanges
    };
}

document.getElementById('resetSelection').addEventListener('click', () => {
    selectedLyceeFromMap = null;
    updateUI();
});


// Fonction principale de mise à jour de l'UI
function updateUI() {
    console.log("updateUI appelée");
    const filters = getFilters();
    
    // Commencer par filtrer par les critères existants
    let filteredData = lyceesData.filter(lycee =>
        filters.lycees.includes(lycee.lycee_name) &&
        filters.profiles.includes(lycee.profile_type)
    );
    
    // Filtrage par plage horaire
    filteredData = filteredData.filter(lycee => {
        const hour = parseInt(lycee.timestamp.split(' ')[1].split(':')[0], 10);
        return filters.timeRanges.some(range => {
            const [start, end] = range.split('-').map(Number);
            return hour >= start && hour < end;
        });
    });
    
    // Si un lycée a été sélectionné sur la carte, filtrer uniquement pour celui-ci
    if (selectedLyceeFromMap) {
        filteredData = filteredData.filter(lycee => lycee.lycee_name === selectedLyceeFromMap);
        console.log("Filtrage appliqué pour le lycée sélectionné :", selectedLyceeFromMap);
    }

    // Si un type a été sélectionné dans le camembert, filtrer par ce type
    if (selectedProfileFromPie) {
        filteredData = filteredData.filter(lycee => lycee.profile_type === selectedProfileFromPie);
        console.log("Filtrage par type appliqué :", selectedProfileFromPie);
    }

     // Si un type a été sélectionné dans le camembert, on applique ce filtre
     if (selectedProfileFromPie) {
        filteredData = filteredData.filter(lycee => lycee.profile_type === selectedProfileFromPie);
    }
    
    console.log("Données finales après filtrage :", filteredData);

    updateWordClouds(filteredData);
    updateProfilePieChart(filteredData);
    updateRadarChart(filteredData);
    updateMapMarkers(filteredData);
}

let radarChartInstance = null;

function updateRadarChart(filteredData) {
    console.log("updateRadarChart appelée avec filteredData:", filteredData);
    // Profils et plages horaires prédéfinis
    const profiles = ["Environnement", "Politique", "Scientifique"];
    const timeRanges = ["8-12", "12-14", "14-18", "18-23"];

    // Initialiser un objet pour stocker la somme des page_views pour chaque profil par plage horaire
    let profileData = {};
    profiles.forEach(profile => {
        profileData[profile] = {};
        timeRanges.forEach(range => {
            profileData[profile][range] = 0;
        });
    });

    // Pour chaque enregistrement filtré, déterminer sa plage horaire et sommer les page_views pour son profil
    filteredData.forEach(lycee => {
        let profile = lycee.profile_type;
        if (profiles.includes(profile)) {
            const hour = parseInt(lycee.timestamp.split(' ')[1].split(':')[0], 10);
            let rangeFound = timeRanges.find(range => {
                const [start, end] = range.split('-').map(Number);
                return hour >= start && hour < end;
            });
            if (rangeFound) {
                profileData[profile][rangeFound] += lycee.page_views;
            }
        }
    });
    console.log("Données par profil pour radar:", profileData);

    // Créer les indicateurs pour le radar chart : une pour chaque plage horaire
    let indicators = timeRanges.map(range => {
        let maxVal = 0;
        profiles.forEach(profile => {
            maxVal = Math.max(maxVal, profileData[profile][range]);
        });
        return { text: range, max: maxVal + (maxVal * 0.1) };
    });

    // Préparer la série pour le radar chart : un objet par profil avec un tableau de valeurs
    let seriesData = profiles.map(profile => ({
        name: profile,
        value: timeRanges.map(range => profileData[profile][range])
    }));

    console.log("Indicateurs radar:", indicators);
    console.log("Données série radar:", seriesData);

    // Initialiser (ou réutiliser) l'instance ECharts dans le conteneur "radarChart"
    const radarDom = document.getElementById('radarChart');
    if (!radarChartInstance) {
        radarChartInstance = echarts.init(radarDom);
    }
    const option = {
        title: {
            text: 'Activité des profils par plage horaire',
            subtext: 'Somme des pages vues',
            top: 10,
            left: 10
        },
        tooltip: {
            trigger: 'item'
        },
        legend: {
            data: profiles,
            bottom: 10,
            type: 'scroll'
        },
        visualMap: {
            top: 'middle',
            right: 10,
            color: ['red', 'yellow'],
            calculable: true
        },
        radar: {
            indicator: indicators
        },
        series: [{
            type: 'radar',
            symbol: 'circle',
            lineStyle: {
                width: 1
            },
            data: seriesData
        }]
    };
    radarChartInstance.setOption(option);
    console.log("Radar chart mis à jour.");
}


// Variable globale pour l'instance ECharts du camembert
let echartPieChart = null;

function updateProfilePieChart(filteredData) {
    // Comptage des occurrences pour chaque type de profil
    const counts = {};
    filteredData.forEach(lycee => {
        counts[lycee.profile_type] = (counts[lycee.profile_type] || 0) + 1;
    });

    // Transformer les données pour ECharts
    const data = Object.keys(counts).map(profile => ({
        value: counts[profile],
        name: profile
    }));

    // Initialiser ou récupérer l'instance ECharts sur le conteneur
    const chartDom = document.getElementById('echartPie');
    if (!echartPieChart) {
        echartPieChart = echarts.init(chartDom);
    }

    // Définir l'option du camembert
    const option = {
        tooltip: {
            trigger: 'item'
        },
        legend: {
            top: '5%',
            left: 'center'
        },
        series: [
            {
                name: 'Profils',
                type: 'pie',
                radius: ['40%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false,
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 20,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: data
            }
        ]
    };

    echartPieChart.setOption(option);

    // Ajouter l'écouteur de clic une seule fois
    if (!echartPieChart.__hasClickEvent) {
        echartPieChart.on('click', function (params) {
            console.log("Slice cliqué :", params.name);
            // Si le même type est cliqué, on le désélectionne
            if (selectedProfileFromPie === params.name) {
                selectedProfileFromPie = null;
            } else {
                selectedProfileFromPie = params.name;
            }
            // Réactualiser l'interface en appliquant ce nouveau filtre
            updateUI();
        });
        echartPieChart.__hasClickEvent = true;
    }
}




// Mise à jour du nuage de mots avec WordCloud2
function updateWordCloudForContainer(containerId, filteredData) {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error("Conteneur non trouvé :", containerId);
        return;
    }
    let allWords = [];
    filteredData.forEach(l => {
        l.articles_visited.split(',').forEach(word => {
            allWords.push(word.trim());
        });
    });
    let freq = {};
    allWords.forEach(w => {
        freq[w] = (freq[w] || 0) + 1;
    });
    let entries = [];
    for (let w in freq) {
        entries.push([w, freq[w]]);
    }
    WordCloud(container, {
        list: entries,
        weightFactor: size => Math.pow(size, 1.5) * 1,
        fontFamily: 'Poppins, sans-serif',
        color: (word, weight) => {
            const hue = Math.floor(Math.random() * 360);
            return `hsl(${hue}, 70%, 50%)`;
        },
        classes: 'word-cloud-item',
        rotate: () => Math.floor(Math.random() * 3 - 1) * 30,
        backgroundColor: 'transparent'
    });
}


function updateWordClouds(filteredData) {
    updateWordCloudForContainer("wordCloud1Content", filteredData);
    updateWordCloudForContainer("wordCloud2Content", filteredData);
    updateWordCloudForContainer("wordCloud3Content", filteredData);
}



// Variable globale pour conserver l'instance du camembert
let pieChartInstance = null;

// Mise à jour du camembert avec Chart.js
function updatePieChart(lycees) {
    const ctx = document.getElementById('pieChart').getContext('2d');
    let counts = {};
    lycees.forEach(l => {
        counts[l.profile_type] = (counts[l.profile_type] || 0) + 1;
    });
    let labels = Object.keys(counts);
    let data = Object.values(counts);

    if (pieChartInstance) {
        pieChartInstance.destroy();
    }

    pieChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(108, 82, 199, 0.8)',
                    'rgba(255, 104, 1, 0.8)',
                    'rgba(25, 153, 106, 0.8)',
                    'rgba(68, 123, 205, 0.8)'
                ],
                borderWidth: 0,
                hoverOffset: 10,
                spacing: 5
            }]
        },
        options: {
            cutout: '70%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20,
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    bodyFont: { size: 14 },
                    titleFont: { size: 16 },
                    boxPadding: 10
                }
            },
            animation: {
                duration: 800,
                easing: 'easeOutQuart'
            }
        }
    });
}

