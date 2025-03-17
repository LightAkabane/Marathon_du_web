from django.shortcuts import render, redirect
from .models import UserData, LyceeData
from .forms import CSVImportForm
import csv
from io import TextIOWrapper
import json
from django.core import serializers

def dashboard(request):
    lycees = LyceeData.objects.all()
    # On va transformer la queryset en liste de dictionnaires
    # pour injecter dans un script JS de façon simple
    lycee_list = []
    for obj in lycees:
        lycee_list.append({
            'user_id': obj.user_id,
            'lycee_name': obj.lycee_name,
            'latitude': obj.latitude,
            'longitude': obj.longitude,
            'profile_type': obj.profile_type,
            'usage_purpose': obj.usage_purpose,
            'articles_visited': obj.articles_visited,
            'page_views': obj.page_views,
            'session_duration': obj.session_duration,
            'timestamp': obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        })

    # On convertit en JSON
    lycees_json = json.dumps(lycee_list)

    return render(request, 'dashboard/dashboard.html', {
        'lycees': lycees,      # Pour le tableau
        'lycees_json': lycees_json,  # Pour le JS
    })


def import_csv(request):
    """
    Vue d'import CSV.
    """
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            # Lecture du CSV en utilisant TextIOWrapper pour décoder en UTF-8
            csv_reader = csv.DictReader(TextIOWrapper(csv_file.file, encoding='utf-8'))

            for row in csv_reader:
                # On crée un nouvel objet LyceeData par ligne
                LyceeData.objects.create(
                    user_id=row['user_id'],
                    lycee_name=row['lycee_name'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    profile_type=row['profile_type'],
                    usage_purpose=row['usage_purpose'],
                    articles_visited=row['articles_visited'], # texte brut
                    page_views=int(row['page_views']),
                    session_duration=int(row['session_duration']),
                    # timestamp = parsing direct : row['timestamp']
                    # Astuce : si besoin, on peut parser la string en datetime 
                    # via datetime.strptime ou utiliser l’objet django utils parse_datetime
                    # Mais dans beaucoup de cas, le simple parse sur DateTimeField fonctionne
                    # si le format est "YYYY-MM-DD HH:MM:SS".
                    timestamp=row['timestamp']
                )

            return redirect('dashboard')
    else:
        form = CSVImportForm()

    return render(request, 'dashboard/import.html', {'form': form})
