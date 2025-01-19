from haystack import component
from weaviate.classes.query import Filter

from utils.clients import weaviate_client
from utils.config import get_env
from utils.types import JobListing

env = get_env()


@component
class ListingsValidator:
    """
    Validates listings by checking if they have been reposted or if they are already in the database.
    """

    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @component.output_types(listings=list[JobListing])
    def run(self, listings: list[JobListing]) -> list[JobListing]:
        final_listings: list[JobListing] = []
        listings_collection = weaviate_client.collections.get(self.collection_name)
        # Get existing listing by tracking_url
        for listing in listings:
            if listing.reposted:
                continue

            response = listings_collection.query.fetch_objects(
                filters=Filter.by_property("tracking_urn").equal(listing.tracking_urn),
                limit=1,
            )

            if len(response.objects) > 0:
                continue

            final_listings.append(listing)

        return final_listings
