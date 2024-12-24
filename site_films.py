import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import os
import json

# Configuration AWS
BUCKET_NAME = 'filmographiepersonono'

# Fonction pour lister les fichiers dans le bucket S3


def list_s3_files(bucket_name):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION', 'eu-west-3')
    )
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            return [obj['Key'] for obj in response['Contents']]
        else:
            return []
    except NoCredentialsError:
        st.error("AWS credentials not found.")
        return []

# Fonction pour générer une URL signée


def generate_presigned_url(bucket_name, object_key, expiration=3600):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_DEFAULT_REGION',
                              'eu-west-3')  # Région par défaut
    )
    try:
        return s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': object_key},
            ExpiresIn=expiration
        )
    except Exception as e:
        st.error("Erreur lors de la génération du lien : " + str(e))
        return None

# Fonction pour charger et enregistrer l'état des "films vus"


def load_seen_movies():
    if os.path.exists("seen_movies.json"):
        with open("seen_movies.json", "r") as file:
            return json.load(file)
    return {}


def save_seen_movies(seen_movies):
    with open("seen_movies.json", "w") as file:
        json.dump(seen_movies, file)


# Charger l'état initial des films vus
seen_movies = load_seen_movies()

# Interface Streamlit
st.markdown(
    "<h1 style='text-align: center; color: #FF5733;'>🎬 Nimy's Paradise</h1>",
    unsafe_allow_html=True
)

# Récupération et affichage des fichiers
files = list_s3_files(BUCKET_NAME)

if files:
    # Barre de recherche
    search = st.text_input("🔍 Rechercher un film (partie du nom)", "")
    if search:
        files = [file for file in files if search.lower() in file.lower()]
        if not files:
            st.warning("Aucun film trouvé pour votre recherche.")

    # Mise en avant des derniers ajouts
    st.markdown("### 🆕 Derniers ajouts")
    latest_files = files[:5]  # Affiche les 5 fichiers les plus récents
    with st.container():
        cols = st.columns(5)
        for i, file in enumerate(latest_files):
            url = generate_presigned_url(BUCKET_NAME, file)
            if url:
                with cols[i % 5]:
                    st.markdown("📽️ **" + file + "**")
                    if file.endswith(('.mp4', '.mkv')):
                        st.markdown(
                            '<a href="' + url + '" target="_blank" style="text-decoration: none; color: white; background: #28a745; padding: 8px 12px; border-radius: 5px;">▶️ Visionner</a>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<a href="' + url + '" download style="text-decoration: none; color: white; background: #007BFF; padding: 8px 12px; border-radius: 5px;">📥 Télécharger</a>',
                            unsafe_allow_html=True
                        )

    # Affichage des films sous forme de liste
    st.markdown("### 🎥 Tous les films")
    with st.container():
        scroll_style = """
            <style>
            .scrollable-container {
                max-height: 400px;
                overflow-y: auto;
                border: 1px solid #333;
                padding: 10px;
                border-radius: 10px;
                background-color: #202020;
            }
            .film-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid #444;
            }
            .film-item:last-child {
                border-bottom: none;
            }
            .checkbox {
                margin-right: 10px;
            }
            .film-title {
                display: flex;
                align-items: center;
            }
            .download-btn {
                text-decoration: none;
                color: #FFFFFF; /* Couleur blanche pour le texte */
                background: #0056B3; /* Bleu plus foncé pour améliorer le contraste */
                padding: 10px 15px; /* Augmente le padding pour rendre le bouton plus grand */
                border-radius: 5px;
                font-size: 14px; /* Augmente la taille du texte */
                font-weight: bold; /* Rend le texte plus gras */
                display: inline-block;
                text-align: center;
            }
            .download-btn:hover {
                background: #007BFF; /* Couleur légèrement plus claire au survol */
            }
            </style>
        """
        st.markdown(scroll_style, unsafe_allow_html=True)
        st.markdown('<div class="scrollable-container">',
                    unsafe_allow_html=True)
        for file in files:
            url = generate_presigned_url(BUCKET_NAME, file)
            if url:
                # Ajout d'une case à cocher alignée avec le titre du film
                st.markdown('<div class="film-item">', unsafe_allow_html=True)
                col1, col2 = st.columns([0.1, 0.9])
                with col1:
                    checkbox = st.checkbox("", value=seen_movies.get(
                        file, False), key=file, help="Marquer comme vu")
                    seen_movies[file] = checkbox
                with col2:
                    st.markdown('<span class="film-title">📽️ ' +
                                file + '</span>', unsafe_allow_html=True)
                    if file.endswith(('.mp4', '.mkv')):
                        st.markdown(
                            '<a class="download-btn" href="' + url + '" target="_blank">▶️ Visionner</a>',
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            '<a class="download-btn" href="' + url + '" download>📥 Télécharger</a>',
                            unsafe_allow_html=True
                        )
                st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Sauvegarder l'état des films vus
    save_seen_movies(seen_movies)
else:
    st.error("Aucun fichier trouvé dans le bucket.")
