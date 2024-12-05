import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError
import os

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
        st.error(f"Erreur lors de la génération du lien : {e}")
        return None


# Interface Streamlit
st.markdown(
    "<h1 style='text-align: center; color: #FF5733;'>🎬 A la carte </h1>",
    unsafe_allow_html=True
)

# Barre de recherche
search = st.text_input("🔍 Rechercher un film (partie du nom)", "")

files = list_s3_files(BUCKET_NAME)

if files:
    # Filtrer les fichiers en fonction de la recherche
    if search:
        files = [file for file in files if search.lower() in file.lower()]
        if not files:
            st.warning("Aucun film trouvé pour votre recherche.")

    # Affichage des films sous forme de cartes
    for file in files:
        url = generate_presigned_url(BUCKET_NAME, file)
        if url:
            st.markdown(
                f"""
                <div style='border: 2px solid #FF5733; padding: 10px; border-radius: 10px; margin-bottom: 10px; background-color: #333333;'>
                    <h4 style='color: #FFFFFF;'>🎥 {file}</h4>
                    <a href="{url}" target="_blank" style='text-decoration: none; color: white; background: #007BFF; padding: 8px 12px; border-radius: 5px;'>📥 Télécharger</a>
                </div>
                """,
                unsafe_allow_html=True
            )
else:
    st.error("Aucun fichier trouvé dans le bucket.")
