Agents
Learn how to build agents with the OpenAI API.
Agents represent systems that intelligently accomplish tasks, ranging from executing simple workflows to pursuing complex, open-ended objectives.

OpenAI provides a rich set of composable primitives that enable you to build agents. This guide walks through those primitives, and how they come together to form a robust agentic platform.

Overview
Building agents involves assembling components across several domains—such as models, tools, knowledge and memory, audio and speech, guardrails, and orchestration—and OpenAI provides composable primitives for each.

Domain
Description OpenAI Primitives
Models Core intelligence capable of reasoning, making decisions, and processing different modalities. o1, o3-mini, GPT-4.5, GPT-4o, GPT-4o-mini
Tools Interface to the world, interact with environment, function calling, built-in tools, etc. Function calling, Web search, File search, Computer use
Knowledge and memory Augment agents with external and persistent knowledge. Vector stores, File search, Embeddings
Audio and speech Create agents that can understand audio and respond back in natural language. Audio generation, realtime, Audio agents
Guardrails Prevent irrelevant, harmful, or undesirable behavior. Moderation, Instruction hierarchy (Python), Instruction hierarchy (TypeScript)
Orchestration Develop, deploy, monitor, and improve agents. Python Agents SDK, TypeScript Agents SDK, Tracing, Evaluations, Fine-tuning
Voice agents Create agents that can understand audio and respond back in natural language. Realtime API, Voice support in the Python Agents SDK, Voice support in the TypeScript Agents SDK
Models
Model Agentic Strengths
o3 and o4-mini Best for long-term planning, hard tasks, and reasoning.
GPT-4.1 Best for agentic execution.
GPT-4.1-mini Good balance of agentic capability and latency.
GPT-4.1-nano Best for low-latency.
Large language models (LLMs) are at the core of many agentic systems, responsible for making decisions and interacting with the world. OpenAI’s models support a wide range of capabilities:

High intelligence: Capable of reasoning and planning to tackle the most difficult tasks.
Tools: Call your functions and leverage OpenAI's built-in tools.
Multimodality: Natively understand text, images, audio, code, and documents.
Low-latency: Support for real-time audio conversations and smaller, faster models.
For detailed model comparisons, visit the models page.

Tools
Tools enable agents to interact with the world. OpenAI supports
function calling
to connect with your code, and
built-in tools
for common tasks like web searches and data retrieval.

Tool Description
Function calling Interact with developer-defined code.
Web search Fetch up-to-date information from the web.
File search Perform semantic search across your documents.
Computer use Understand and control a computer or browser.
Local shell Execute commands on a local machine.
Knowledge and memory
Knowledge and memory help agents store, retrieve, and utilize information beyond their initial training data. Vector stores enable agents to search your documents semantically and retrieve relevant information at runtime. Meanwhile, embeddings represent data efficiently for quick retrieval, powering dynamic knowledge solutions and long-term agent memory. You can integrate your data using OpenAI’s vector stores and Embeddings API.

Guardrails
Guardrails ensure your agents behave safely, consistently, and within your intended boundaries—critical for production deployments. Use OpenAI’s free Moderation API to automatically filter unsafe content. Further control your agent’s behavior by leveraging the instruction hierarchy, which prioritizes developer-defined prompts and mitigates unwanted agent behaviors.

Orchestration
Building agents is a process. OpenAI provides tools to effectively build, deploy, monitor, evaluate, and improve agentic systems.

Agent Traces UI in OpenAI Dashboard
Phase
Description
OpenAI Primitives
Build and deploy Rapidly build agents, enforce guardrails, and handle conversational flows using the Agents SDK. Agents SDK Python, Agents SDK TypeScript
Monitor Observe agent behavior in real-time, debug issues, and gain insights through tracing. Tracing
Evaluate and improve Measure agent performance, identify areas for improvement, and refine your agents. Evaluations
Fine-tuning\

Assistants API overview
Beta
Build AI Assistants with essential tools and integrations.
Based on your feedback from the Assistants API beta, we've incorporated key improvements into the Responses API. After we achieve full feature parity, we will announce a deprecation plan later this year, with a target sunset date in the first half of 2026. Learn more.
Overview
The Assistants API allows you to build AI assistants within your own applications. An Assistant has instructions and can leverage models, tools, and files to respond to user queries.

The Assistants API currently supports three types of tools: Code Interpreter, File Search, and Function calling.

You can explore the capabilities of the Assistants API using the Assistants playground or by building a step-by-step integration outlined in our Assistants API quickstart.

How assistants work
The Assistants API is designed to help developers build powerful AI assistants capable of performing a variety of tasks.

Assistants can call OpenAI’s models with specific instructions to tune their personality and capabilities.
Assistants can access multiple tools in parallel. These can be both OpenAI built-in tools — like code_interpreter and file_search — or tools you build / host (via function calling).
Assistants can access persistent Threads. Threads simplify AI application development by storing message history and truncating it when the conversation gets too long for the model’s context length. You create a Thread once, and simply append Messages to it as your users reply.
Assistants can access files in several formats — either as part of their creation or as part of Threads between Assistants and users. When using tools, Assistants can also create files (e.g., images, spreadsheets, etc) and cite files they reference in the Messages they create.
Objects
Assistants object architecture diagram

Object What it represents
Assistant Purpose-built AI that uses OpenAI’s models and calls tools
Thread A conversation session between an Assistant and a user. Threads store Messages and automatically handle truncation to fit content into a model’s context.
Message A message created by an Assistant or a user. Messages can include text, images, and other files. Messages stored as a list on the Thread.
Run An invocation of an Assistant on a Thread. The Assistant uses its configuration and the Thread’s Messages to perform tasks by calling models and tools. As part of a Run, the Assistant appends Messages to the Thread.
Run Step A detailed list of steps the Assistant took as part of a Run. An Assistant can call tools or create Messages during its run. Examining Run Steps allows you to introspect how the Assistant is getting to its final results.

Step-by-step guide to creating an assistant.
Based on your feedback from the Assistants API beta, we've incorporated key improvements into the Responses API. After we achieve full feature parity, we will announce a deprecation plan later this year, with a target sunset date in the first half of 2026. Learn more.
Overview
A typical integration of the Assistants API has the following flow:

Create an Assistant by defining its custom instructions and picking a model. If helpful, add files and enable tools like Code Interpreter, File Search, and Function calling.
Create a Thread when a user starts a conversation.
Add Messages to the Thread as the user asks questions.
Run the Assistant on the Thread to generate a response by calling the model and the tools.
This starter guide walks through the key steps to create and run an Assistant that uses Code Interpreter. In this example, we're creating an Assistant that is a personal math tutor, with the Code Interpreter tool enabled.

Calls to the Assistants API require that you pass a beta HTTP header. This is handled automatically if you’re using OpenAI’s official Python or Node.js SDKs. OpenAI-Beta: assistants=v2

Step 1: Create an Assistant
An Assistant represents an entity that can be configured to respond to a user's messages using several parameters like model, instructions, and tools.

Create an Assistant
from openai import OpenAI
client = OpenAI()

assistant = client.beta.assistants.create(
name="Math Tutor",
instructions="You are a personal math tutor. Write and run code to answer math questions.",
tools=[{"type": "code_interpreter"}],
model="gpt-4o",
)
Step 2: Create a Thread
A Thread represents a conversation between a user and one or many Assistants. You can create a Thread when a user (or your AI application) starts a conversation with your Assistant.

Create a Thread
thread = client.beta.threads.create()
Step 3: Add a Message to the Thread
The contents of the messages your users or applications create are added as Message objects to the Thread. Messages can contain both text and files. There is a limit of 100,000 Messages per Thread and we smartly truncate any context that does not fit into the model's context window.

Add a Message to the Thread
message = client.beta.threads.messages.create(
thread_id=thread.id,
role="user",
content="I need to solve the equation `3x + 11 = 14`. Can you help me?"
)
Step 4: Create a Run
Once all the user Messages have been added to the Thread, you can Run the Thread with any Assistant. Creating a Run uses the model and tools associated with the Assistant to generate a response. These responses are added to the Thread as assistant Messages.

With streaming
Without streaming
You can use the 'create and stream' helpers in the Python and Node SDKs to create a run and stream the response.

Create and Stream a Run
from typing_extensions import override
from openai import AssistantEventHandler

# First, we create a EventHandler class to define

# how we want to handle the events in the response stream.

class EventHandler(AssistantEventHandler):  
 @override
def on_text_created(self, text) -> None:
print(f"\nassistant > ", end="", flush=True)

@override
def on_text_delta(self, delta, snapshot):
print(delta.value, end="", flush=True)

def on_tool_call_created(self, tool_call):
print(f"\nassistant > {tool_call.type}\n", flush=True)

def on_tool_call_delta(self, delta, snapshot):
if delta.type == 'code_interpreter':
if delta.code_interpreter.input:
print(delta.code_interpreter.input, end="", flush=True)
if delta.code_interpreter.outputs:
print(f"\n\noutput >", flush=True)
for output in delta.code_interpreter.outputs:
if output.type == "logs":
print(f"\n{output.logs}", flush=True)

# Then, we use the `stream` SDK helper

# with the `EventHandler` class to create the Run

# and stream the response.

with client.beta.threads.runs.stream(
thread_id=thread.id,
assistant_id=assistant.id,
instructions="Please address the user as Jane Doe. The user has a premium account.",
event_handler=EventHandler(),
) as stream:
stream.until_done()
See the full list of Assistants streaming events in our API reference here. You can also see a list of SDK event listeners for these events in the Python & Node repository documentation.

Next steps
Continue learning about Assistants Concepts in the Deep Dive
Learn more about Tools
Explore the Assistants playground
Check out our Assistants Quickstart app on github

Assistants API deep dive
Beta
In-depth guide to creating and managing assistants.
Based on your feedback from the Assistants API beta, we've incorporated key improvements into the Responses API. After we achieve full feature parity, we will announce a deprecation plan later this year, with a target sunset date in the first half of 2026. Learn more.
Overview
As described in the Assistants Overview, there are several concepts involved in building an app with the Assistants API.

This guide goes deeper into each of these concepts.

If you want to get started coding right away, check out the Assistants API Quickstart.

Creating Assistants
We recommend using OpenAI's latest models with the Assistants API for best results and maximum compatibility with tools.

To get started, creating an Assistant only requires specifying the model to use. But you can further customize the behavior of the Assistant:

Use the instructions parameter to guide the personality of the Assistant and define its goals. Instructions are similar to system messages in the Chat Completions API.
Use the tools parameter to give the Assistant access to up to 128 tools. You can give it access to OpenAI built-in tools like code_interpreter and file_search, or call a third-party tools via a function calling.
Use the tool_resources parameter to give the tools like code_interpreter and file_search access to files. Files are uploaded using the File upload endpoint and must have the purpose set to assistants to be used with this API.
For example, to create an Assistant that can create data visualization based on a .csv file, first upload a file.

file = client.files.create(
file=open("revenue-forecast.csv", "rb"),
purpose='assistants'
)
Then, create the Assistant with the code_interpreter tool enabled and provide the file as a resource to the tool.

assistant = client.beta.assistants.create(
name="Data visualizer",
description="You are great at creating beautiful data visualizations. You analyze data present in .csv files, understand trends, and come up with data visualizations relevant to those trends. You also share a brief text summary of the trends observed.",
model="gpt-4o",
tools=[{"type": "code_interpreter"}],
tool_resources={
"code_interpreter": {
"file_ids": [file.id]
}
}
)
You can attach a maximum of 20 files to code_interpreter and 10,000 files to file_search (using vector_store objects).

Each file can be at most 512 MB in size and have a maximum of 5,000,000 tokens. By default, the size of all the files uploaded in your project cannot exceed 100 GB, but you can reach out to our support team to increase this limit.

Managing Threads and Messages
Threads and Messages represent a conversation session between an Assistant and a user. There is a limit of 100,000 Messages per Thread. Once the size of the Messages exceeds the context window of the model, the Thread will attempt to smartly truncate messages, before fully dropping the ones it considers the least important.

You can create a Thread with an initial list of Messages like this:

thread = client.beta.threads.create(
messages=[
{
"role": "user",
"content": "Create 3 data visualizations based on the trends in this file.",
"attachments": [
{
"file_id": file.id,
"tools": [{"type": "code_interpreter"}]
}
]
}
]
)
Messages can contain text, images, or file attachment. Message attachments are helper methods that add files to a thread's tool_resources. You can also choose to add files to the thread.tool_resources directly.

Creating image input content
Message content can contain either external image URLs or File IDs uploaded via the File API. Only models with Vision support can accept image input. Supported image content types include png, jpg, gif, and webp. When creating image files, pass purpose="vision" to allow you to later download and display the input content. Currently, there is a 100GB limit per project. Please contact us to request a limit increase.

Tools cannot access image content unless specified. To pass image files to Code Interpreter, add the file ID in the message attachments list to allow the tool to read and analyze the input. Image URLs cannot be downloaded in Code Interpreter today.

file = client.files.create(
file=open("myimage.png", "rb"),
purpose="vision"
)
thread = client.beta.threads.create(
messages=[
{
"role": "user",
"content": [
{
"type": "text",
"text": "What is the difference between these images?"
},
{
"type": "image_url",
"image_url": {"url": "https://example.com/image.png"}
},
{
"type": "image_file",
"image_file": {"file_id": file.id}
},
],
}
]
)
Low or high fidelity image understanding
By controlling the detail parameter, which has three options, low, high, or auto, you have control over how the model processes the image and generates its textual understanding.

low will enable the "low res" mode. The model will receive a low-res 512px x 512px version of the image, and represent the image with a budget of 85 tokens. This allows the API to return faster responses and consume fewer input tokens for use cases that do not require high detail.
high will enable "high res" mode, which first allows the model to see the low res image and then creates detailed crops of input images based on the input image size. Use the pricing calculator to see token counts for various image sizes.
thread = client.beta.threads.create(
messages=[
{
"role": "user",
"content": [
{
"type": "text",
"text": "What is this an image of?"
},
{
"type": "image_url",
"image_url": {
"url": "https://example.com/image.png",
"detail": "high"
}
},
],
}
]
)
Context window management
The Assistants API automatically manages the truncation to ensure it stays within the model's maximum context length. You can customize this behavior by specifying the maximum tokens you'd like a run to utilize and/or the maximum number of recent messages you'd like to include in a run.

Max Completion and Max Prompt Tokens
To control the token usage in a single Run, set max_prompt_tokens and max_completion_tokens when creating the Run. These limits apply to the total number of tokens used in all completions throughout the Run's lifecycle.

For example, initiating a Run with max_prompt_tokens set to 500 and max_completion_tokens set to 1000 means the first completion will truncate the thread to 500 tokens and cap the output at 1000 tokens. If only 200 prompt tokens and 300 completion tokens are used in the first completion, the second completion will have available limits of 300 prompt tokens and 700 completion tokens.

If a completion reaches the max_completion_tokens limit, the Run will terminate with a status of incomplete, and details will be provided in the incomplete_details field of the Run object.

When using the File Search tool, we recommend setting the max_prompt_tokens to no less than 20,000. For longer conversations or multiple interactions with File Search, consider increasing this limit to 50,000, or ideally, removing the max_prompt_tokens limits altogether to get the highest quality results.

Truncation Strategy
You may also specify a truncation strategy to control how your thread should be rendered into the model's context window. Using a truncation strategy of type auto will use OpenAI's default truncation strategy. Using a truncation strategy of type last_messages will allow you to specify the number of the most recent messages to include in the context window.

Message annotations
Messages created by Assistants may contain
annotations
within the content array of the object. Annotations provide information around how you should annotate the text in the Message.

There are two types of Annotations:

file_citation: File citations are created by the
file_search
tool and define references to a specific file that was uploaded and used by the Assistant to generate the response.
file_path: File path annotations are created by the
code_interpreter
tool and contain references to the files generated by the tool.
When annotations are present in the Message object, you'll see illegible model-generated substrings in the text that you should replace with the annotations. These strings may look something like 【13†source】 or sandbox:/mnt/data/file.csv. Here’s an example python code snippet that replaces these strings with the annotations.

# Retrieve the message object

message = client.beta.threads.messages.retrieve(
thread_id="...",
message_id="..."
)

# Extract the message content

message_content = message.content[0].text
annotations = message_content.annotations
citations = []

# Iterate over the annotations and add footnotes

for index, annotation in enumerate(annotations): # Replace the text with a footnote
message_content.value = message_content.value.replace(annotation.text, f' [{index}]')

    # Gather citations based on annotation attributes
    if (file_citation := getattr(annotation, 'file_citation', None)):
        cited_file = client.files.retrieve(file_citation.file_id)
        citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
    elif (file_path := getattr(annotation, 'file_path', None)):
        cited_file = client.files.retrieve(file_path.file_id)
        citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
        # Note: File download functionality not implemented above for brevity

# Add footnotes to the end of the message before displaying to user

message_content.value += '\n' + '\n'.join(citations)
Runs and Run Steps
When you have all the context you need from your user in the Thread, you can run the Thread with an Assistant of your choice.

run = client.beta.threads.runs.create(
thread_id=thread.id,
assistant_id=assistant.id
)
By default, a Run will use the model and tools configuration specified in Assistant object, but you can override most of these when creating the Run for added flexibility:

run = client.beta.threads.runs.create(
thread_id=thread.id,
assistant_id=assistant.id,
model="gpt-4o",
instructions="New instructions that override the Assistant instructions",
tools=[{"type": "code_interpreter"}, {"type": "file_search"}]
)
Note: tool_resources associated with the Assistant cannot be overridden during Run creation. You must use the modify Assistant endpoint to do this.

Run lifecycle
Run objects can have multiple statuses.

Run lifecycle - diagram showing possible status transitions

Status Definition
queued When Runs are first created or when you complete the required_action, they are moved to a queued status. They should almost immediately move to in_progress.
in_progress While in_progress, the Assistant uses the model and tools to perform steps. You can view progress being made by the Run by examining the Run Steps.
completed The Run successfully completed! You can now view all Messages the Assistant added to the Thread, and all the steps the Run took. You can also continue the conversation by adding more user Messages to the Thread and creating another Run.
requires_action When using the Function calling tool, the Run will move to a required_action state once the model determines the names and arguments of the functions to be called. You must then run those functions and submit the outputs before the run proceeds. If the outputs are not provided before the expires_at timestamp passes (roughly 10 mins past creation), the run will move to an expired status.
expired This happens when the function calling outputs were not submitted before expires_at and the run expires. Additionally, if the runs take too long to execute and go beyond the time stated in expires_at, our systems will expire the run.
cancelling You can attempt to cancel an in_progress run using the Cancel Run endpoint. Once the attempt to cancel succeeds, status of the Run moves to cancelled. Cancellation is attempted but not guaranteed.
cancelled Run was successfully cancelled.
failed You can view the reason for the failure by looking at the last_error object in the Run. The timestamp for the failure will be recorded under failed_at.
incomplete Run ended due to max_prompt_tokens or max_completion_tokens reached. You can view the specific reason by looking at the incomplete_details object in the Run.
Polling for updates
If you are not using streaming, in order to keep the status of your run up to date, you will have to periodically retrieve the Run object. You can check the status of the run each time you retrieve the object to determine what your application should do next.

You can optionally use Polling Helpers in our Node and Python SDKs to help you with this. These helpers will automatically poll the Run object for you and return the Run object when it's in a terminal state.

Thread locks
When a Run is in_progress and not in a terminal state, the Thread is locked. This means that:

New Messages cannot be added to the Thread.
New Runs cannot be created on the Thread.
Run steps
Run steps lifecycle - diagram showing possible status transitions

Run step statuses have the same meaning as Run statuses.

Most of the interesting detail in the Run Step object lives in the step_details field. There can be two types of step details:

message_creation: This Run Step is created when the Assistant creates a Message on the Thread.
tool_calls: This Run Step is created when the Assistant calls a tool. Details around this are covered in the relevant sections of the Tools guide.
Data Access Guidance
Currently, Assistants, Threads, Messages, and Vector Stores created via the API are scoped to the Project they're created in. As such, any person with API key access to that Project is able to read or write Assistants, Threads, Messages, and Runs in the Project.

We strongly recommend the following data access controls:

Implement authorization. Before performing reads or writes on Assistants, Threads, Messages, and Vector Stores, ensure that the end-user is authorized to do so. For example, store in your database the object IDs that the end-user has access to, and check it before fetching the object ID with the API.
Restrict API key access. Carefully consider who in your organization should have API keys and be part of a Project. Periodically audit this list. API keys enable a wide range of operations including reading and modifying sensitive information, such as Messages and Files.
Create separate accounts. Consider creating separate Projects for different applications in order to isolate data across multiple applications.

Assistants Function Calling
Beta
Based on your feedback from the Assistants API beta, we've incorporated key improvements into the Responses API. After we achieve full feature parity, we will announce a deprecation plan later this year, with a target sunset date in the first half of 2026. Learn more.
Overview
Similar to the Chat Completions API, the Assistants API supports function calling. Function calling allows you to describe functions to the Assistants API and have it intelligently return the functions that need to be called along with their arguments.

Quickstart
In this example, we'll create a weather assistant and define two functions, get_current_temperature and get_rain_probability, as tools that the Assistant can call. Depending on the user query, the model will invoke parallel function calling if using our latest models released on or after Nov 6, 2023. In our example that uses parallel function calling, we will ask the Assistant what the weather in San Francisco is like today and the chances of rain. We also show how to output the Assistant's response with streaming.

With the launch of Structured Outputs, you can now use the parameter strict: true when using function calling with the Assistants API. For more information, refer to the Function calling guide. Please note that Structured Outputs are not supported in the Assistants API when using vision.

Step 1: Define functions
When creating your assistant, you will first define the functions under the tools param of the assistant.

from openai import OpenAI
client = OpenAI()

assistant = client.beta.assistants.create(
instructions="You are a weather bot. Use the provided functions to answer questions.",
model="gpt-4o",
tools=[
{
"type": "function",
"function": {
"name": "get_current_temperature",
"description": "Get the current temperature for a specific location",
"parameters": {
"type": "object",
"properties": {
"location": {
"type": "string",
"description": "The city and state, e.g., San Francisco, CA"
},
"unit": {
"type": "string",
"enum": ["Celsius", "Fahrenheit"],
"description": "The temperature unit to use. Infer this from the user's location."
}
},
"required": ["location", "unit"]
}
}
},
{
"type": "function",
"function": {
"name": "get_rain_probability",
"description": "Get the probability of rain for a specific location",
"parameters": {
"type": "object",
"properties": {
"location": {
"type": "string",
"description": "The city and state, e.g., San Francisco, CA"
}
},
"required": ["location"]
}
}
}
]
)
Step 2: Create a Thread and add Messages
Create a Thread when a user starts a conversation and add Messages to the Thread as the user asks questions.

thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
thread_id=thread.id,
role="user",
content="What's the weather in San Francisco today and the likelihood it'll rain?",
)
Step 3: Initiate a Run
When you initiate a Run on a Thread containing a user Message that triggers one or more functions, the Run will enter a pending status. After it processes, the run will enter a requires_action state which you can verify by checking the Run’s status. This indicates that you need to run tools and submit their outputs to the Assistant to continue Run execution. In our case, we will see two tool_calls, which indicates that the user query resulted in parallel function calling.

Note that a runs expire ten minutes after creation. Be sure to submit your tool outputs before the 10 min mark.

You will see two tool_calls within required_action, which indicates the user query triggered parallel function calling.

{
"id": "run_qJL1kI9xxWlfE0z1yfL0fGg9",
...
"status": "requires_action",
"required_action": {
"submit_tool_outputs": {
"tool_calls": [
{
"id": "call_FthC9qRpsL5kBpwwyw6c7j4k",
"function": {
"arguments": "{"location": "San Francisco, CA"}",
"name": "get_rain_probability"
},
"type": "function"
},
{
"id": "call_RpEDoB8O0FTL9JoKTuCVFOyR",
"function": {
"arguments": "{"location": "San Francisco, CA", "unit": "Fahrenheit"}",
"name": "get_current_temperature"
},
"type": "function"
}
]
},
...
"type": "submit_tool_outputs"
}
}
Run object truncated here for readability

How you initiate a Run and submit tool_calls will differ depending on whether you are using streaming or not, although in both cases all tool_calls need to be submitted at the same time. You can then complete the Run by submitting the tool outputs from the functions you called. Pass each tool_call_id referenced in the required_action object to match outputs to each function call.

With streaming
Without streaming
For the streaming case, we create an EventHandler class to handle events in the response stream and submit all tool outputs at once with the “submit tool outputs stream” helper in the Python and Node SDKs.

from typing_extensions import override
from openai import AssistantEventHandler

class EventHandler(AssistantEventHandler):
@override
def on_event(self, event): # Retrieve events that are denoted with 'requires_action' # since these will have our tool_calls
if event.event == 'thread.run.requires_action':
run_id = event.data.id # Retrieve the run ID from the event data
self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
      tool_outputs = []

      for tool in data.required_action.submit_tool_outputs.tool_calls:
        if tool.function.name == "get_current_temperature":
          tool_outputs.append({"tool_call_id": tool.id, "output": "57"})
        elif tool.function.name == "get_rain_probability":
          tool_outputs.append({"tool_call_id": tool.id, "output": "0.06"})

      # Submit all tool_outputs at the same time
      self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
      # Use the submit_tool_outputs_stream helper
      with client.beta.threads.runs.submit_tool_outputs_stream(
        thread_id=self.current_run.thread_id,
        run_id=self.current_run.id,
        tool_outputs=tool_outputs,
        event_handler=EventHandler(),
      ) as stream:
        for text in stream.text_deltas:
          print(text, end="", flush=True)
        print()

with client.beta.threads.runs.stream(
thread_id=thread.id,
assistant_id=assistant.id,
event_handler=EventHandler()
) as stream:
stream.until_done()
Using Structured Outputs
When you enable Structured Outputs by supplying strict: true, the OpenAI API will pre-process your supplied schema on your first request, and then use this artifact to constrain the model to your schema.

from openai import OpenAI
client = OpenAI()

assistant = client.beta.assistants.create(
instructions="You are a weather bot. Use the provided functions to answer questions.",
model="gpt-4o-2024-08-06",
tools=[
{
"type": "function",
"function": {
"name": "get_current_temperature",
"description": "Get the current temperature for a specific location",
"parameters": {
"type": "object",
"properties": {
"location": {
"type": "string",
"description": "The city and state, e.g., San Francisco, CA"
},
"unit": {
"type": "string",
"enum": ["Celsius", "Fahrenheit"],
"description": "The temperature unit to use. Infer this from the user's location."
}
},
"required": ["location", "unit"],
"additionalProperties": False
},
"strict": True
}
},
{
"type": "function",
"function": {
"name": "get_rain_probability",
"description": "Get the probability of rain for a specific location",
"parameters": {
"type": "object",
"properties": {
"location": {
"type": "string",
"description": "The city and state, e.g., San Francisco, CA"
}
},
"required": ["location"],
"additionalProperties": False
},
"strict": True
}
}
]
)

What's new in Assistants API
Beta
Discover new features and improvements in Assistants API.
March 2025
Based on developer feedback from the Assistants API beta, we've incorporated key improvements into the Responses API, making it more flexible, faster, and easier to use.

We launched the Responses API, a new API primitive with built-in tools, like function calling, file search, web search, and computer use.
We're working to achieve full feature parity between the Assistants and the Responses API, including support for Assistant-like and Thread-like objects and the Code Interpreter tool. We will communicate updates to the Assistants API in the changelog.
After achieving full feature parity, we plan to formally announce the deprecation of the Assistants API with a target sunset date in the first half of 2026. Upon deprecation, we will provide a clear migration guide from the Assistants API to the Responses API that allows developers to preserve all their data and migrate their applications.
Until we formally announce the deprecation, we will continue delivering new models to the Assistants API. The Responses API represents the future direction for building agents on OpenAI.
April 2024
We are announcing a variety of new features and improvements to the Assistants API and moving our Beta to a new API version, OpenAI-Beta: assistants=v2. Here's what's new:

We're launching an improved retrieval tool called
file_search
, which can ingest up to 10,000 files per assistant - 500x more than before. It is faster, supports parallel queries through multi-threaded searches, and features enhanced reranking and query rewriting.
Alongside file_search, we're introducing
vector_store
objects in the API. Once a file is added to a vector store, it's automatically parsed, chunked, and embedded, made ready to be searched. Vector stores can be used across assistants and threads, simplifying file management and billing.
You can now control the maximum number of tokens a run uses in the Assistants API, allowing you to manage token usage costs. You can also set limits on the number of previous / recent messages used in each run.
We've added support for the
tool_choice
parameter which can be used to force the use of a specific tool (like file_search, code_interpreter, or a function) in a particular run.
You can now create messages with the role
assistant
to create custom conversation histories in Threads.
Assistant and Run objects now support popular model configuration parameters like
temperature
,
response_format
(JSON mode), and
top_p
.
You can now use fine-tuned models in the Assistants API. At the moment, only fine-tuned versions of gpt-3.5-turbo-0125 are supported.
Assistants API now supports streaming.
We've added several streaming and polling helpers to our Node and Python SDKs.
See our migration guide to learn more about how to migrate your tool usage to the latest version of the Assistants API.

Create assistant
Beta
post

https://api.openai.com/v1/assistants
Create an assistant with a model and instructions.

Request body
model
string

Required
ID of the model to use. You can use the List models API to see all of your available models, or see our Model overview for descriptions of them.

description
string or null

Optional
The description of the assistant. The maximum length is 512 characters.

instructions
string or null

Optional
The system instructions that the assistant uses. The maximum length is 256,000 characters.

metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

name
string or null

Optional
The name of the assistant. The maximum length is 256 characters.

reasoning_effort
string or null

Optional
Defaults to medium
o-series models only

Constrains effort on reasoning for reasoning models. Currently supported values are low, medium, and high. Reducing reasoning effort can result in faster responses and fewer tokens used on reasoning in a response.

response_format
"auto" or object

Optional
Specifies the format that the model must output. Compatible with GPT-4o, GPT-4 Turbo, and all GPT-3.5 Turbo models since gpt-3.5-turbo-1106.

Setting to { "type": "json_schema", "json_schema": {...} } enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the Structured Outputs guide.

Setting to { "type": "json_object" } enables JSON mode, which ensures the message the model generates is valid JSON.

Important: when using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if finish_reason="length", which indicates the generation exceeded max_tokens or the conversation exceeded the max context length.

Show possible types
temperature
number or null

Optional
Defaults to 1
What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

tool_resources
object or null

Optional
A set of resources that are used by the assistant's tools. The resources are specific to the type of tool. For example, the code_interpreter tool requires a list of file IDs, while the file_search tool requires a list of vector store IDs.

Show properties
tools
array

Optional
Defaults to []
A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types code_interpreter, file_search, or function.

Show possible types
top_p
number or null

Optional
Defaults to 1
An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

Returns
An assistant object.

Code Interpreter
Files
Example request
curl "https://api.openai.com/v1/assistants" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2" \
 -d '{
"instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
"name": "Math Tutor",
"tools": [{"type": "code_interpreter"}],
"model": "gpt-4o"
}'
Response
{
"id": "asst_abc123",
"object": "assistant",
"created_at": 1698984975,
"name": "Math Tutor",
"description": null,
"model": "gpt-4o",
"instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
"tools": [
{
"type": "code_interpreter"
}
],
"metadata": {},
"top_p": 1.0,
"temperature": 1.0,
"response_format": "auto"
}
List assistants
Beta
get

https://api.openai.com/v1/assistants
Returns a list of assistants.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

before
string

Optional
A cursor for use in pagination. before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order
string

Optional
Defaults to desc
Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.

Returns
A list of assistant objects.

Example request
curl "https://api.openai.com/v1/assistants?order=desc&limit=20" \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"object": "list",
"data": [
{
"id": "asst_abc123",
"object": "assistant",
"created_at": 1698982736,
"name": "Coding Tutor",
"description": null,
"model": "gpt-4o",
"instructions": "You are a helpful assistant designed to make me better at coding!",
"tools": [],
"tool_resources": {},
"metadata": {},
"top_p": 1.0,
"temperature": 1.0,
"response_format": "auto"
},
{
"id": "asst_abc456",
"object": "assistant",
"created_at": 1698982718,
"name": "My Assistant",
"description": null,
"model": "gpt-4o",
"instructions": "You are a helpful assistant designed to make me better at coding!",
"tools": [],
"tool_resources": {},
"metadata": {},
"top_p": 1.0,
"temperature": 1.0,
"response_format": "auto"
},
{
"id": "asst_abc789",
"object": "assistant",
"created_at": 1698982643,
"name": null,
"description": null,
"model": "gpt-4o",
"instructions": null,
"tools": [],
"tool_resources": {},
"metadata": {},
"top_p": 1.0,
"temperature": 1.0,
"response_format": "auto"
}
],
"first_id": "asst_abc123",
"last_id": "asst_abc789",
"has_more": false
}
Retrieve assistant
Beta
get

https://api.openai.com/v1/assistants/{assistant_id}
Retrieves an assistant.

Path parameters
assistant_id
string

Required
The ID of the assistant to retrieve.

Returns
The assistant object matching the specified ID.

Example request
curl https://api.openai.com/v1/assistants/asst_abc123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"id": "asst_abc123",
"object": "assistant",
"created_at": 1699009709,
"name": "HR Helper",
"description": null,
"model": "gpt-4o",
"instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies.",
"tools": [
{
"type": "file_search"
}
],
"metadata": {},
"top_p": 1.0,
"temperature": 1.0,
"response_format": "auto"
}
Modify assistant
Beta
post

https://api.openai.com/v1/assistants/{assistant_id}
Modifies an assistant.

Path parameters
assistant_id
string

Required
The ID of the assistant to modify.

Request body
description
string or null

Optional
The description of the assistant. The maximum length is 512 characters.

instructions
string or null

Optional
The system instructions that the assistant uses. The maximum length is 256,000 characters.

metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

model
string

Optional
ID of the model to use. You can use the List models API to see all of your available models, or see our Model overview for descriptions of them.

name
string or null

Optional
The name of the assistant. The maximum length is 256 characters.

reasoning_effort
string or null

Optional
Defaults to medium
o-series models only

Constrains effort on reasoning for reasoning models. Currently supported values are low, medium, and high. Reducing reasoning effort can result in faster responses and fewer tokens used on reasoning in a response.

response_format
"auto" or object

Optional
Specifies the format that the model must output. Compatible with GPT-4o, GPT-4 Turbo, and all GPT-3.5 Turbo models since gpt-3.5-turbo-1106.

Setting to { "type": "json_schema", "json_schema": {...} } enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the Structured Outputs guide.

Setting to { "type": "json_object" } enables JSON mode, which ensures the message the model generates is valid JSON.

Important: when using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if finish_reason="length", which indicates the generation exceeded max_tokens or the conversation exceeded the max context length.

Show possible types
temperature
number or null

Optional
Defaults to 1
What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

tool_resources
object or null

Optional
A set of resources that are used by the assistant's tools. The resources are specific to the type of tool. For example, the code_interpreter tool requires a list of file IDs, while the file_search tool requires a list of vector store IDs.

Show properties
tools
array

Optional
Defaults to []
A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types code_interpreter, file_search, or function.

Show possible types
top_p
number or null

Optional
Defaults to 1
An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

Returns
The modified assistant object.

Example request
curl https://api.openai.com/v1/assistants/asst_abc123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2" \
 -d '{
"instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
"tools": [{"type": "file_search"}],
"model": "gpt-4o"
}'
Response
{
"id": "asst_123",
"object": "assistant",
"created_at": 1699009709,
"name": "HR Helper",
"description": null,
"model": "gpt-4o",
"instructions": "You are an HR bot, and you have access to files to answer employee questions about company policies. Always response with info from either of the files.",
"tools": [
{
"type": "file_search"
}
],
"tool_resources": {
"file_search": {
"vector_store_ids": []
}
},
"metadata": {},
"top_p": 1.0,
"temperature": 1.0,
"response_format": "auto"
}
Delete assistant
Beta
delete

https://api.openai.com/v1/assistants/{assistant_id}
Delete an assistant.

Path parameters
assistant_id
string

Required
The ID of the assistant to delete.

Returns
Deletion status

Example request
curl https://api.openai.com/v1/assistants/asst_abc123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2" \
 -X DELETE
Response
{
"id": "asst_abc123",
"object": "assistant.deleted",
"deleted": true
}
The assistant object
Beta
Represents an assistant that can call the model and use tools.

created_at
integer

The Unix timestamp (in seconds) for when the assistant was created.

description
string or null

The description of the assistant. The maximum length is 512 characters.

id
string

The identifier, which can be referenced in API endpoints.

instructions
string or null

The system instructions that the assistant uses. The maximum length is 256,000 characters.

metadata
map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

model
string

ID of the model to use. You can use the List models API to see all of your available models, or see our Model overview for descriptions of them.

name
string or null

The name of the assistant. The maximum length is 256 characters.

object
string

The object type, which is always assistant.

response_format
"auto" or object

Specifies the format that the model must output. Compatible with GPT-4o, GPT-4 Turbo, and all GPT-3.5 Turbo models since gpt-3.5-turbo-1106.

Setting to { "type": "json_schema", "json_schema": {...} } enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the Structured Outputs guide.

Setting to { "type": "json_object" } enables JSON mode, which ensures the message the model generates is valid JSON.

Important: when using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if finish_reason="length", which indicates the generation exceeded max_tokens or the conversation exceeded the max context length.

Show possible types
temperature
number or null

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

tool_resources
object or null

A set of resources that are used by the assistant's tools. The resources are specific to the type of tool. For example, the code_interpreter tool requires a list of file IDs, while the file_search tool requires a list of vector store IDs.

Show properties
tools
array

A list of tool enabled on the assistant. There can be a maximum of 128 tools per assistant. Tools can be of types code_interpreter, file_search, or function.

Show possible types
top_p
number or null

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

OBJECT The assistant object
{
"id": "asst_abc123",
"object": "assistant",
"created_at": 1698984975,
"name": "Math Tutor",
"description": null,
"model": "gpt-4o",
"instructions": "You are a personal math tutor. When asked a question, write and run Python code to answer the question.",
"tools": [
{
"type": "code_interpreter"
}
],
"metadata": {},
"top_p": 1.0,
"temperature": 1.0,
"response_format": "auto"
}
Threads
Beta
Create threads that assistants can interact with.

Related guide: Assistants

Create thread
Beta
post

https://api.openai.com/v1/threads
Create a thread.

Request body
messages
array

Optional
A list of messages to start the thread with.

Show properties
metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

tool_resources
object or null

Optional
A set of resources that are made available to the assistant's tools in this thread. The resources are specific to the type of tool. For example, the code_interpreter tool requires a list of file IDs, while the file_search tool requires a list of vector store IDs.

Show properties
Returns
A thread object.

Empty
Messages
Example request
curl https://api.openai.com/v1/threads \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2" \
 -d ''
Response
{
"id": "thread_abc123",
"object": "thread",
"created_at": 1699012949,
"metadata": {},
"tool_resources": {}
}
Retrieve thread
Beta
get

https://api.openai.com/v1/threads/{thread_id}
Retrieves a thread.

Path parameters
thread_id
string

Required
The ID of the thread to retrieve.

Returns
The thread object matching the specified ID.

Example request
curl https://api.openai.com/v1/threads/thread_abc123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"id": "thread_abc123",
"object": "thread",
"created_at": 1699014083,
"metadata": {},
"tool_resources": {
"code_interpreter": {
"file_ids": []
}
}
}
Modify thread
Beta
post

https://api.openai.com/v1/threads/{thread_id}
Modifies a thread.

Path parameters
thread_id
string

Required
The ID of the thread to modify. Only the metadata can be modified.

Request body
metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

tool_resources
object or null

Optional
A set of resources that are made available to the assistant's tools in this thread. The resources are specific to the type of tool. For example, the code_interpreter tool requires a list of file IDs, while the file_search tool requires a list of vector store IDs.

Show properties
Returns
The modified thread object matching the specified ID.

Example request
curl https://api.openai.com/v1/threads/thread_abc123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2" \
 -d '{
"metadata": {
"modified": "true",
"user": "abc123"
}
}'
Response
{
"id": "thread_abc123",
"object": "thread",
"created_at": 1699014083,
"metadata": {
"modified": "true",
"user": "abc123"
},
"tool_resources": {}
}
Delete thread
Beta
delete

https://api.openai.com/v1/threads/{thread_id}
Delete a thread.

Path parameters
thread_id
string

Required
The ID of the thread to delete.

Returns
Deletion status

Example request
curl https://api.openai.com/v1/threads/thread_abc123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2" \
 -X DELETE
Response
{
"id": "thread_abc123",
"object": "thread.deleted",
"deleted": true
}
The thread object
Beta
Represents a thread that contains messages.

created_at
integer

The Unix timestamp (in seconds) for when the thread was created.

id
string

The identifier, which can be referenced in API endpoints.

metadata
map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

object
string

The object type, which is always thread.

tool_resources
object or null

A set of resources that are made available to the assistant's tools in this thread. The resources are specific to the type of tool. For example, the code_interpreter tool requires a list of file IDs, while the file_search tool requires a list of vector store IDs.

Show properties
OBJECT The thread object
{
"id": "thread_abc123",
"object": "thread",
"created_at": 1698107661,
"metadata": {}
}
Messages
Beta
Create messages within threads

Related guide: Assistants

Create message
Beta
post

https://api.openai.com/v1/threads/{thread_id}/messages
Create a message.

Path parameters
thread_id
string

Required
The ID of the thread to create a message for.

Request body
content
string or array

Required

Show possible types
role
string

Required
The role of the entity that is creating the message. Allowed values include:

user: Indicates the message is sent by an actual user and should be used in most cases to represent user-generated messages.
assistant: Indicates the message is generated by the assistant. Use this value to insert messages from the assistant into the conversation.
attachments
array or null

Optional
A list of files attached to the message, and the tools they should be added to.

Show properties
metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

Returns
A message object.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/messages \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2" \
 -d '{
"role": "user",
"content": "How does AI work? Explain it in simple terms."
}'
Response
{
"id": "msg_abc123",
"object": "thread.message",
"created_at": 1713226573,
"assistant_id": null,
"thread_id": "thread_abc123",
"run_id": null,
"role": "user",
"content": [
{
"type": "text",
"text": {
"value": "How does AI work? Explain it in simple terms.",
"annotations": []
}
}
],
"attachments": [],
"metadata": {}
}
List messages
Beta
get

https://api.openai.com/v1/threads/{thread_id}/messages
Returns a list of messages for a given thread.

Path parameters
thread_id
string

Required
The ID of the thread the messages belong to.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

before
string

Optional
A cursor for use in pagination. before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order
string

Optional
Defaults to desc
Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.

run_id
string

Optional
Filter messages by the run ID that generated them.

Returns
A list of message objects.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/messages \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"object": "list",
"data": [
{
"id": "msg_abc123",
"object": "thread.message",
"created_at": 1699016383,
"assistant_id": null,
"thread_id": "thread_abc123",
"run_id": null,
"role": "user",
"content": [
{
"type": "text",
"text": {
"value": "How does AI work? Explain it in simple terms.",
"annotations": []
}
}
],
"attachments": [],
"metadata": {}
},
{
"id": "msg_abc456",
"object": "thread.message",
"created_at": 1699016383,
"assistant_id": null,
"thread_id": "thread_abc123",
"run_id": null,
"role": "user",
"content": [
{
"type": "text",
"text": {
"value": "Hello, what is AI?",
"annotations": []
}
}
],
"attachments": [],
"metadata": {}
}
],
"first_id": "msg_abc123",
"last_id": "msg_abc456",
"has_more": false
}
Retrieve message
Beta
get

https://api.openai.com/v1/threads/{thread_id}/messages/{message_id}
Retrieve a message.

Path parameters
message_id
string

Required
The ID of the message to retrieve.

thread_id
string

Required
The ID of the thread to which this message belongs.

Returns
The message object matching the specified ID.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"id": "msg_abc123",
"object": "thread.message",
"created_at": 1699017614,
"assistant_id": null,
"thread_id": "thread_abc123",
"run_id": null,
"role": "user",
"content": [
{
"type": "text",
"text": {
"value": "How does AI work? Explain it in simple terms.",
"annotations": []
}
}
],
"attachments": [],
"metadata": {}
}
Modify message
Beta
post

https://api.openai.com/v1/threads/{thread_id}/messages/{message_id}
Modifies a message.

Path parameters
message_id
string

Required
The ID of the message to modify.

thread_id
string

Required
The ID of the thread to which this message belongs.

Request body
metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

Returns
The modified message object.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2" \
 -d '{
"metadata": {
"modified": "true",
"user": "abc123"
}
}'
Response
{
"id": "msg_abc123",
"object": "thread.message",
"created_at": 1699017614,
"assistant_id": null,
"thread_id": "thread_abc123",
"run_id": null,
"role": "user",
"content": [
{
"type": "text",
"text": {
"value": "How does AI work? Explain it in simple terms.",
"annotations": []
}
}
],
"file_ids": [],
"metadata": {
"modified": "true",
"user": "abc123"
}
}
Delete message
Beta
delete

https://api.openai.com/v1/threads/{thread_id}/messages/{message_id}
Deletes a message.

Path parameters
message_id
string

Required
The ID of the message to delete.

thread_id
string

Required
The ID of the thread to which this message belongs.

Returns
Deletion status

Example request
curl -X DELETE https://api.openai.com/v1/threads/thread_abc123/messages/msg_abc123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"id": "msg_abc123",
"object": "thread.message.deleted",
"deleted": true
}
The message object
Beta
Represents a message within a thread.

assistant_id
string or null

If applicable, the ID of the assistant that authored this message.

attachments
array or null

A list of files attached to the message, and the tools they were added to.

Show properties
completed_at
integer or null

The Unix timestamp (in seconds) for when the message was completed.

content
array

The content of the message in array of text and/or images.

Show possible types
created_at
integer

The Unix timestamp (in seconds) for when the message was created.

id
string

The identifier, which can be referenced in API endpoints.

incomplete_at
integer or null

The Unix timestamp (in seconds) for when the message was marked as incomplete.

incomplete_details
object or null

On an incomplete message, details about why the message is incomplete.

Show properties
metadata
map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

object
string

The object type, which is always thread.message.

role
string

The entity that produced the message. One of user or assistant.

run_id
string or null

The ID of the run associated with the creation of this message. Value is null when messages are created manually using the create message or create thread endpoints.

status
string

The status of the message, which can be either in_progress, incomplete, or completed.

thread_id
string

The thread ID that this message belongs to.

OBJECT The message object
{
"id": "msg_abc123",
"object": "thread.message",
"created_at": 1698983503,
"thread_id": "thread_abc123",
"role": "assistant",
"content": [
{
"type": "text",
"text": {
"value": "Hi! How can I help you today?",
"annotations": []
}
}
],
"assistant_id": "asst_abc123",
"run_id": "run_abc123",
"attachments": [],
"metadata": {}
}
Runs
Beta
Represents an execution run on a thread.

Related guide: Assistants

Create run
Beta
post

https://api.openai.com/v1/threads/{thread_id}/runs
Create a run.

Path parameters
thread_id
string

Required
The ID of the thread to run.

Query parameters
include[]
array

Optional
A list of additional fields to include in the response. Currently the only supported value is step_details.tool_calls[*].file_search.results[*].content to fetch the file search result content.

See the file search tool documentation for more information.

Request body
assistant_id
string

Required
The ID of the assistant to use to execute this run.

additional_instructions
string or null

Optional
Appends additional instructions at the end of the instructions for the run. This is useful for modifying the behavior on a per-run basis without overriding other instructions.

additional_messages
array or null

Optional
Adds additional messages to the thread before creating the run.

Show properties
instructions
string or null

Optional
Overrides the instructions of the assistant. This is useful for modifying the behavior on a per-run basis.

max_completion_tokens
integer or null

Optional
The maximum number of completion tokens that may be used over the course of the run. The run will make a best effort to use only the number of completion tokens specified, across multiple turns of the run. If the run exceeds the number of completion tokens specified, the run will end with status incomplete. See incomplete_details for more info.

max_prompt_tokens
integer or null

Optional
The maximum number of prompt tokens that may be used over the course of the run. The run will make a best effort to use only the number of prompt tokens specified, across multiple turns of the run. If the run exceeds the number of prompt tokens specified, the run will end with status incomplete. See incomplete_details for more info.

metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

model
string

Optional
The ID of the Model to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.

parallel_tool_calls
boolean

Optional
Defaults to true
Whether to enable parallel function calling during tool use.

reasoning_effort
string or null

Optional
Defaults to medium
o-series models only

Constrains effort on reasoning for reasoning models. Currently supported values are low, medium, and high. Reducing reasoning effort can result in faster responses and fewer tokens used on reasoning in a response.

response_format
"auto" or object

Optional
Specifies the format that the model must output. Compatible with GPT-4o, GPT-4 Turbo, and all GPT-3.5 Turbo models since gpt-3.5-turbo-1106.

Setting to { "type": "json_schema", "json_schema": {...} } enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the Structured Outputs guide.

Setting to { "type": "json_object" } enables JSON mode, which ensures the message the model generates is valid JSON.

Important: when using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if finish_reason="length", which indicates the generation exceeded max_tokens or the conversation exceeded the max context length.

Show possible types
stream
boolean or null

Optional
If true, returns a stream of events that happen during the Run as server-sent events, terminating when the Run enters a terminal state with a data: [DONE] message.

temperature
number or null

Optional
Defaults to 1
What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

tool_choice
string or object

Optional
Controls which (if any) tool is called by the model. none means the model will not call any tools and instead generates a message. auto is the default value and means the model can pick between generating a message or calling one or more tools. required means the model must call one or more tools before responding to the user. Specifying a particular tool like {"type": "file_search"} or {"type": "function", "function": {"name": "my_function"}} forces the model to call that tool.

Show possible types
tools
array or null

Optional
Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.

Show possible types
top_p
number or null

Optional
Defaults to 1
An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

truncation_strategy
object or null

Optional
Controls for how a thread will be truncated prior to the run. Use this to control the intial context window of the run.

Show properties
Returns
A run object.

Default
Streaming
Streaming with Functions
Example request
curl https://api.openai.com/v1/threads/thread_abc123/runs \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json" \
 -H "OpenAI-Beta: assistants=v2" \
 -d '{
"assistant_id": "asst_abc123"
}'
Response
{
"id": "run_abc123",
"object": "thread.run",
"created_at": 1699063290,
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"status": "queued",
"started_at": 1699063290,
"expires_at": null,
"cancelled_at": null,
"failed_at": null,
"completed_at": 1699063291,
"last_error": null,
"model": "gpt-4o",
"instructions": null,
"incomplete_details": null,
"tools": [
{
"type": "code_interpreter"
}
],
"metadata": {},
"usage": null,
"temperature": 1.0,
"top_p": 1.0,
"max_prompt_tokens": 1000,
"max_completion_tokens": 1000,
"truncation_strategy": {
"type": "auto",
"last_messages": null
},
"response_format": "auto",
"tool_choice": "auto",
"parallel_tool_calls": true
}
Create thread and run
Beta
post

https://api.openai.com/v1/threads/runs
Create a thread and run it in one request.

Request body
assistant_id
string

Required
The ID of the assistant to use to execute this run.

instructions
string or null

Optional
Override the default system message of the assistant. This is useful for modifying the behavior on a per-run basis.

max_completion_tokens
integer or null

Optional
The maximum number of completion tokens that may be used over the course of the run. The run will make a best effort to use only the number of completion tokens specified, across multiple turns of the run. If the run exceeds the number of completion tokens specified, the run will end with status incomplete. See incomplete_details for more info.

max_prompt_tokens
integer or null

Optional
The maximum number of prompt tokens that may be used over the course of the run. The run will make a best effort to use only the number of prompt tokens specified, across multiple turns of the run. If the run exceeds the number of prompt tokens specified, the run will end with status incomplete. See incomplete_details for more info.

metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

model
string

Optional
The ID of the Model to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.

parallel_tool_calls
boolean

Optional
Defaults to true
Whether to enable parallel function calling during tool use.

response_format
"auto" or object

Optional
Specifies the format that the model must output. Compatible with GPT-4o, GPT-4 Turbo, and all GPT-3.5 Turbo models since gpt-3.5-turbo-1106.

Setting to { "type": "json_schema", "json_schema": {...} } enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the Structured Outputs guide.

Setting to { "type": "json_object" } enables JSON mode, which ensures the message the model generates is valid JSON.

Important: when using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if finish_reason="length", which indicates the generation exceeded max_tokens or the conversation exceeded the max context length.

Show possible types
stream
boolean or null

Optional
If true, returns a stream of events that happen during the Run as server-sent events, terminating when the Run enters a terminal state with a data: [DONE] message.

temperature
number or null

Optional
Defaults to 1
What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.

thread
object

Optional
Options to create a new thread. If no thread is provided when running a request, an empty thread will be created.

Show properties
tool_choice
string or object

Optional
Controls which (if any) tool is called by the model. none means the model will not call any tools and instead generates a message. auto is the default value and means the model can pick between generating a message or calling one or more tools. required means the model must call one or more tools before responding to the user. Specifying a particular tool like {"type": "file_search"} or {"type": "function", "function": {"name": "my_function"}} forces the model to call that tool.

Show possible types
tool_resources
object or null

Optional
A set of resources that are used by the assistant's tools. The resources are specific to the type of tool. For example, the code_interpreter tool requires a list of file IDs, while the file_search tool requires a list of vector store IDs.

Show properties
tools
array or null

Optional
Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.

Show possible types
top_p
number or null

Optional
Defaults to 1
An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

truncation_strategy
object or null

Optional
Controls for how a thread will be truncated prior to the run. Use this to control the intial context window of the run.

Show properties
Returns
A run object.

Default
Streaming
Streaming with Functions
Example request
curl https://api.openai.com/v1/threads/runs \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json" \
 -H "OpenAI-Beta: assistants=v2" \
 -d '{
"assistant_id": "asst_abc123",
"thread": {
"messages": [
{"role": "user", "content": "Explain deep learning to a 5 year old."}
]
}
}'
Response
{
"id": "run_abc123",
"object": "thread.run",
"created_at": 1699076792,
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"status": "queued",
"started_at": null,
"expires_at": 1699077392,
"cancelled_at": null,
"failed_at": null,
"completed_at": null,
"required_action": null,
"last_error": null,
"model": "gpt-4o",
"instructions": "You are a helpful assistant.",
"tools": [],
"tool_resources": {},
"metadata": {},
"temperature": 1.0,
"top_p": 1.0,
"max_completion_tokens": null,
"max_prompt_tokens": null,
"truncation_strategy": {
"type": "auto",
"last_messages": null
},
"incomplete_details": null,
"usage": null,
"response_format": "auto",
"tool_choice": "auto",
"parallel_tool_calls": true
}
List runs
Beta
get

https://api.openai.com/v1/threads/{thread_id}/runs
Returns a list of runs belonging to a thread.

Path parameters
thread_id
string

Required
The ID of the thread the run belongs to.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

before
string

Optional
A cursor for use in pagination. before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order
string

Optional
Defaults to desc
Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.

Returns
A list of run objects.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/runs \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"object": "list",
"data": [
{
"id": "run_abc123",
"object": "thread.run",
"created_at": 1699075072,
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"status": "completed",
"started_at": 1699075072,
"expires_at": null,
"cancelled_at": null,
"failed_at": null,
"completed_at": 1699075073,
"last_error": null,
"model": "gpt-4o",
"instructions": null,
"incomplete_details": null,
"tools": [
{
"type": "code_interpreter"
}
],
"tool_resources": {
"code_interpreter": {
"file_ids": [
"file-abc123",
"file-abc456"
]
}
},
"metadata": {},
"usage": {
"prompt_tokens": 123,
"completion_tokens": 456,
"total_tokens": 579
},
"temperature": 1.0,
"top_p": 1.0,
"max_prompt_tokens": 1000,
"max_completion_tokens": 1000,
"truncation_strategy": {
"type": "auto",
"last_messages": null
},
"response_format": "auto",
"tool_choice": "auto",
"parallel_tool_calls": true
},
{
"id": "run_abc456",
"object": "thread.run",
"created_at": 1699063290,
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"status": "completed",
"started_at": 1699063290,
"expires_at": null,
"cancelled_at": null,
"failed_at": null,
"completed_at": 1699063291,
"last_error": null,
"model": "gpt-4o",
"instructions": null,
"incomplete_details": null,
"tools": [
{
"type": "code_interpreter"
}
],
"tool_resources": {
"code_interpreter": {
"file_ids": [
"file-abc123",
"file-abc456"
]
}
},
"metadata": {},
"usage": {
"prompt_tokens": 123,
"completion_tokens": 456,
"total_tokens": 579
},
"temperature": 1.0,
"top_p": 1.0,
"max_prompt_tokens": 1000,
"max_completion_tokens": 1000,
"truncation_strategy": {
"type": "auto",
"last_messages": null
},
"response_format": "auto",
"tool_choice": "auto",
"parallel_tool_calls": true
}
],
"first_id": "run_abc123",
"last_id": "run_abc456",
"has_more": false
}
Retrieve run
Beta
get

https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}
Retrieves a run.

Path parameters
run_id
string

Required
The ID of the run to retrieve.

thread_id
string

Required
The ID of the thread that was run.

Returns
The run object matching the specified ID.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123 \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"id": "run_abc123",
"object": "thread.run",
"created_at": 1699075072,
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"status": "completed",
"started_at": 1699075072,
"expires_at": null,
"cancelled_at": null,
"failed_at": null,
"completed_at": 1699075073,
"last_error": null,
"model": "gpt-4o",
"instructions": null,
"incomplete_details": null,
"tools": [
{
"type": "code_interpreter"
}
],
"metadata": {},
"usage": {
"prompt_tokens": 123,
"completion_tokens": 456,
"total_tokens": 579
},
"temperature": 1.0,
"top_p": 1.0,
"max_prompt_tokens": 1000,
"max_completion_tokens": 1000,
"truncation_strategy": {
"type": "auto",
"last_messages": null
},
"response_format": "auto",
"tool_choice": "auto",
"parallel_tool_calls": true
}
Modify run
Beta
post

https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}
Modifies a run.

Path parameters
run_id
string

Required
The ID of the run to modify.

thread_id
string

Required
The ID of the thread that was run.

Request body
metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

Returns
The modified run object matching the specified ID.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123 \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json" \
 -H "OpenAI-Beta: assistants=v2" \
 -d '{
"metadata": {
"user_id": "user_abc123"
}
}'
Response
{
"id": "run_abc123",
"object": "thread.run",
"created_at": 1699075072,
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"status": "completed",
"started_at": 1699075072,
"expires_at": null,
"cancelled_at": null,
"failed_at": null,
"completed_at": 1699075073,
"last_error": null,
"model": "gpt-4o",
"instructions": null,
"incomplete_details": null,
"tools": [
{
"type": "code_interpreter"
}
],
"tool_resources": {
"code_interpreter": {
"file_ids": [
"file-abc123",
"file-abc456"
]
}
},
"metadata": {
"user_id": "user_abc123"
},
"usage": {
"prompt_tokens": 123,
"completion_tokens": 456,
"total_tokens": 579
},
"temperature": 1.0,
"top_p": 1.0,
"max_prompt_tokens": 1000,
"max_completion_tokens": 1000,
"truncation_strategy": {
"type": "auto",
"last_messages": null
},
"response_format": "auto",
"tool_choice": "auto",
"parallel_tool_calls": true
}
Submit tool outputs to run
Beta
post

https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}/submit_tool_outputs
When a run has the status: "requires_action" and required_action.type is submit_tool_outputs, this endpoint can be used to submit the outputs from the tool calls once they're all completed. All outputs must be submitted in a single request.

Path parameters
run_id
string

Required
The ID of the run that requires the tool output submission.

thread_id
string

Required
The ID of the thread to which this run belongs.

Request body
tool_outputs
array

Required
A list of tools for which the outputs are being submitted.

Show properties
stream
boolean or null

Optional
If true, returns a stream of events that happen during the Run as server-sent events, terminating when the Run enters a terminal state with a data: [DONE] message.

Returns
The modified run object matching the specified ID.

Default
Streaming
Example request
curl https://api.openai.com/v1/threads/thread_123/runs/run_123/submit_tool_outputs \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json" \
 -H "OpenAI-Beta: assistants=v2" \
 -d '{
"tool_outputs": [
{
"tool_call_id": "call_001",
"output": "70 degrees and sunny."
}
]
}'
Response
{
"id": "run_123",
"object": "thread.run",
"created_at": 1699075592,
"assistant_id": "asst_123",
"thread_id": "thread_123",
"status": "queued",
"started_at": 1699075592,
"expires_at": 1699076192,
"cancelled_at": null,
"failed_at": null,
"completed_at": null,
"last_error": null,
"model": "gpt-4o",
"instructions": null,
"tools": [
{
"type": "function",
"function": {
"name": "get_current_weather",
"description": "Get the current weather in a given location",
"parameters": {
"type": "object",
"properties": {
"location": {
"type": "string",
"description": "The city and state, e.g. San Francisco, CA"
},
"unit": {
"type": "string",
"enum": ["celsius", "fahrenheit"]
}
},
"required": ["location"]
}
}
}
],
"metadata": {},
"usage": null,
"temperature": 1.0,
"top_p": 1.0,
"max_prompt_tokens": 1000,
"max_completion_tokens": 1000,
"truncation_strategy": {
"type": "auto",
"last_messages": null
},
"response_format": "auto",
"tool_choice": "auto",
"parallel_tool_calls": true
}
Cancel a run
Beta
post

https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}/cancel
Cancels a run that is in_progress.

Path parameters
run_id
string

Required
The ID of the run to cancel.

thread_id
string

Required
The ID of the thread to which this run belongs.

Returns
The modified run object matching the specified ID.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123/cancel \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "OpenAI-Beta: assistants=v2" \
 -X POST
Response
{
"id": "run_abc123",
"object": "thread.run",
"created_at": 1699076126,
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"status": "cancelling",
"started_at": 1699076126,
"expires_at": 1699076726,
"cancelled_at": null,
"failed_at": null,
"completed_at": null,
"last_error": null,
"model": "gpt-4o",
"instructions": "You summarize books.",
"tools": [
{
"type": "file_search"
}
],
"tool_resources": {
"file_search": {
"vector_store_ids": ["vs_123"]
}
},
"metadata": {},
"usage": null,
"temperature": 1.0,
"top_p": 1.0,
"response_format": "auto",
"tool_choice": "auto",
"parallel_tool_calls": true
}
The run object
Beta
Represents an execution run on a thread.

assistant_id
string

The ID of the assistant used for execution of this run.

cancelled_at
integer or null

The Unix timestamp (in seconds) for when the run was cancelled.

completed_at
integer or null

The Unix timestamp (in seconds) for when the run was completed.

created_at
integer

The Unix timestamp (in seconds) for when the run was created.

expires_at
integer or null

The Unix timestamp (in seconds) for when the run will expire.

failed_at
integer or null

The Unix timestamp (in seconds) for when the run failed.

id
string

The identifier, which can be referenced in API endpoints.

incomplete_details
object or null

Details on why the run is incomplete. Will be null if the run is not incomplete.

Show properties
instructions
string

The instructions that the assistant used for this run.

last_error
object or null

The last error associated with this run. Will be null if there are no errors.

Show properties
max_completion_tokens
integer or null

The maximum number of completion tokens specified to have been used over the course of the run.

max_prompt_tokens
integer or null

The maximum number of prompt tokens specified to have been used over the course of the run.

metadata
map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

model
string

The model that the assistant used for this run.

object
string

The object type, which is always thread.run.

parallel_tool_calls
boolean

Whether to enable parallel function calling during tool use.

required_action
object or null

Details on the action required to continue the run. Will be null if no action is required.

Show properties
response_format
"auto" or object

Specifies the format that the model must output. Compatible with GPT-4o, GPT-4 Turbo, and all GPT-3.5 Turbo models since gpt-3.5-turbo-1106.

Setting to { "type": "json_schema", "json_schema": {...} } enables Structured Outputs which ensures the model will match your supplied JSON schema. Learn more in the Structured Outputs guide.

Setting to { "type": "json_object" } enables JSON mode, which ensures the message the model generates is valid JSON.

Important: when using JSON mode, you must also instruct the model to produce JSON yourself via a system or user message. Without this, the model may generate an unending stream of whitespace until the generation reaches the token limit, resulting in a long-running and seemingly "stuck" request. Also note that the message content may be partially cut off if finish_reason="length", which indicates the generation exceeded max_tokens or the conversation exceeded the max context length.

Show possible types
started_at
integer or null

The Unix timestamp (in seconds) for when the run was started.

status
string

The status of the run, which can be either queued, in_progress, requires_action, cancelling, cancelled, failed, completed, incomplete, or expired.

temperature
number or null

The sampling temperature used for this run. If not set, defaults to 1.

thread_id
string

The ID of the thread that was executed on as a part of this run.

tool_choice
string or object

Controls which (if any) tool is called by the model. none means the model will not call any tools and instead generates a message. auto is the default value and means the model can pick between generating a message or calling one or more tools. required means the model must call one or more tools before responding to the user. Specifying a particular tool like {"type": "file_search"} or {"type": "function", "function": {"name": "my_function"}} forces the model to call that tool.

Show possible types
tools
array

The list of tools that the assistant used for this run.

Show possible types
top_p
number or null

The nucleus sampling value used for this run. If not set, defaults to 1.

truncation_strategy
object or null

Controls for how a thread will be truncated prior to the run. Use this to control the intial context window of the run.

Show properties
usage
object or null

Usage statistics related to the run. This value will be null if the run is not in a terminal state (i.e. in_progress, queued, etc.).

Show properties
OBJECT The run object
{
"id": "run_abc123",
"object": "thread.run",
"created_at": 1698107661,
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"status": "completed",
"started_at": 1699073476,
"expires_at": null,
"cancelled_at": null,
"failed_at": null,
"completed_at": 1699073498,
"last_error": null,
"model": "gpt-4o",
"instructions": null,
"tools": [{"type": "file_search"}, {"type": "code_interpreter"}],
"metadata": {},
"incomplete_details": null,
"usage": {
"prompt_tokens": 123,
"completion_tokens": 456,
"total_tokens": 579
},
"temperature": 1.0,
"top_p": 1.0,
"max_prompt_tokens": 1000,
"max_completion_tokens": 1000,
"truncation_strategy": {
"type": "auto",
"last_messages": null
},
"response_format": "auto",
"tool_choice": "auto",
"parallel_tool_calls": true
}
Run steps
Beta
Represents the steps (model and tool calls) taken during the run.

Related guide: Assistants

List run steps
Beta
get

https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}/steps
Returns a list of run steps belonging to a run.

Path parameters
run_id
string

Required
The ID of the run the run steps belong to.

thread_id
string

Required
The ID of the thread the run and run steps belong to.

Query parameters
after
string

Optional
A cursor for use in pagination. after is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, ending with obj_foo, your subsequent call can include after=obj_foo in order to fetch the next page of the list.

before
string

Optional
A cursor for use in pagination. before is an object ID that defines your place in the list. For instance, if you make a list request and receive 100 objects, starting with obj_foo, your subsequent call can include before=obj_foo in order to fetch the previous page of the list.

include[]
array

Optional
A list of additional fields to include in the response. Currently the only supported value is step_details.tool_calls[*].file_search.results[*].content to fetch the file search result content.

See the file search tool documentation for more information.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order
string

Optional
Defaults to desc
Sort order by the created_at timestamp of the objects. asc for ascending order and desc for descending order.

Returns
A list of run step objects.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123/steps \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"object": "list",
"data": [
{
"id": "step_abc123",
"object": "thread.run.step",
"created_at": 1699063291,
"run_id": "run_abc123",
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"type": "message_creation",
"status": "completed",
"cancelled_at": null,
"completed_at": 1699063291,
"expired_at": null,
"failed_at": null,
"last_error": null,
"step_details": {
"type": "message_creation",
"message_creation": {
"message_id": "msg_abc123"
}
},
"usage": {
"prompt_tokens": 123,
"completion_tokens": 456,
"total_tokens": 579
}
}
],
"first_id": "step_abc123",
"last_id": "step_abc456",
"has_more": false
}
Retrieve run step
Beta
get

https://api.openai.com/v1/threads/{thread_id}/runs/{run_id}/steps/{step_id}
Retrieves a run step.

Path parameters
run_id
string

Required
The ID of the run to which the run step belongs.

step_id
string

Required
The ID of the run step to retrieve.

thread_id
string

Required
The ID of the thread to which the run and run step belongs.

Query parameters
include[]
array

Optional
A list of additional fields to include in the response. Currently the only supported value is step_details.tool_calls[*].file_search.results[*].content to fetch the file search result content.

See the file search tool documentation for more information.

Returns
The run step object matching the specified ID.

Example request
curl https://api.openai.com/v1/threads/thread_abc123/runs/run_abc123/steps/step_abc123 \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -H "Content-Type: application/json" \
 -H "OpenAI-Beta: assistants=v2"
Response
{
"id": "step_abc123",
"object": "thread.run.step",
"created_at": 1699063291,
"run_id": "run_abc123",
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"type": "message_creation",
"status": "completed",
"cancelled_at": null,
"completed_at": 1699063291,
"expired_at": null,
"failed_at": null,
"last_error": null,
"step_details": {
"type": "message_creation",
"message_creation": {
"message_id": "msg_abc123"
}
},
"usage": {
"prompt_tokens": 123,
"completion_tokens": 456,
"total_tokens": 579
}
}
The run step object
Beta
Represents a step in execution of a run.

assistant_id
string

The ID of the assistant associated with the run step.

cancelled_at
integer or null

The Unix timestamp (in seconds) for when the run step was cancelled.

completed_at
integer or null

The Unix timestamp (in seconds) for when the run step completed.

created_at
integer

The Unix timestamp (in seconds) for when the run step was created.

expired_at
integer or null

The Unix timestamp (in seconds) for when the run step expired. A step is considered expired if the parent run is expired.

failed_at
integer or null

The Unix timestamp (in seconds) for when the run step failed.

id
string

The identifier of the run step, which can be referenced in API endpoints.

last_error
object or null

The last error associated with this run step. Will be null if there are no errors.

Show properties
metadata
map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

object
string

The object type, which is always thread.run.step.

run_id
string

The ID of the run that this run step is a part of.

status
string

The status of the run step, which can be either in_progress, cancelled, failed, completed, or expired.

step_details
object

The details of the run step.

Show possible types
thread_id
string

The ID of the thread that was run.

type
string

The type of run step, which can be either message_creation or tool_calls.

usage
object or null

Usage statistics related to the run step. This value will be null while the run step's status is in_progress.

Show properties
OBJECT The run step object
{
"id": "step_abc123",
"object": "thread.run.step",
"created_at": 1699063291,
"run_id": "run_abc123",
"assistant_id": "asst_abc123",
"thread_id": "thread_abc123",
"type": "message_creation",
"status": "completed",
"cancelled_at": null,
"completed_at": 1699063291,
"expired_at": null,
"failed_at": null,
"last_error": null,
"step_details": {
"type": "message_creation",
"message_creation": {
"message_id": "msg_abc123"
}
},
"usage": {
"prompt_tokens": 123,
"completion_tokens": 456,
"total_tokens": 579
}
}
Streaming
Beta
Stream the result of executing a Run or resuming a Run after submitting tool outputs. You can stream events from the Create Thread and Run, Create Run, and Submit Tool Outputs endpoints by passing "stream": true. The response will be a Server-Sent events stream. Our Node and Python SDKs provide helpful utilities to make streaming easy. Reference the Assistants API quickstart to learn more.

The message delta object
Beta
Represents a message delta i.e. any changed fields on a message during streaming.

delta
object

The delta containing the fields that have changed on the Message.

Show properties
id
string

The identifier of the message, which can be referenced in API endpoints.

object
string

The object type, which is always thread.message.delta.

OBJECT The message delta object
{
"id": "msg_123",
"object": "thread.message.delta",
"delta": {
"content": [
{
"index": 0,
"type": "text",
"text": { "value": "Hello", "annotations": [] }
}
]
}
}
The run step delta object
Beta
Represents a run step delta i.e. any changed fields on a run step during streaming.

delta
object

The delta containing the fields that have changed on the run step.

Show properties
id
string

The identifier of the run step, which can be referenced in API endpoints.

object
string

The object type, which is always thread.run.step.delta.

OBJECT The run step delta object
{
"id": "step_123",
"object": "thread.run.step.delta",
"delta": {
"step_details": {
"type": "tool_calls",
"tool_calls": [
{
"index": 0,
"id": "call_123",
"type": "code_interpreter",
"code_interpreter": { "input": "", "outputs": [] }
}
]
}
}
}
Assistant stream events
Beta
Represents an event emitted when streaming a Run.

Each event in a server-sent events stream has an event and data property:

event: thread.created
data: {"id": "thread_123", "object": "thread", ...}
We emit events whenever a new object is created, transitions to a new state, or is being streamed in parts (deltas). For example, we emit thread.run.created when a new run is created, thread.run.completed when a run completes, and so on. When an Assistant chooses to create a message during a run, we emit a thread.message.created event, a thread.message.in_progress event, many thread.message.delta events, and finally a thread.message.completed event.

We may add additional events over time, so we recommend handling unknown events gracefully in your code. See the Assistants API quickstart to learn how to integrate the Assistants API with streaming.

done
data is [DONE]

Occurs when a stream ends.

error
data is an error

Occurs when an error occurs. This can happen due to an internal server error or a timeout.

thread.created
data is a thread

Occurs when a new thread is created.

thread.message.completed
data is a message

Occurs when a message is completed.

thread.message.created
data is a message

Occurs when a message is created.

thread.message.delta
data is a message delta

Occurs when parts of a Message are being streamed.

thread.message.in_progress
data is a message

Occurs when a message moves to an in_progress state.

thread.message.incomplete
data is a message

Occurs when a message ends before it is completed.

thread.run.cancelled
data is a run

Occurs when a run is cancelled.

thread.run.cancelling
data is a run

Occurs when a run moves to a cancelling status.

thread.run.completed
data is a run

Occurs when a run is completed.

thread.run.created
data is a run

Occurs when a new run is created.

thread.run.expired
data is a run

Occurs when a run expires.

thread.run.failed
data is a run

Occurs when a run fails.

thread.run.in_progress
data is a run

Occurs when a run moves to an in_progress status.

thread.run.incomplete
data is a run

Occurs when a run ends with status incomplete.

thread.run.queued
data is a run

Occurs when a run moves to a queued status.

thread.run.requires_action
data is a run

Occurs when a run moves to a requires_action status.

thread.run.step.cancelled
data is a run step

Occurs when a run step is cancelled.

thread.run.step.completed
data is a run step

Occurs when a run step is completed.

thread.run.step.created
data is a run step

Occurs when a run step is created.

thread.run.step.delta
data is a run step delta

Occurs when parts of a run step are being streamed.

thread.run.step.expired
data is a run step

Occurs when a run step expires.

thread.run.step.failed
data is a run step

Occurs when a run step fails.

thread.run.step.in_progress
data is a run step

Occurs when a run step moves to an in_progress state.
