from typing import Any

from haystack import component
from weaviate.classes.query import Filter

from utils.clients import weaviate_client
from utils.config import get_env
from utils.types import JobListing, JobListings

env = get_env()


@component
class ListingsValidator:
    """
    Validates listings by checking if they have been reposted or if they are already in the database.
    """

    def __init__(self, collection_name: str):
        self.collection_name = collection_name

    @component.output_types(listings=dict[str, Any])
    def run(self, listings: dict[str, Any]) -> dict[str, Any]:
        final_listings: list[JobListing] = []
        job_listings = [JobListing(**listing) for listing in listings]
        listings_collection = weaviate_client.collections.get(self.collection_name)
        # Get existing listing by tracking_url
        for listing in job_listings:
            if listing.reposted:
                continue

            response = listings_collection.query.fetch_objects(
                filters=Filter.by_property("tracking_urn").equal(listing.tracking_urn),
                limit=1,
            )

            if len(response.objects) > 0:
                continue

            final_listings.append(listing)

        return JobListings(listings=final_listings).model_dump()
