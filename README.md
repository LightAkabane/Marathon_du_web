# Le Futur de l'Actu en Bref

Ce dépôt contient l'ensemble des ressources et documents liés au projet **"Le futur de l'actu en bref"** dans le cadre du Master – Parcours Communication Numérique et Organisations. Ce projet a été réalisé pour Brief.me, un média indépendant sans publicité, financé par ses abonnés, et destiné notamment à alimenter des fonds documentaires utilisés en HGGSP dans les lycées.

## Contexte

Brief.me souhaite améliorer son accessibilité auprès des lycéen·e·s et de leurs enseignant·e·s. Le projet vise à :
- Analyser les parcours utilisateurs en étudiant des données issues des consultations.
- Identifier les profils d’utilisateurs en croisant les timestamps, les identifiants de lycée et d’autres informations (articles populaires, moments de consultation, thématiques, etc.).
- Différencier l’usage du média comme fond documentaire (recherche et consultation d’articles anciens) ou actualité (articles récents).
- Préparer l’outil à intégrer les données à venir de 2025.

## Objectifs de Communication

L’objectif est de créer des supports de communication qui respectent la charte graphique de Brief.me afin de valoriser le média auprès des élèves et des enseignant·e·s. Deux vidéos promotionnelles ont été conçues :
- **Pour les élèves** : mettant en avant des témoignages d’élève.
- **Pour les enseignant·e·s** : présentant des témoignages d’enseignant·e·s et soulignant l’usage préféré de Brief.me d’après l’analyse des données.

## Analyse de Données

Les principales étapes de l’analyse de données incluent :

1. **Identification des profils d’utilisateurs**  
   - Croisement des timestamps et des identifiants de lycée.
   - Analyse des articles populaires, des moments de consultation et des thématiques abordées.

2. **Différenciation des usages du média**  
   - Détermination de l’utilisation de Brief.me comme fond documentaire versus son usage pour l’actualité.

3. **Préparation pour les données futures**  
   - Adaptation de l’outil d’analyse pour intégrer les données supplémentaires prévues pour 2025.

### Données utilisées

Un fichier CSV (≈5 millions de lignes) contenant :
- Identifiants de lycée,
- Timestamps,
- URL (contenant des informations sur la date de publication, le nom de l'article, et le moyen d'accès à l'article).

Lien vers les données : [Accéder aux données](https://upvdrive.univ-montp3.fr/s/qGoqKpkLxZiTFDG)

## Contenu du Dépôt

- **/docs** : Documentation détaillée sur le projet.
- **/data** : Exemple de jeu de données (ou instructions pour récupérer le jeu de données complet).
- **/scripts** : Scripts d'analyse de données et de préparation des supports de communication.
- **/videos** : Prototypes ou versions finales des vidéos promotionnelles pour élèves et enseignant·e·s.
- **README.md** : Ce fichier de présentation.

## Installation et Usage

1. **Cloner le dépôt :**

   ```bash
   git clone https://github.com/LightAkabane/le-futur-de-l-actu-en-bref.git
   cd le-futur-de-l-actu-en-bref
