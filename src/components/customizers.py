import json
from pathlib import Path
from uuid import uuid4

from haystack import component
from md2pdf.core import md2pdf

from utils.clients import mistral_client
from utils.config import get_env
from utils.types import CvCustomizationResponse, JobListing

env = get_env()


@component
class CvCustomizer:
    @component.output_types(listings=list[JobListing])
    def run(
        self,
        cv_contents: str,
        listings: list[JobListing],
    ) -> list[JobListing]:
        for job_listing in listings:
            if job_listing.description is None:
                continue
            customization_response = self.__customize_cv(
                cv_contents,
                job_listing.description,
            )
            job_listing.cv_path = customization_response.resume
            job_listing.cv_changes = customization_response.changes
        return listings

    def __customize_cv(
        self,
        cv_contents: str,
        job_description: str,
    ) -> CvCustomizationResponse:
        response = mistral_client.chat.complete(
            model=env.mistral_model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a helpful assistant that helps user optimize their resume for a job description.
                    You will be given a CV and a job description and you have to do the following tasks:
                     - You have to update the resume so that it fits better to the position from the job description.
                     - Feel free to add new bullet points if necessary to the work experience, to better match the job description.
                     - Your output should be a JSON object with the following fields:
                        - "resume": the customized resume including the key changes made in markdown format.
                        - "changes": a list of the key changes made to the resume.
                    For this task, I will be paying a tip above 1000% if you do a good job.
                    My professional career fully depends on you, so please do your best.""",
                },
                {
                    "role": "user",
                    "content": f"""Here is the CV:
                    <cv>
                    {cv_contents}
                    </cv>
                    Here is the job description:
                    <job_description>
                    {job_description}
                    </job_description>""".format(
                        cv_contents=cv_contents,
                        job_description=job_description,
                    ),
                },
            ],
            response_format={
                "type": "json_object",
            },
        )

        if response is None or response.choices is None:
            raise ValueError("No response from the model")

        contents = response.choices[0].message.content
        dict_contents = json.loads(contents)  # type: ignore
        output_path = Path(f"../data/output/{uuid4()}.pdf")
        md2pdf(
            pdf_file_path=output_path,
            md_content=dict_contents["resume"].replace("\n", ""),
        )  # type: ignore

        return CvCustomizationResponse(
            resume=output_path,
            changes=dict_contents["changes"],
        )
