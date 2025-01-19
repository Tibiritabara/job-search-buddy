"""
Set of configurations for the application to work
"""

from functools import lru_cache

from pydantic import Field, FilePath, HttpUrl, SecretStr
from pydantic_settings import BaseSettings


class Environment(BaseSettings):
    """
    Class to hold and validate the different environment variables

    Attributes:
        linkedin_username (str): Linkedin username
        linkedin_password (str): Linkedin password
        mistral_api_key (str): Mistral API key
        mistral_model (str): Mistral model
        unstructured_url (str): Unstructured API url
        unstructured_api_key (str): Unstructured API key
        linkedin_job_page_prefix (str): Linkedin job page prefix
        google_credentials_path (FilePath): Path to the Google credentials file
        google_token_path (FilePath): Path to the Google token file
        openai_api_key (str): Azure OpenAI key
    """

    # App Settings
    linkedin_username: SecretStr = Field()
    linkedin_password: SecretStr = Field()
    mistral_api_key: SecretStr = Field()
    mistral_model: str = Field()
    unstructured_url: HttpUrl = Field()
    unstructured_api_key: SecretStr = Field()
    linkedin_job_page_prefix: HttpUrl = Field()
    google_credentials_path: FilePath = Field()
    google_token_path: FilePath = Field()
    openai_api_key: SecretStr = Field()


@lru_cache
def get_env():
    return Environment()  # type: ignore
