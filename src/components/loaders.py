from pathlib import Path
from typing import Any

from haystack import component

from utils.clients import unstructured_client


@component
class CvLoader:
    @component.output_types(cv_contents=dict[str, Any])
    def run(
        self,
        cv_file_path: str,
        cv_file_name: str,
    ) -> dict[str, Any]:
        file_path = Path(cv_file_path)
        with unstructured_client as client:
            response = client.general.partition(
                request={
                    "partition_parameters": {
                        "files": {
                            "content": open(file_path, "rb"),
                            "file_name": cv_file_name,
                        },
                    },
                },
            )
        if response is None or response.elements is None:
            raise ValueError("No response from the model")
        return {"cv_text": response.elements[0]["metadata"]["text_as_html"]}
