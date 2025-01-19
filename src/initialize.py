from weaviate.classes.config import Configure, DataType, Property

from utils.clients import weaviate_client

weaviate_client.collections.create(
    name="Listings",
    vectorizer_config=[
        Configure.NamedVectors.text2vec_mistral(
            name="company_name",
            source_properties=["company_name"],
        ),
        Configure.NamedVectors.text2vec_mistral(
            name="title",
            source_properties=["title"],
        ),
        Configure.NamedVectors.text2vec_mistral(
            name="description",
            source_properties=["description"],
        ),
        Configure.NamedVectors.text2vec_mistral(
            name="location",
            source_properties=["location"],
        ),
        Configure.NamedVectors.text2vec_mistral(
            name="keywords",
            source_properties=["keywords"],
        ),
        Configure.NamedVectors.text2vec_mistral(
            name="status",
            source_properties=["status"],
        ),
    ],
    properties=[
        Property(name="company_name", data_type=DataType.TEXT),
        Property(name="tracking_urn", data_type=DataType.TEXT),
        Property(name="title", data_type=DataType.TEXT),
        Property(name="url", data_type=DataType.TEXT),
        Property(name="location", data_type=DataType.TEXT),
        Property(name="description", data_type=DataType.TEXT),
        Property(name="reposted", data_type=DataType.BOOL),
        Property(name="poster_id", data_type=DataType.TEXT),
        Property(name="keywords", data_type=DataType.TEXT_ARRAY),
        Property(name="cv_path", data_type=DataType.TEXT),
        Property(name="cv_changes", data_type=DataType.TEXT_ARRAY),
        Property(name="status", data_type=DataType.TEXT),
        Property(name="application_date", data_type=DataType.DATE),
    ],
)
