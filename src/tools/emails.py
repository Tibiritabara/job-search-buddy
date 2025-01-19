from typing import Any

from haystack import Pipeline
from haystack.tools import Tool

from components.emails import EmailReader


class EmailValidator:
    def __init__(self):
        self.emails_reader = EmailReader()  # type: ignore

    def generate_pipeline(
        self,
    ) -> Pipeline:
        pipeline = Pipeline()
        pipeline.add_component("emails_reader", self.emails_reader)
        return pipeline

    def generate_tool(self) -> Tool:
        pipeline = self.generate_pipeline()

        def run(
            self,
        ) -> dict[str, Any]:
            return pipeline.run({})

        return Tool(
            name="email_reader",
            description="Search in the inbox for unread emails connected to the job applications",
            function=run,
            parameters={},
        )
