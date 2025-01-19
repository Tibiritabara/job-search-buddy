import uuid

from haystack import component
from linkedin_api import Linkedin
from pydantic import HttpUrl

from utils.config import get_env
from utils.types import JobListing

env = get_env()


@component
class LinkedInScanner:
    limit: int = 10
    _client: Linkedin

    def __init__(self, limit: int = 10):
        self.limit = limit
        self._client = Linkedin(
            env.linkedin_username.get_secret_value(),  # pylint: disable=no-member
            env.linkedin_password.get_secret_value(),  # pylint: disable=no-member
        )

    @component.output_types(listings=list[JobListing])
    def run(self, keywords: list[str], location: str) -> list[JobListing]:
        jobs = self._client.search_jobs(
            keywords=",".join(keywords),
            location=location,
            limit=self.limit,
        )
        job_listings = [
            JobListing(
                id=uuid.uuid4(),
                tracking_urn=job["trackingUrn"],
                url=HttpUrl(
                    f"{str(env.linkedin_job_page_prefix)}/{job['trackingUrn'].split(':')[-1]}"
                ),
                title=job["title"],
                poster_id=job["poster_id"],
                location=location,
                description=job["description"],
                reposted=job["repostedJob"],
                keywords=keywords,
            )
            for job in jobs
        ]

        for job_listing in job_listings:
            job_listing = self.__get_listing_details(job_listing)
        return job_listings

    def __get_listing_details(
        self,
        job_listing: JobListing,
    ) -> JobListing:
        job_details = self._client.get_job(job_listing.tracking_urn.split(":")[-1])
        job_listing.company = job_details["companyDetails"][
            "com.linkedin.voyager.deco.jobs.web.shared.WebCompactJobPostingCompany"
        ]["name"]
        job_listing.description = job_details["description"]["text"]
        return job_listing
