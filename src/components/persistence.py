from haystack import component

from utils.clients import weaviate_client
from utils.config import get_env
from utils.types import JobListing

env = get_env()


@component
class ListingsPersistence:
    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @component.output_types(listings=list[JobListing])
    def run(self, listings: list[JobListing]) -> list[JobListing]:
        listings_collection = weaviate_client.collections.get(self.collection_name)
        with listings_collection.batch.dynamic() as batch:
            for listing in listings:
                batch.add_object(
                    properties=listing.model_dump(exclude={"id"}, exclude_none=True),
                    uuid=listing.id,
                )

        return listings
