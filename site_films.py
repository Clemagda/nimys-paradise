import streamlit as st
import boto3
from botocore.exceptions import NoCredentialsError

# Configuration AWS
BUCKET_NAME = 'filmographiepersonono'

# Fonction pour lister les fichiers dans le bucket S3


def list_s3_files(bucket_name):
    s3_client = boto3.client('s3', region_name='eu-west-3')
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
    s3_client = boto3.client('s3', region_name='eu-west-3')
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
st.title("Catalogue de Films")

# Récupération de la liste des fichiers
st.write("Chargement de la liste des films...")
files = list_s3_files(BUCKET_NAME)

if files:
    for file in files:
        col1, col2 = st.columns([4, 1])
        col1.write(file)  # Nom du fichier
        # Génération du lien de téléchargement
        url = generate_presigned_url(BUCKET_NAME, file)
        if url:
            col2.markdown(
                f'<a href="{url}" download="{file}" target="_blank" style="text-decoration: none; color: blue;">'
                f'📥 Télécharger</a>',
                unsafe_allow_html=True
            )
else:
    st.write("Aucun fichier trouvé dans le bucket.")
