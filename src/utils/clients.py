import weaviate
from mistralai import Mistral
from unstructured_client import UnstructuredClient

from utils.config import get_env

env = get_env()

weaviate_client = weaviate.connect_to_local()
mistral_client = Mistral(api_key=env.mistral_api_key.get_secret_value())
unstructured_client = UnstructuredClient(
    api_key_auth=env.unstructured_api_key.get_secret_value(),
    server_url=str(env.unstructured_url),
)
