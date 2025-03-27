# Utiliser une image de base officielle Python
FROM python:3.9-slim

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de l'application dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger le modèle spaCy
RUN python -m spacy download en_core_web_sm

# Exposer le port sur lequel l'application va tourner
EXPOSE 5000

# Commande pour exécuter l'application
CMD ["python", "app.py"]
