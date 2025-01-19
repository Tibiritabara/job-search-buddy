from typing import Any

from haystack import Pipeline
from haystack.tools import Tool

from components.customizers import CvCustomizer
from components.loaders import CvLoader
from components.persistence import ListingsPersistence
from components.retrievers import JobApplicationsRetriever
from components.scanners import LinkedInScanner
from components.validators import ListingsValidator


class JobSearchAndPreparation:
    def __init__(self):
        self.listings_scanner = LinkedInScanner()  # type: ignore
        self.listings_validator = ListingsValidator(collection_name="Listings")  # type: ignore
        self.cv_loader = CvLoader()  # type: ignore
        self.cv_customizer = CvCustomizer()  # type: ignore
        self.listings_persistence = ListingsPersistence(collection_name="Listings")  # type: ignore

    def generate_pipeline(self) -> Pipeline:
        pipeline = Pipeline()
        pipeline.add_component("cv_loader", self.cv_loader)
        pipeline.add_component("listings_scanner", self.listings_scanner)
        pipeline.add_component("listings_validator", self.listings_validator)
        pipeline.add_component("cv_customizer", self.cv_customizer)
        pipeline.add_component("listings_persistence", self.listings_persistence)

        pipeline.connect("listings_scanner.listings", "listings_validator.listings")
        pipeline.connect("cv_loader.cv_contents", "cv_customizer.cv_contents")
        pipeline.connect("listings_validator.listings", "cv_customizer.listings")
        pipeline.connect("cv_customizer.listings", "listings_persistence.listings")
        return pipeline

    def generate_tool(self) -> Tool:
        pipeline = self.generate_pipeline()

        def run(
            cv_file_path: str,
            cv_file_name: str,
            keywords: list[str],
            location: str,
        ) -> dict[str, Any]:
            return pipeline.run(
                {
                    "cv_file_path": cv_file_path,
                    "cv_file_name": cv_file_name,
                    "keywords": keywords,
                    "location": location,
                }
            )

        return Tool(
            name="job_search_and_preparation",
            description="Search for job listings on LinkedIn and prepare the custom CV for each listing",
            function=run,
            parameters={
                "type": "object",
                "properties": {
                    "cv_file_path": {
                        "type": "string",
                        "description": "The path to the CV file. Only send the path as a string",
                    },
                    "cv_file_name": {
                        "type": "string",
                        "description": "The name and extensionof the CV file to be used for customizing",
                    },
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string",
                        },
                        "description": "The keywords to search for in the job listings. Use a maximum of 2 keywords",
                    },
                    "location": {
                        "type": "string",
                        "description": "The location to search for job listings",
                    },
                },
                "required": ["cv_file_path", "cv_file_name", "keywords", "location"],
            },
        )


class JobApplicationsSearch:
    def __init__(self):
        self.job_applications_retriever = JobApplicationsRetriever()  # type: ignore

    def generate_pipeline(self) -> Pipeline:
        pipeline = Pipeline()
        pipeline.add_component(
            "job_applications_retriever", self.job_applications_retriever
        )
        return pipeline

    def generate_tool(self) -> Tool:
        pipeline = self.generate_pipeline()

        def run(query: str) -> dict[str, Any]:
            return pipeline.run({"query": query})

        return Tool(
            name="job_applications_search",
            description="Search for previous job applications already sent",
            function=run,
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search in the existing applications database",
                    },
                },
                "required": ["query"],
            },
        )
