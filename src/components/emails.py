import json
from datetime import datetime, timedelta

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from haystack import component

from utils.clients import mistral_client
from utils.config import get_env
from utils.types import EmailValidationResponse

env = get_env()

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]


@component
class EmailReader:
    def __init__(self, time_to_search: int = 2):
        self.time_to_search = time_to_search

    @component.output_types(email_validation_response=EmailValidationResponse)
    def run(
        self,
    ) -> list[EmailValidationResponse]:
        creds = Credentials.from_authorized_user_file(
            env.google_credentials_path, SCOPES
        )
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    env.google_credentials_path,
                    SCOPES,
                )
                creds = flow.run_local_server(port=0)

            with open(env.google_token_path, "w") as token:
                token.write(creds.to_json())

        service = build("gmail", "v1", credentials=creds)
        one_hour_ago = int(
            (datetime.now() - timedelta(hours=self.time_to_search)).timestamp()
        )
        # Get unread messages
        results = (
            service.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], q="is:unread")
            .execute()
        )
        messages = results.get("messages", [])

        if len(messages) == 0:
            return []

        recent_messages = []
        for message in messages:
            msg = (
                service.users().messages().get(userId="me", id=message["id"]).execute()
            )
            internal_date = int(msg["internalDate"]) // 1000  # Convert to seconds
            if internal_date >= one_hour_ago:
                recent_messages.append(msg)

        if len(recent_messages) == 0:
            return []

        print(f"Found {len(recent_messages)} unread messages from the last hour.")

        validations: list[EmailValidationResponse] = []
        for msg in recent_messages:
            email_data = msg["payload"]["headers"]

            # Get email details
            subject = next(
                (
                    header["value"]
                    for header in email_data
                    if header["name"] == "Subject"
                ),
                "No subject",
            )
            sender = next(
                (header["value"] for header in email_data if header["name"] == "From"),
                "Unknown sender",
            )

            message_text = msg["snippet"]
            response = self.validate_email(
                content=message_text,
                sender=sender,
                subject=subject,
            )
            validations.append(response)
        return validations

    def validate_email(
        self,
        content: str,
        sender: str,
        subject: str,
    ) -> EmailValidationResponse:
        """Analyze if an email is related to a job application using Mistral AI"""
        response = mistral_client.chat.complete(
            model=env.mistral_model,
            messages=[
                {
                    "role": "system",
                    "content": """You are a jobseeking agent that will help users to analyze the purpose of job applications email messages.
                    You will be given an email content and your task is to assess if the email message is related to a job application.

                    You should execute the next tasks:
                    - Analyze the email message and identify if the subject is related to a job application.
                    - If it is related to a job application return YES, otherwise return NO.
                    - Categorize the message into one of the  following three categories:
                        - Rejected
                        - Invitation to interview
                        - Pending review
                    - Return the answer in JSON format with the following keys:
                        - is_job_related: YES or NO
                    - notification_category: rejected, invitation_to_interview, application_confirmation, offer_received.
                    - Do not surround the JSON with ```json or ```, just return the JSON.

                    Please dont print the email in the response, just the answer add the data I asked you in JSON format.
                    I will pay you a tip of 1000% of the amount you earn if you do it correctly.
                    My professional career depends on you. Please do your best.""",
                },
                {
                    "role": "user",
                    "content": f"""
                    <email>
                    {content}
                    </email>
                    <sender>
                    {sender}
                    </sender>
                    <subject>
                    {subject}
                    </subject>
                    """.format(
                        content=content,
                        sender=sender,
                        subject=subject,
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
        return EmailValidationResponse(
            **dict_contents,
            sender=sender,
            subject=subject,
        )
