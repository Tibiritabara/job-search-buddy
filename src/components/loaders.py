from haystack import component
from pydantic import FilePath

from utils.clients import unstructured_client


@component
class CvLoader:
    @component.output_types(cv_contents=str)
    def run(
        self,
        cv_file_path: FilePath,
        cv_file_name: str,
    ) -> str:
        with unstructured_client as client:
            response = client.general.partition(
                request={
                    "partition_parameters": {
                        "files": {
                            "content": open(cv_file_path, "rb"),
                            "file_name": cv_file_name,
                        },
                    },
                },
            )
        if response is None or response.elements is None:
            raise ValueError("No response from the model")
        return response.elements[0]["metadata"]["text_as_html"]
