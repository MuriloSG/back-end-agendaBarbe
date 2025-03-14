from supabase import create_client, Client
from core import settings

BUCKET = settings.BUCKET_NAME

def get_supabase_client():
    """
    Função para criar e retornar o cliente Supabase,
    abrindo a conexão somente quando necessário.
    """
    url = settings.SUPABASE_URL
    key = settings.SUPABASE_KEY
    return create_client(url, key)


def upload_avatar_to_supabase(image_file, image_name):
    """
    Faz o upload do arquivo de imagem na pasta 'avatars' no Supabase.
    """
    try:
        supabase: Client = get_supabase_client()

        file_path = f"avatar/{image_name}"
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
        file_path = f"services/{image_name}"
        file_content = image_file.read()
        response = supabase.storage.from_(BUCKET).upload(file_path, file_content)
        if response.path:
            public_url = supabase.storage.from_(BUCKET).get_public_url(response.path)
            return public_url
        else:
            raise Exception("Erro no upload: caminho não encontrado na resposta")
    except Exception as e:
        raise Exception(f"Erro no upload dos serviços: {str(e)}")
