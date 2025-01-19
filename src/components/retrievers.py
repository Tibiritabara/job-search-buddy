from typing import Any

from haystack import component

from utils.clients import weaviate_client
from utils.config import get_env
from utils.types import JobListing, JobListings

env = get_env()


@component
class JobApplicationsRetriever:
    """
    Validates listings by checking if they have been reposted or if they are already in the database.
    """

    collection_name: str = "Listings"

    def __init__(self, collection_name: str = "Listings"):
        self.collection_name = collection_name

    @component.output_types(listings=dict[str, Any])
    def run(self, query: str) -> dict[str, Any]:
        listings_collection = weaviate_client.collections.get(self.collection_name)

        response = listings_collection.query.hybrid(
            query=query,
            target_vector=["title", "description", "location", "keywords", "status"],
            limit=5,
        )

        listings: list[JobListing] = []
        for obj in response.objects:
            listings.append(JobListing(id=obj.uuid, **obj.properties))  # type: ignore

        return JobListings(listings=listings).model_dump()
