from supabase import create_client, Client
from core import settings
import hashlib

BUCKET = settings.BUCKET_NAME

def get_supabase_client():
    """
    Função para criar e retornar o cliente Supabase,
    abrindo a conexão somente quando necessário.
    """
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    return create_client(url, key)


def generate_image_hash(image_name):
    """
    Gera um hash SHA-256 único para o nome do arquivo.
    """
    hash_object = hashlib.sha256(image_name.encode())
    return hash_object.hexdigest()

def upload_avatar_to_supabase(image_file, image_name):
    """
    Faz o upload do arquivo de imagem na pasta 'avatars' no Supabase.
    """
    try:
        supabase: Client = get_supabase_client()

        unique_image_name = f"{generate_image_hash(image_name)}_{image_name}"
        file_path = f"avatar/{unique_image_name}"
        file_content = image_file.read()
        response = supabase.storage.from_(BUCKET).upload(file_path, file_content)
        if response.path:
            public_url = supabase.storage.from_(BUCKET).get_public_url(response.path)
            return public_url
        else:
            raise Exception("Erro no upload: caminho não encontrado na resposta")

    except Exception as e:
        raise Exception(f"Erro no upload do avatar: {str(e)}")


def upload_services_to_supabase(image_file, image_name):
    """
    Faz o upload do arquivo de imagem na pasta 'services' no Supabase.
    """
    try:
        supabase: Client = get_supabase_client()
        unique_image_name = f"{generate_image_hash(image_name)}_{image_name}"
        file_path = f"services/{unique_image_name}"
        file_content = image_file.read()
        response = supabase.storage.from_(BUCKET).upload(file_path, file_content)
        if response.path:
            public_url = supabase.storage.from_(BUCKET).get_public_url(response.path)
            return public_url
        else:
            raise Exception("Erro no upload: caminho não encontrado na resposta")
    except Exception as e:
        raise Exception(f"Erro no upload dos serviços: {str(e)}")
