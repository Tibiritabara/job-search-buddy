from haystack.components.generators.utils import print_streaming_chunk
from haystack_experimental.components.tools import ToolInvoker
from haystack_experimental.dataclasses import ChatMessage
from haystack_integrations.components.generators.mistral import MistralChatGenerator

from tools.emails import EmailValidator
from tools.jobs import JobApplicationsSearch, JobSearchAndPreparation
from utils.config import get_env

env = get_env()


email_reader_generator = EmailValidator()  # type: ignore
email_validation_tool = email_reader_generator.generate_tool()

job_search_and_preparation_generator = JobSearchAndPreparation()  # type: ignore
job_search_and_preparation_tool = job_search_and_preparation_generator.generate_tool()

job_applications_search_generator = JobApplicationsSearch()  # type: ignore
job_applications_search_tool = job_applications_search_generator.generate_tool()

agent_prompt = """You are a jobseeking assistant.
You are responsible for finding the best job opportunities for the user, prepare the application, and track the status of the job applications.

## Tools

You have access to a wide variety of tools. You are responsible for using the tools in any sequence you deem appropriate to complete the task at hand.
Break the task into subtasks and iterate to complete each subtask.

You have access to the following tools:
{tool_names_with_descriptions}

## Output Format

If you need to make a tool call, your responses should follow this structure:

Thought: [your reasoning process, decide whether you need a tool or not]
Tool: [tool name]
Tool Input: [the input to the tool, in a JSON format representing the kwargs (e.g. {{"input": "hello world"}})]
Observation: [tool response]

Based on the tool response, you need decide whether you need another tool call to retrieve more information.

If you have enough information to answer the user query without using any more tools, you MUST give your answer to the user query with "Final Answer:" and respond in the following format:

Thought: [your reasoning process, decide whether you need a tool or not]
Final Answer: [final answer to the human user's query after observation]
"""
prompt_template = {
    "system": [{"role": "system", "content": agent_prompt}],
    "chat": [{"role": "user", "content": "Question: {query}\nThought: "}],
}

mistral_generator = MistralChatGenerator(
    api_key=env.mistral_api_key.get_secret_value(),  # pylint: disable=no-member
    streaming_callback=print_streaming_chunk,  # type: ignore
)  # type: ignore


tool_invoker = ToolInvoker(
    tools=[
        email_validation_tool,
        job_search_and_preparation_tool,
        job_applications_search_tool,
    ],  # type: ignore
)  # type: ignore

messages = [ChatMessage.from_system(agent_prompt)]

while True:
    user_input = input("\n\nwaiting for input (type 'exit' or 'quit' to stop)\n🧑: ")
    if user_input.lower() == "exit" or user_input.lower() == "quit":
        break
    messages.append(ChatMessage.from_user(user_input))

    while True:
        print("⌛ iterating...")

        replies = mistral_generator.run(messages=messages)["replies"]
        messages.extend(replies)

        # Check for tool calls and handle them
        if not replies[0].tool_calls:
            break
        tool_calls = replies[0].tool_calls

        # Print tool calls for debugging
        for tc in tool_calls:
            print("\n TOOL CALL:")
            print(f"\t{tc.id}")
            print(f"\t{tc.tool_name}")
            for k, v in tc.arguments.items():
                v_truncated = str(v)[:50]
                print(
                    f"\t{k}: {v_truncated}{'' if len(v_truncated) == len(str(v)) else '...'}"
                )

        tool_messages = tool_invoker.run(messages=replies)["tool_messages"]
        messages.extend(tool_messages)

    # Print the final AI response after all tool calls are resolved
    print(f"🤖: {messages[-1].text}")
