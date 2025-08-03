Responses vs. Chat Completions
Compare the Responses API and Chat Completions API.
The Responses API and Chat Completions API are two different ways to interact with OpenAI's models. This guide explains the key differences between the two APIs.

Why the Responses API?
The Responses API is our newest core API and an agentic API primitive, combining the simplicity of Chat Completions with the ability to do more agentic tasks. As model capabilities evolve, the Responses API is a flexible foundation for building action-oriented applications, with built-in tools:

Web search
File search
Computer use
If you're a new user, we recommend using the Responses API.

Capabilities Chat Completions API Responses API
Text generation
Audio Coming soon
Vision
Structured Outputs
Function calling
Web search
File search
Computer use
Code interpreter
MCP
The Chat Completions API is not going away
The Chat Completions API is an industry standard for building AI applications, and we intend to continue supporting this API indefinitely. We're introducing the Responses API to simplify workflows involving tool use, code execution, and state management. We believe this new API primitive will allow us to more effectively enhance the OpenAI platform into the future.

A stateful API and semantic events
Events are simpler with the Responses API. It has a predictable, event-driven architecture, whereas the Chat Completions API continuously appends to the content field as tokens are generated—requiring you to manually track differences between each state. Multi-step conversational logic and reasoning are easier to implement with the Responses API.

The Responses API clearly emits semantic events detailing precisely what changed (e.g., specific text additions), so you can write integrations targeted at specific emitted events (e.g., text changes), simplifying integration and improving type safety.

Model availability in each API
Whenever possible, all new models will be added to both the Chat Completions API and Responses API. Some models may only be available through Responses API if they use built-in tools (e.g. our computer use models), or trigger multiple model generation turns behind the scenes (e.g. o1-pro) . The detail pages for each model will indicate if they support Chat Completions, Responses, or both.

Compare the code
The following examples show how to make a basic API call to the Chat Completions API and the Responses API.

Text generation example
Both APIs make it easy to generate output from our models. A completion requires a messages array, but a response requires an input (string or array, as shown below).

Chat Completions API
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
model="gpt-4.1",
messages=[
{
"role": "user",
"content": "Write a one-sentence bedtime story about a unicorn."
}
]
)

print(completion.choices[0].message.content)
Responses API
from openai import OpenAI
client = OpenAI()

response = client.responses.create(
model="gpt-4.1",
input=[
{
"role": "user",
"content": "Write a one-sentence bedtime story about a unicorn."
}
]
)

print(response.output_text)
When you get a response back from the Responses API, the fields differ slightly. Instead of a message, you receive a typed response object with its own id. Responses are stored by default. Chat completions are stored by default for new accounts. To disable storage when using either API, set store: false.

Chat Completions API
[
{
"index": 0,
"message": {
"role": "assistant",
"content": "Under the soft glow of the moon, Luna the unicorn danced through fields of twinkling stardust, leaving trails of dreams for every child asleep.",
"refusal": null
},
"logprobs": null,
"finish_reason": "stop"
}
]
Responses API
[
{
"id": "msg_67b73f697ba4819183a15cc17d011509",
"type": "message",
"role": "assistant",
"content": [
{
"type": "output_text",
"text": "Under the soft glow of the moon, Luna the unicorn danced through fields of twinkling stardust, leaving trails of dreams for every child asleep.",
"annotations": []
}
]
}
]
Other noteworthy differences
The Responses API returns output, while the Chat Completions API returns a choices array.
Structured Outputs API shape is different. Instead of response_format, use text.format in Responses. Learn more in the Structured Outputs guide.
Function calling API shape is different—both for the function config on the request and function calls sent back in the response. See the full difference in the function calling guide.
Reasoning is different. Instead of reasoning_effort in Chat Completions, use reasoning.effort with the Responses API. Read more details in the reasoning guide.
The Responses SDK has an output_text helper, which the Chat Completions SDK does not have.
Conversation state: You have to manage conversation state yourself in Chat Completions, while Responses has previous_response_id to help you with long-running conversations.
Responses are stored by default. Chat completions are stored by default for new accounts. To disable storage, set store: false.
What this means for existing APIs
Chat Completions
The Chat Completions API remains our most widely used API. We'll continue supporting it with new models and capabilities. If you don't need built-in tools for your application, you can confidently continue using Chat Completions.

We'll keep releasing new models to Chat Completions whenever their capabilities don't depend on built-in tools or multiple model calls. When you're ready for advanced capabilities designed specifically for agent workflows, we recommend the Responses API.

Assistants
Based on developer feedback from the Assistants API beta, we've incorporated key improvements into the Responses API to make it more flexible, faster, and easier to use. The Responses API represents the future direction for building agents on OpenAI.

We're working to achieve full feature parity between the Assistants and the Responses API, including support for Assistant-like and Thread-like objects and the Code Interpreter tool. When complete, we plan to formally announce the deprecation of the Assistants API with a target sunset date in the first half of 2026.

Upon deprecation, we will provide a clear migration guide from the Assistants API to the Responses API that allows developers to preserve all their data and migrate their applications. Until we formally announce the deprecation, we'll continue delivering new models to the Assistants API.

Responses
OpenAI's most advanced interface for generating model responses. Supports text and image inputs, and text outputs. Create stateful interactions with the model, using the output of previous responses as input. Extend the model's capabilities with built-in tools for file search, web search, computer use, and more. Allow the model access to external systems and data using function calling.

Related guides:

Quickstart
Text inputs and outputs
Image inputs
Structured Outputs
Function calling
Conversation state
Extend the models with tools
Create a model response
post

https://api.openai.com/v1/responses
Creates a model response. Provide text or image inputs to generate text or JSON outputs. Have the model call your own custom code or use built-in tools like web search or file search to use your own data as input for the model's response.

Request body
background
boolean or null

Optional
Defaults to false
Whether to run the model response in the background. Learn more.

include
array or null

Optional
Specify additional output data to include in the model response. Currently supported values are:

code_interpreter_call.outputs: Includes the outputs of python code execution in code interpreter tool call items.
computer_call_output.output.image_url: Include image urls from the computer call output.
file_search_call.results: Include the search results of the file search tool call.
message.input_image.image_url: Include image urls from the input message.
message.output_text.logprobs: Include logprobs with assistant messages.
reasoning.encrypted_content: Includes an encrypted version of reasoning tokens in reasoning item outputs. This enables reasoning items to be used in multi-turn conversations when using the Responses API statelessly (like when the store parameter is set to false, or when an organization is enrolled in the zero data retention program).
input
string or array

Optional
Text, image, or file inputs to the model, used to generate a response.

Learn more:

Text inputs and outputs
Image inputs
File inputs
Conversation state
Function calling

Show possible types
instructions
string or null

Optional
A system (or developer) message inserted into the model's context.

When using along with previous_response_id, the instructions from a previous response will not be carried over to the next response. This makes it simple to swap out system (or developer) messages in new responses.

max_output_tokens
integer or null

Optional
An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.

max_tool_calls
integer or null

Optional
The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.

metadata
map

Optional
Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

model
string

Optional
Model ID used to generate the response, like gpt-4o or o3. OpenAI offers a wide range of models with different capabilities, performance characteristics, and price points. Refer to the model guide to browse and compare available models.

parallel_tool_calls
boolean or null

Optional
Defaults to true
Whether to allow the model to run tool calls in parallel.

previous_response_id
string or null

Optional
The unique ID of the previous response to the model. Use this to create multi-turn conversations. Learn more about conversation state.

prompt
object or null

Optional
Reference to a prompt template and its variables. Learn more.

Show properties
prompt_cache_key
string

Optional
Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the user field. Learn more.

reasoning
object or null

Optional
o-series models only

Configuration options for reasoning models.

Show properties
safety_identifier
string

Optional
A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies. The IDs should be a string that uniquely identifies each user. We recommend hashing their username or email address, in order to avoid sending us any identifying information. Learn more.

service_tier
string or null

Optional
Defaults to auto
Specifies the processing type used for serving the request.

If set to 'auto', then the request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'.
If set to 'default', then the request will be processed with the standard pricing and performance for the selected model.
If set to 'flex' or 'priority', then the request will be processed with the corresponding service tier. Contact sales to learn more about Priority processing.
When not set, the default behavior is 'auto'.
When the service_tier parameter is set, the response body will include the service_tier value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter.

store
boolean or null

Optional
Defaults to true
Whether to store the generated model response for later retrieval via API.

stream
boolean or null

Optional
Defaults to false
If set to true, the model response data will be streamed to the client as it is generated using server-sent events. See the Streaming section below for more information.

temperature
number or null

Optional
Defaults to 1
What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both.

text
object

Optional
Configuration options for a text response from the model. Can be plain text or structured JSON data. Learn more:

Text inputs and outputs
Structured Outputs

Show properties
tool_choice
string or object

Optional
How the model should select which tool (or tools) to use when generating a response. See the tools parameter to see how to specify which tools the model can call.

Show possible types
tools
array

Optional
An array of tools the model may call while generating a response. You can specify which tool to use by setting the tool_choice parameter.

The two categories of tools you can provide the model are:

Built-in tools: Tools that are provided by OpenAI that extend the model's capabilities, like web search or file search. Learn more about built-in tools.
Function calls (custom tools): Functions that are defined by you, enabling the model to call your own code. Learn more about function calling.

Show possible types
top_logprobs
integer or null

Optional
An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability.

top_p
number or null

Optional
Defaults to 1
An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

truncation
string or null

Optional
Defaults to disabled
The truncation strategy to use for the model response.

auto: If the context of this response and previous ones exceeds the model's context window size, the model will truncate the response to fit the context window by dropping input items in the middle of the conversation.
disabled (default): If a model response will exceed the context window size for a model, the request will fail with a 400 error.
user
Deprecated
string

Optional
This field is being replaced by safety_identifier and prompt_cache_key. Use prompt_cache_key instead to maintain caching optimizations. A stable identifier for your end-users. Used to boost cache hit rates by better bucketing similar requests and to help OpenAI detect and prevent abuse. Learn more.

Returns
Returns a Response object.

Text input
Image input
File input
Web search
File search
Streaming
Functions
Reasoning
Example request
curl https://api.openai.com/v1/responses \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY" \
 -d '{
"model": "gpt-4.1",
"input": "Tell me a three sentence bedtime story about a unicorn."
}'
Response
{
"id": "resp_67ccd2bed1ec8190b14f964abc0542670bb6a6b452d3795b",
"object": "response",
"created_at": 1741476542,
"status": "completed",
"error": null,
"incomplete_details": null,
"instructions": null,
"max_output_tokens": null,
"model": "gpt-4.1-2025-04-14",
"output": [
{
"type": "message",
"id": "msg_67ccd2bf17f0819081ff3bb2cf6508e60bb6a6b452d3795b",
"status": "completed",
"role": "assistant",
"content": [
{
"type": "output_text",
"text": "In a peaceful grove beneath a silver moon, a unicorn named Lumina discovered a hidden pool that reflected the stars. As she dipped her horn into the water, the pool began to shimmer, revealing a pathway to a magical realm of endless night skies. Filled with wonder, Lumina whispered a wish for all who dream to find their own hidden magic, and as she glanced back, her hoofprints sparkled like stardust.",
"annotations": []
}
]
}
],
"parallel_tool_calls": true,
"previous_response_id": null,
"reasoning": {
"effort": null,
"summary": null
},
"store": true,
"temperature": 1.0,
"text": {
"format": {
"type": "text"
}
},
"tool_choice": "auto",
"tools": [],
"top_p": 1.0,
"truncation": "disabled",
"usage": {
"input_tokens": 36,
"input_tokens_details": {
"cached_tokens": 0
},
"output_tokens": 87,
"output_tokens_details": {
"reasoning_tokens": 0
},
"total_tokens": 123
},
"user": null,
"metadata": {}
}
Get a model response
get

https://api.openai.com/v1/responses/{response_id}
Retrieves a model response with the given ID.

Path parameters
response_id
string

Required
The ID of the response to retrieve.

Query parameters
include
array

Optional
Additional fields to include in the response. See the include parameter for Response creation above for more information.

starting_after
integer

Optional
The sequence number of the event after which to start streaming.

stream
boolean

Optional
If set to true, the model response data will be streamed to the client as it is generated using server-sent events. See the Streaming section below for more information.

Returns
The Response object matching the specified ID.

Example request
curl https://api.openai.com/v1/responses/resp_123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY"
Response
{
"id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
"object": "response",
"created_at": 1741386163,
"status": "completed",
"error": null,
"incomplete_details": null,
"instructions": null,
"max_output_tokens": null,
"model": "gpt-4o-2024-08-06",
"output": [
{
"type": "message",
"id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
"status": "completed",
"role": "assistant",
"content": [
{
"type": "output_text",
"text": "Silent circuits hum, \nThoughts emerge in data streams— \nDigital dawn breaks.",
"annotations": []
}
]
}
],
"parallel_tool_calls": true,
"previous_response_id": null,
"reasoning": {
"effort": null,
"summary": null
},
"store": true,
"temperature": 1.0,
"text": {
"format": {
"type": "text"
}
},
"tool_choice": "auto",
"tools": [],
"top_p": 1.0,
"truncation": "disabled",
"usage": {
"input_tokens": 32,
"input_tokens_details": {
"cached_tokens": 0
},
"output_tokens": 18,
"output_tokens_details": {
"reasoning_tokens": 0
},
"total_tokens": 50
},
"user": null,
"metadata": {}
}
Delete a model response
delete

https://api.openai.com/v1/responses/{response_id}
Deletes a model response with the given ID.

Path parameters
response_id
string

Required
The ID of the response to delete.

Returns
A success message.

Example request
curl -X DELETE https://api.openai.com/v1/responses/resp_123 \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY"
Response
{
"id": "resp_6786a1bec27481909a17d673315b29f6",
"object": "response",
"deleted": true
}
Cancel a response
post

https://api.openai.com/v1/responses/{response_id}/cancel
Cancels a model response with the given ID. Only responses created with the background parameter set to true can be cancelled. Learn more.

Path parameters
response_id
string

Required
The ID of the response to cancel.

Returns
A Response object.

Example request
curl -X POST https://api.openai.com/v1/responses/resp_123/cancel \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY"
Response
{
"id": "resp_67cb71b351908190a308f3859487620d06981a8637e6bc44",
"object": "response",
"created_at": 1741386163,
"status": "completed",
"error": null,
"incomplete_details": null,
"instructions": null,
"max_output_tokens": null,
"model": "gpt-4o-2024-08-06",
"output": [
{
"type": "message",
"id": "msg_67cb71b3c2b0819084d481baaaf148f206981a8637e6bc44",
"status": "completed",
"role": "assistant",
"content": [
{
"type": "output_text",
"text": "Silent circuits hum, \nThoughts emerge in data streams— \nDigital dawn breaks.",
"annotations": []
}
]
}
],
"parallel_tool_calls": true,
"previous_response_id": null,
"reasoning": {
"effort": null,
"summary": null
},
"store": true,
"temperature": 1.0,
"text": {
"format": {
"type": "text"
}
},
"tool_choice": "auto",
"tools": [],
"top_p": 1.0,
"truncation": "disabled",
"usage": {
"input_tokens": 32,
"input_tokens_details": {
"cached_tokens": 0
},
"output_tokens": 18,
"output_tokens_details": {
"reasoning_tokens": 0
},
"total_tokens": 50
},
"user": null,
"metadata": {}
}
List input items
get

https://api.openai.com/v1/responses/{response_id}/input_items
Returns a list of input items for a given response.

Path parameters
response_id
string

Required
The ID of the response to retrieve input items for.

Query parameters
after
string

Optional
An item ID to list items after, used in pagination.

before
string

Optional
An item ID to list items before, used in pagination.

include
array

Optional
Additional fields to include in the response. See the include parameter for Response creation above for more information.

limit
integer

Optional
Defaults to 20
A limit on the number of objects to be returned. Limit can range between 1 and 100, and the default is 20.

order
string

Optional
The order to return the input items in. Default is desc.

asc: Return the input items in ascending order.
desc: Return the input items in descending order.
Returns
A list of input item objects.

Example request
curl https://api.openai.com/v1/responses/resp_abc123/input_items \
 -H "Content-Type: application/json" \
 -H "Authorization: Bearer $OPENAI_API_KEY"
Response
{
"object": "list",
"data": [
{
"id": "msg_abc123",
"type": "message",
"role": "user",
"content": [
{
"type": "input_text",
"text": "Tell me a three sentence bedtime story about a unicorn."
}
]
}
],
"first_id": "msg_abc123",
"last_id": "msg_abc123",
"has_more": false
}
The response object
background
boolean or null

Whether to run the model response in the background. Learn more.

created_at
number

Unix timestamp (in seconds) of when this Response was created.

error
object or null

An error object returned when the model fails to generate a Response.

Show properties
id
string

Unique identifier for this Response.

incomplete_details
object or null

Details about why the response is incomplete.

Show properties
instructions
string or array

A system (or developer) message inserted into the model's context.

When using along with previous_response_id, the instructions from a previous response will not be carried over to the next response. This makes it simple to swap out system (or developer) messages in new responses.

Show possible types
max_output_tokens
integer or null

An upper bound for the number of tokens that can be generated for a response, including visible output tokens and reasoning tokens.

max_tool_calls
integer or null

The maximum number of total calls to built-in tools that can be processed in a response. This maximum number applies across all built-in tool calls, not per individual tool. Any further attempts to call a tool by the model will be ignored.

metadata
map

Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format, and querying for objects via API or the dashboard.

Keys are strings with a maximum length of 64 characters. Values are strings with a maximum length of 512 characters.

model
string

Model ID used to generate the response, like gpt-4o or o3. OpenAI offers a wide range of models with different capabilities, performance characteristics, and price points. Refer to the model guide to browse and compare available models.

object
string

The object type of this resource - always set to response.

output
array

An array of content items generated by the model.

The length and order of items in the output array is dependent on the model's response.
Rather than accessing the first item in the output array and assuming it's an assistant message with the content generated by the model, you might consider using the output_text property where supported in SDKs.

Show possible types
output_text
string or null

SDK Only
SDK-only convenience property that contains the aggregated text output from all output_text items in the output array, if any are present. Supported in the Python and JavaScript SDKs.

parallel_tool_calls
boolean

Whether to allow the model to run tool calls in parallel.

previous_response_id
string or null

The unique ID of the previous response to the model. Use this to create multi-turn conversations. Learn more about conversation state.

prompt
object or null

Reference to a prompt template and its variables. Learn more.

Show properties
prompt_cache_key
string

Used by OpenAI to cache responses for similar requests to optimize your cache hit rates. Replaces the user field. Learn more.

reasoning
object or null

o-series models only

Configuration options for reasoning models.

Show properties
safety_identifier
string

A stable identifier used to help detect users of your application that may be violating OpenAI's usage policies. The IDs should be a string that uniquely identifies each user. We recommend hashing their username or email address, in order to avoid sending us any identifying information. Learn more.

service_tier
string or null

Specifies the processing type used for serving the request.

If set to 'auto', then the request will be processed with the service tier configured in the Project settings. Unless otherwise configured, the Project will use 'default'.
If set to 'default', then the request will be processed with the standard pricing and performance for the selected model.
If set to 'flex' or 'priority', then the request will be processed with the corresponding service tier. Contact sales to learn more about Priority processing.
When not set, the default behavior is 'auto'.
When the service_tier parameter is set, the response body will include the service_tier value based on the processing mode actually used to serve the request. This response value may be different from the value set in the parameter.

status
string

The status of the response generation. One of completed, failed, in_progress, cancelled, queued, or incomplete.

temperature
number or null

What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic. We generally recommend altering this or top_p but not both.

text
object

Configuration options for a text response from the model. Can be plain text or structured JSON data. Learn more:

Text inputs and outputs
Structured Outputs

Show properties
tool_choice
string or object

How the model should select which tool (or tools) to use when generating a response. See the tools parameter to see how to specify which tools the model can call.

Show possible types
tools
array

An array of tools the model may call while generating a response. You can specify which tool to use by setting the tool_choice parameter.

The two categories of tools you can provide the model are:

Built-in tools: Tools that are provided by OpenAI that extend the model's capabilities, like web search or file search. Learn more about built-in tools.
Function calls (custom tools): Functions that are defined by you, enabling the model to call your own code. Learn more about function calling.

Show possible types
top_logprobs
integer or null

An integer between 0 and 20 specifying the number of most likely tokens to return at each token position, each with an associated log probability.

top_p
number or null

An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.

We generally recommend altering this or temperature but not both.

truncation
string or null

The truncation strategy to use for the model response.

auto: If the context of this response and previous ones exceeds the model's context window size, the model will truncate the response to fit the context window by dropping input items in the middle of the conversation.
disabled (default): If a model response will exceed the context window size for a model, the request will fail with a 400 error.
usage
object

Represents token usage details including input tokens, output tokens, a breakdown of output tokens, and the total tokens used.

Show properties
user
Deprecated
string

This field is being replaced by safety_identifier and prompt_cache_key. Use prompt_cache_key instead to maintain caching optimizations. A stable identifier for your end-users. Used to boost cache hit rates by better bucketing similar requests and to help OpenAI detect and prevent abuse. Learn more.

OBJECT The response object
{
"id": "resp_67ccd3a9da748190baa7f1570fe91ac604becb25c45c1d41",
"object": "response",
"created_at": 1741476777,
"status": "completed",
"error": null,
"incomplete_details": null,
"instructions": null,
"max_output_tokens": null,
"model": "gpt-4o-2024-08-06",
"output": [
{
"type": "message",
"id": "msg_67ccd3acc8d48190a77525dc6de64b4104becb25c45c1d41",
"status": "completed",
"role": "assistant",
"content": [
{
"type": "output_text",
"text": "The image depicts a scenic landscape with a wooden boardwalk or pathway leading through lush, green grass under a blue sky with some clouds. The setting suggests a peaceful natural area, possibly a park or nature reserve. There are trees and shrubs in the background.",
"annotations": []
}
]
}
],
"parallel_tool_calls": true,
"previous_response_id": null,
"reasoning": {
"effort": null,
"summary": null
},
"store": true,
"temperature": 1,
"text": {
"format": {
"type": "text"
}
},
"tool_choice": "auto",
"tools": [],
"top_p": 1,
"truncation": "disabled",
"usage": {
"input_tokens": 328,
"input_tokens_details": {
"cached_tokens": 0
},
"output_tokens": 52,
"output_tokens_details": {
"reasoning_tokens": 0
},
"total_tokens": 380
},
"user": null,
"metadata": {}
}
The input item list
A list of Response items.

data
array

A list of items used to generate this response.

Show possible types
first_id
string

The ID of the first item in the list.

has_more
boolean

Whether there are more items available.

last_id
string

The ID of the last item in the list.

object
string

The type of object returned, must be list.

OBJECT The input item list
{
"object": "list",
"data": [
{
"id": "msg_abc123",
"type": "message",
"role": "user",
"content": [
{
"type": "input_text",
"text": "Tell me a three sentence bedtime story about a unicorn."
}
]
}
],
"first_id": "msg_abc123",
"last_id": "msg_abc123",
"has_more": false
}
Streaming
When you create a Response with stream set to true, the server will emit server-sent events to the client as the Response is generated. This section contains the events that are emitted by the server.

Learn more about streaming responses.

response.created
An event that is emitted when a response is created.

response
object

The response that was created.

Show properties
sequence_number
integer

The sequence number for this event.

type
string

The type of the event. Always response.created.

OBJECT response.created
{
"type": "response.created",
"response": {
"id": "resp_67ccfcdd16748190a91872c75d38539e09e4d4aac714747c",
"object": "response",
"created_at": 1741487325,
"status": "in_progress",
"error": null,
"incomplete_details": null,
"instructions": null,
"max_output_tokens": null,
"model": "gpt-4o-2024-08-06",
"output": [],
"parallel_tool_calls": true,
"previous_response_id": null,
"reasoning": {
"effort": null,
"summary": null
},
"store": true,
"temperature": 1,
"text": {
"format": {
"type": "text"
}
},
"tool_choice": "auto",
"tools": [],
"top_p": 1,
"truncation": "disabled",
"usage": null,
"user": null,
"metadata": {}
},
"sequence_number": 1
}
response.in_progress
Emitted when the response is in progress.

response
object

The response that is in progress.

Show properties
sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.in_progress.

OBJECT response.in_progress
{
"type": "response.in_progress",
"response": {
"id": "resp_67ccfcdd16748190a91872c75d38539e09e4d4aac714747c",
"object": "response",
"created_at": 1741487325,
"status": "in_progress",
"error": null,
"incomplete_details": null,
"instructions": null,
"max_output_tokens": null,
"model": "gpt-4o-2024-08-06",
"output": [],
"parallel_tool_calls": true,
"previous_response_id": null,
"reasoning": {
"effort": null,
"summary": null
},
"store": true,
"temperature": 1,
"text": {
"format": {
"type": "text"
}
},
"tool_choice": "auto",
"tools": [],
"top_p": 1,
"truncation": "disabled",
"usage": null,
"user": null,
"metadata": {}
},
"sequence_number": 1
}
response.completed
Emitted when the model response is complete.

response
object

Properties of the completed response.

Show properties
sequence_number
integer

The sequence number for this event.

type
string

The type of the event. Always response.completed.

OBJECT response.completed
{
"type": "response.completed",
"response": {
"id": "resp_123",
"object": "response",
"created_at": 1740855869,
"status": "completed",
"error": null,
"incomplete_details": null,
"input": [],
"instructions": null,
"max_output_tokens": null,
"model": "gpt-4o-mini-2024-07-18",
"output": [
{
"id": "msg_123",
"type": "message",
"role": "assistant",
"content": [
{
"type": "output_text",
"text": "In a shimmering forest under a sky full of stars, a lonely unicorn named Lila discovered a hidden pond that glowed with moonlight. Every night, she would leave sparkling, magical flowers by the water's edge, hoping to share her beauty with others. One enchanting evening, she woke to find a group of friendly animals gathered around, eager to be friends and share in her magic.",
"annotations": []
}
]
}
],
"previous_response_id": null,
"reasoning_effort": null,
"store": false,
"temperature": 1,
"text": {
"format": {
"type": "text"
}
},
"tool_choice": "auto",
"tools": [],
"top_p": 1,
"truncation": "disabled",
"usage": {
"input_tokens": 0,
"output_tokens": 0,
"output_tokens_details": {
"reasoning_tokens": 0
},
"total_tokens": 0
},
"user": null,
"metadata": {}
},
"sequence_number": 1
}
response.failed
An event that is emitted when a response fails.

response
object

The response that failed.

Show properties
sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.failed.

OBJECT response.failed
{
"type": "response.failed",
"response": {
"id": "resp_123",
"object": "response",
"created_at": 1740855869,
"status": "failed",
"error": {
"code": "server_error",
"message": "The model failed to generate a response."
},
"incomplete_details": null,
"instructions": null,
"max_output_tokens": null,
"model": "gpt-4o-mini-2024-07-18",
"output": [],
"previous_response_id": null,
"reasoning_effort": null,
"store": false,
"temperature": 1,
"text": {
"format": {
"type": "text"
}
},
"tool_choice": "auto",
"tools": [],
"top_p": 1,
"truncation": "disabled",
"usage": null,
"user": null,
"metadata": {}
}
}
response.incomplete
An event that is emitted when a response finishes as incomplete.

response
object

The response that was incomplete.

Show properties
sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.incomplete.

OBJECT response.incomplete
{
"type": "response.incomplete",
"response": {
"id": "resp_123",
"object": "response",
"created_at": 1740855869,
"status": "incomplete",
"error": null,
"incomplete_details": {
"reason": "max_tokens"
},
"instructions": null,
"max_output_tokens": null,
"model": "gpt-4o-mini-2024-07-18",
"output": [],
"previous_response_id": null,
"reasoning_effort": null,
"store": false,
"temperature": 1,
"text": {
"format": {
"type": "text"
}
},
"tool_choice": "auto",
"tools": [],
"top_p": 1,
"truncation": "disabled",
"usage": null,
"user": null,
"metadata": {}
},
"sequence_number": 1
}
response.output_item.added
Emitted when a new output item is added.

item
object

The output item that was added.

Show possible types
output_index
integer

The index of the output item that was added.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.output_item.added.

OBJECT response.output_item.added
{
"type": "response.output_item.added",
"output_index": 0,
"item": {
"id": "msg_123",
"status": "in_progress",
"type": "message",
"role": "assistant",
"content": []
},
"sequence_number": 1
}
response.output_item.done
Emitted when an output item is marked done.

item
object

The output item that was marked done.

Show possible types
output_index
integer

The index of the output item that was marked done.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.output_item.done.

OBJECT response.output_item.done
{
"type": "response.output_item.done",
"output_index": 0,
"item": {
"id": "msg_123",
"status": "completed",
"type": "message",
"role": "assistant",
"content": [
{
"type": "output_text",
"text": "In a shimmering forest under a sky full of stars, a lonely unicorn named Lila discovered a hidden pond that glowed with moonlight. Every night, she would leave sparkling, magical flowers by the water's edge, hoping to share her beauty with others. One enchanting evening, she woke to find a group of friendly animals gathered around, eager to be friends and share in her magic.",
"annotations": []
}
]
},
"sequence_number": 1
}
response.content_part.added
Emitted when a new content part is added.

content_index
integer

The index of the content part that was added.

item_id
string

The ID of the output item that the content part was added to.

output_index
integer

The index of the output item that the content part was added to.

part
object

The content part that was added.

Show possible types
sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.content_part.added.

OBJECT response.content_part.added
{
"type": "response.content_part.added",
"item_id": "msg_123",
"output_index": 0,
"content_index": 0,
"part": {
"type": "output_text",
"text": "",
"annotations": []
},
"sequence_number": 1
}
response.content_part.done
Emitted when a content part is done.

content_index
integer

The index of the content part that is done.

item_id
string

The ID of the output item that the content part was added to.

output_index
integer

The index of the output item that the content part was added to.

part
object

The content part that is done.

Show possible types
sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.content_part.done.

OBJECT response.content_part.done
{
"type": "response.content_part.done",
"item_id": "msg_123",
"output_index": 0,
"content_index": 0,
"sequence_number": 1,
"part": {
"type": "output_text",
"text": "In a shimmering forest under a sky full of stars, a lonely unicorn named Lila discovered a hidden pond that glowed with moonlight. Every night, she would leave sparkling, magical flowers by the water's edge, hoping to share her beauty with others. One enchanting evening, she woke to find a group of friendly animals gathered around, eager to be friends and share in her magic.",
"annotations": []
}
}
response.output_text.delta
Emitted when there is an additional text delta.

content_index
integer

The index of the content part that the text delta was added to.

delta
string

The text delta that was added.

item_id
string

The ID of the output item that the text delta was added to.

logprobs
array

The log probabilities of the tokens in the delta.

Show properties
output_index
integer

The index of the output item that the text delta was added to.

sequence_number
integer

The sequence number for this event.

type
string

The type of the event. Always response.output_text.delta.

OBJECT response.output_text.delta
{
"type": "response.output_text.delta",
"item_id": "msg_123",
"output_index": 0,
"content_index": 0,
"delta": "In",
"sequence_number": 1
}
response.output_text.done
Emitted when text content is finalized.

content_index
integer

The index of the content part that the text content is finalized.

item_id
string

The ID of the output item that the text content is finalized.

logprobs
array

The log probabilities of the tokens in the delta.

Show properties
output_index
integer

The index of the output item that the text content is finalized.

sequence_number
integer

The sequence number for this event.

text
string

The text content that is finalized.

type
string

The type of the event. Always response.output_text.done.

OBJECT response.output_text.done
{
"type": "response.output_text.done",
"item_id": "msg_123",
"output_index": 0,
"content_index": 0,
"text": "In a shimmering forest under a sky full of stars, a lonely unicorn named Lila discovered a hidden pond that glowed with moonlight. Every night, she would leave sparkling, magical flowers by the water's edge, hoping to share her beauty with others. One enchanting evening, she woke to find a group of friendly animals gathered around, eager to be friends and share in her magic.",
"sequence_number": 1
}
response.refusal.delta
Emitted when there is a partial refusal text.

content_index
integer

The index of the content part that the refusal text is added to.

delta
string

The refusal text that is added.

item_id
string

The ID of the output item that the refusal text is added to.

output_index
integer

The index of the output item that the refusal text is added to.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.refusal.delta.

OBJECT response.refusal.delta
{
"type": "response.refusal.delta",
"item_id": "msg_123",
"output_index": 0,
"content_index": 0,
"delta": "refusal text so far",
"sequence_number": 1
}
response.refusal.done
Emitted when refusal text is finalized.

content_index
integer

The index of the content part that the refusal text is finalized.

item_id
string

The ID of the output item that the refusal text is finalized.

output_index
integer

The index of the output item that the refusal text is finalized.

refusal
string

The refusal text that is finalized.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.refusal.done.

OBJECT response.refusal.done
{
"type": "response.refusal.done",
"item_id": "item-abc",
"output_index": 1,
"content_index": 2,
"refusal": "final refusal text",
"sequence_number": 1
}
response.function_call_arguments.delta
Emitted when there is a partial function-call arguments delta.

delta
string

The function-call arguments delta that is added.

item_id
string

The ID of the output item that the function-call arguments delta is added to.

output_index
integer

The index of the output item that the function-call arguments delta is added to.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.function_call_arguments.delta.

OBJECT response.function_call_arguments.delta
{
"type": "response.function_call_arguments.delta",
"item_id": "item-abc",
"output_index": 0,
"delta": "{ \"arg\":"
"sequence_number": 1
}
response.function_call_arguments.done
Emitted when function-call arguments are finalized.

arguments
string

The function-call arguments.

item_id
string

The ID of the item.

output_index
integer

The index of the output item.

sequence_number
integer

The sequence number of this event.

type
string

OBJECT response.function_call_arguments.done
{
"type": "response.function_call_arguments.done",
"item_id": "item-abc",
"output_index": 1,
"arguments": "{ \"arg\": 123 }",
"sequence_number": 1
}
response.file_search_call.in_progress
Emitted when a file search call is initiated.

item_id
string

The ID of the output item that the file search call is initiated.

output_index
integer

The index of the output item that the file search call is initiated.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.file_search_call.in_progress.

OBJECT response.file_search_call.in_progress
{
"type": "response.file_search_call.in_progress",
"output_index": 0,
"item_id": "fs_123",
"sequence_number": 1
}
response.file_search_call.searching
Emitted when a file search is currently searching.

item_id
string

The ID of the output item that the file search call is initiated.

output_index
integer

The index of the output item that the file search call is searching.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.file_search_call.searching.

OBJECT response.file_search_call.searching
{
"type": "response.file_search_call.searching",
"output_index": 0,
"item_id": "fs_123",
"sequence_number": 1
}
response.file_search_call.completed
Emitted when a file search call is completed (results found).

item_id
string

The ID of the output item that the file search call is initiated.

output_index
integer

The index of the output item that the file search call is initiated.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always response.file_search_call.completed.

OBJECT response.file_search_call.completed
{
"type": "response.file_search_call.completed",
"output_index": 0,
"item_id": "fs_123",
"sequence_number": 1
}
response.web_search_call.in_progress
Emitted when a web search call is initiated.

item_id
string

Unique ID for the output item associated with the web search call.

output_index
integer

The index of the output item that the web search call is associated with.

sequence_number
integer

The sequence number of the web search call being processed.

type
string

The type of the event. Always response.web_search_call.in_progress.

OBJECT response.web_search_call.in_progress
{
"type": "response.web_search_call.in_progress",
"output_index": 0,
"item_id": "ws_123",
"sequence_number": 0
}
response.web_search_call.searching
Emitted when a web search call is executing.

item_id
string

Unique ID for the output item associated with the web search call.

output_index
integer

The index of the output item that the web search call is associated with.

sequence_number
integer

The sequence number of the web search call being processed.

type
string

The type of the event. Always response.web_search_call.searching.

OBJECT response.web_search_call.searching
{
"type": "response.web_search_call.searching",
"output_index": 0,
"item_id": "ws_123",
"sequence_number": 0
}
response.web_search_call.completed
Emitted when a web search call is completed.

item_id
string

Unique ID for the output item associated with the web search call.

output_index
integer

The index of the output item that the web search call is associated with.

sequence_number
integer

The sequence number of the web search call being processed.

type
string

The type of the event. Always response.web_search_call.completed.

OBJECT response.web_search_call.completed
{
"type": "response.web_search_call.completed",
"output_index": 0,
"item_id": "ws_123",
"sequence_number": 0
}
response.reasoning_summary_part.added
Emitted when a new reasoning summary part is added.

item_id
string

The ID of the item this summary part is associated with.

output_index
integer

The index of the output item this summary part is associated with.

part
object

The summary part that was added.

Show properties
sequence_number
integer

The sequence number of this event.

summary_index
integer

The index of the summary part within the reasoning summary.

type
string

The type of the event. Always response.reasoning_summary_part.added.

OBJECT response.reasoning_summary_part.added
{
"type": "response.reasoning_summary_part.added",
"item_id": "rs_6806bfca0b2481918a5748308061a2600d3ce51bdffd5476",
"output_index": 0,
"summary_index": 0,
"part": {
"type": "summary_text",
"text": ""
},
"sequence_number": 1
}
response.reasoning_summary_part.done
Emitted when a reasoning summary part is completed.

item_id
string

The ID of the item this summary part is associated with.

output_index
integer

The index of the output item this summary part is associated with.

part
object

The completed summary part.

Show properties
sequence_number
integer

The sequence number of this event.

summary_index
integer

The index of the summary part within the reasoning summary.

type
string

The type of the event. Always response.reasoning_summary_part.done.

OBJECT response.reasoning_summary_part.done
{
"type": "response.reasoning_summary_part.done",
"item_id": "rs_6806bfca0b2481918a5748308061a2600d3ce51bdffd5476",
"output_index": 0,
"summary_index": 0,
"part": {
"type": "summary_text",
"text": "**Responding to a greeting**\n\nThe user just said, \"Hello!\" So, it seems I need to engage. I'll greet them back and offer help since they're looking to chat. I could say something like, \"Hello! How can I assist you today?\" That feels friendly and open. They didn't ask a specific question, so this approach will work well for starting a conversation. Let's see where it goes from there!"
},
"sequence_number": 1
}
response.reasoning_summary_text.delta
Emitted when a delta is added to a reasoning summary text.

delta
string

The text delta that was added to the summary.

item_id
string

The ID of the item this summary text delta is associated with.

output_index
integer

The index of the output item this summary text delta is associated with.

sequence_number
integer

The sequence number of this event.

summary_index
integer

The index of the summary part within the reasoning summary.

type
string

The type of the event. Always response.reasoning_summary_text.delta.

OBJECT response.reasoning_summary_text.delta
{
"type": "response.reasoning_summary_text.delta",
"item_id": "rs_6806bfca0b2481918a5748308061a2600d3ce51bdffd5476",
"output_index": 0,
"summary_index": 0,
"delta": "**Responding to a greeting**\n\nThe user just said, \"Hello!\" So, it seems I need to engage. I'll greet them back and offer help since they're looking to chat. I could say something like, \"Hello! How can I assist you today?\" That feels friendly and open. They didn't ask a specific question, so this approach will work well for starting a conversation. Let's see where it goes from there!",
"sequence_number": 1
}
response.reasoning_summary_text.done
Emitted when a reasoning summary text is completed.

item_id
string

The ID of the item this summary text is associated with.

output_index
integer

The index of the output item this summary text is associated with.

sequence_number
integer

The sequence number of this event.

summary_index
integer

The index of the summary part within the reasoning summary.

text
string

The full text of the completed reasoning summary.

type
string

The type of the event. Always response.reasoning_summary_text.done.

OBJECT response.reasoning_summary_text.done
{
"type": "response.reasoning_summary_text.done",
"item_id": "rs_6806bfca0b2481918a5748308061a2600d3ce51bdffd5476",
"output_index": 0,
"summary_index": 0,
"text": "**Responding to a greeting**\n\nThe user just said, \"Hello!\" So, it seems I need to engage. I'll greet them back and offer help since they're looking to chat. I could say something like, \"Hello! How can I assist you today?\" That feels friendly and open. They didn't ask a specific question, so this approach will work well for starting a conversation. Let's see where it goes from there!",
"sequence_number": 1
}
response.image_generation_call.completed
Emitted when an image generation tool call has completed and the final image is available.

item_id
string

The unique identifier of the image generation item being processed.

output_index
integer

The index of the output item in the response's output array.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.image_generation_call.completed'.

OBJECT response.image_generation_call.completed
{
"type": "response.image_generation_call.completed",
"output_index": 0,
"item_id": "item-123",
"sequence_number": 1
}
response.image_generation_call.generating
Emitted when an image generation tool call is actively generating an image (intermediate state).

item_id
string

The unique identifier of the image generation item being processed.

output_index
integer

The index of the output item in the response's output array.

sequence_number
integer

The sequence number of the image generation item being processed.

type
string

The type of the event. Always 'response.image_generation_call.generating'.

OBJECT response.image_generation_call.generating
{
"type": "response.image_generation_call.generating",
"output_index": 0,
"item_id": "item-123",
"sequence_number": 0
}
response.image_generation_call.in_progress
Emitted when an image generation tool call is in progress.

item_id
string

The unique identifier of the image generation item being processed.

output_index
integer

The index of the output item in the response's output array.

sequence_number
integer

The sequence number of the image generation item being processed.

type
string

The type of the event. Always 'response.image_generation_call.in_progress'.

OBJECT response.image_generation_call.in_progress
{
"type": "response.image_generation_call.in_progress",
"output_index": 0,
"item_id": "item-123",
"sequence_number": 0
}
response.image_generation_call.partial_image
Emitted when a partial image is available during image generation streaming.

item_id
string

The unique identifier of the image generation item being processed.

output_index
integer

The index of the output item in the response's output array.

partial_image_b64
string

Base64-encoded partial image data, suitable for rendering as an image.

partial_image_index
integer

0-based index for the partial image (backend is 1-based, but this is 0-based for the user).

sequence_number
integer

The sequence number of the image generation item being processed.

type
string

The type of the event. Always 'response.image_generation_call.partial_image'.

OBJECT response.image_generation_call.partial_image
{
"type": "response.image_generation_call.partial_image",
"output_index": 0,
"item_id": "item-123",
"sequence_number": 0,
"partial_image_index": 0,
"partial_image_b64": "..."
}
response.mcp_call_arguments.delta
Emitted when there is a delta (partial update) to the arguments of an MCP tool call.

delta
string

A JSON string containing the partial update to the arguments for the MCP tool call.

item_id
string

The unique identifier of the MCP tool call item being processed.

output_index
integer

The index of the output item in the response's output array.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.mcp_call_arguments.delta'.

OBJECT response.mcp_call_arguments.delta
{
"type": "response.mcp_call_arguments.delta",
"output_index": 0,
"item_id": "item-abc",
"delta": "{",
"sequence_number": 1
}
response.mcp_call_arguments.done
Emitted when the arguments for an MCP tool call are finalized.

arguments
string

A JSON string containing the finalized arguments for the MCP tool call.

item_id
string

The unique identifier of the MCP tool call item being processed.

output_index
integer

The index of the output item in the response's output array.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.mcp_call_arguments.done'.

OBJECT response.mcp_call_arguments.done
{
"type": "response.mcp_call_arguments.done",
"output_index": 0,
"item_id": "item-abc",
"arguments": "{\"arg1\": \"value1\", \"arg2\": \"value2\"}",
"sequence_number": 1
}
response.mcp_call.completed
Emitted when an MCP tool call has completed successfully.

item_id
string

The ID of the MCP tool call item that completed.

output_index
integer

The index of the output item that completed.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.mcp_call.completed'.

OBJECT response.mcp_call.completed
{
"type": "response.mcp_call.completed",
"sequence_number": 1,
"item_id": "mcp_682d437d90a88191bf88cd03aae0c3e503937d5f622d7a90",
"output_index": 0
}
response.mcp_call.failed
Emitted when an MCP tool call has failed.

item_id
string

The ID of the MCP tool call item that failed.

output_index
integer

The index of the output item that failed.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.mcp_call.failed'.

OBJECT response.mcp_call.failed
{
"type": "response.mcp_call.failed",
"sequence_number": 1,
"item_id": "mcp_682d437d90a88191bf88cd03aae0c3e503937d5f622d7a90",
"output_index": 0
}
response.mcp_call.in_progress
Emitted when an MCP tool call is in progress.

item_id
string

The unique identifier of the MCP tool call item being processed.

output_index
integer

The index of the output item in the response's output array.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.mcp_call.in_progress'.

OBJECT response.mcp_call.in_progress
{
"type": "response.mcp_call.in_progress",
"sequence_number": 1,
"output_index": 0,
"item_id": "mcp_682d437d90a88191bf88cd03aae0c3e503937d5f622d7a90"
}
response.mcp_list_tools.completed
Emitted when the list of available MCP tools has been successfully retrieved.

item_id
string

The ID of the MCP tool call item that produced this output.

output_index
integer

The index of the output item that was processed.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.mcp_list_tools.completed'.

OBJECT response.mcp_list_tools.completed
{
"type": "response.mcp_list_tools.completed",
"sequence_number": 1,
"output_index": 0,
"item_id": "mcpl_682d4379df088191886b70f4ec39f90403937d5f622d7a90"
}
response.mcp_list_tools.failed
Emitted when the attempt to list available MCP tools has failed.

item_id
string

The ID of the MCP tool call item that failed.

output_index
integer

The index of the output item that failed.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.mcp_list_tools.failed'.

OBJECT response.mcp_list_tools.failed
{
"type": "response.mcp_list_tools.failed",
"sequence_number": 1,
"output_index": 0,
"item_id": "mcpl_682d4379df088191886b70f4ec39f90403937d5f622d7a90"
}
response.mcp_list_tools.in_progress
Emitted when the system is in the process of retrieving the list of available MCP tools.

item_id
string

The ID of the MCP tool call item that is being processed.

output_index
integer

The index of the output item that is being processed.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.mcp_list_tools.in_progress'.

OBJECT response.mcp_list_tools.in_progress
{
"type": "response.mcp_list_tools.in_progress",
"sequence_number": 1,
"output_index": 0,
"item_id": "mcpl_682d4379df088191886b70f4ec39f90403937d5f622d7a90"
}
response.code_interpreter_call.in_progress
Emitted when a code interpreter call is in progress.

item_id
string

The unique identifier of the code interpreter tool call item.

output_index
integer

The index of the output item in the response for which the code interpreter call is in progress.

sequence_number
integer

The sequence number of this event, used to order streaming events.

type
string

The type of the event. Always response.code_interpreter_call.in_progress.

OBJECT response.code_interpreter_call.in_progress
{
"type": "response.code_interpreter_call.in_progress",
"output_index": 0,
"item_id": "ci_12345",
"sequence_number": 1
}
response.code_interpreter_call.interpreting
Emitted when the code interpreter is actively interpreting the code snippet.

item_id
string

The unique identifier of the code interpreter tool call item.

output_index
integer

The index of the output item in the response for which the code interpreter is interpreting code.

sequence_number
integer

The sequence number of this event, used to order streaming events.

type
string

The type of the event. Always response.code_interpreter_call.interpreting.

OBJECT response.code_interpreter_call.interpreting
{
"type": "response.code_interpreter_call.interpreting",
"output_index": 4,
"item_id": "ci_12345",
"sequence_number": 1
}
response.code_interpreter_call.completed
Emitted when the code interpreter call is completed.

item_id
string

The unique identifier of the code interpreter tool call item.

output_index
integer

The index of the output item in the response for which the code interpreter call is completed.

sequence_number
integer

The sequence number of this event, used to order streaming events.

type
string

The type of the event. Always response.code_interpreter_call.completed.

OBJECT response.code_interpreter_call.completed
{
"type": "response.code_interpreter_call.completed",
"output_index": 5,
"item_id": "ci_12345",
"sequence_number": 1
}
response.code_interpreter_call_code.delta
Emitted when a partial code snippet is streamed by the code interpreter.

delta
string

The partial code snippet being streamed by the code interpreter.

item_id
string

The unique identifier of the code interpreter tool call item.

output_index
integer

The index of the output item in the response for which the code is being streamed.

sequence_number
integer

The sequence number of this event, used to order streaming events.

type
string

The type of the event. Always response.code_interpreter_call_code.delta.

OBJECT response.code_interpreter_call_code.delta
{
"type": "response.code_interpreter_call_code.delta",
"output_index": 0,
"item_id": "ci_12345",
"delta": "print('Hello, world')",
"sequence_number": 1
}
response.code_interpreter_call_code.done
Emitted when the code snippet is finalized by the code interpreter.

code
string

The final code snippet output by the code interpreter.

item_id
string

The unique identifier of the code interpreter tool call item.

output_index
integer

The index of the output item in the response for which the code is finalized.

sequence_number
integer

The sequence number of this event, used to order streaming events.

type
string

The type of the event. Always response.code_interpreter_call_code.done.

OBJECT response.code_interpreter_call_code.done
{
"type": "response.code_interpreter_call_code.done",
"output_index": 3,
"item_id": "ci_12345",
"code": "print('done')",
"sequence_number": 1
}
response.output_text.annotation.added
Emitted when an annotation is added to output text content.

annotation
object

The annotation object being added. (See annotation schema for details.)

annotation_index
integer

The index of the annotation within the content part.

content_index
integer

The index of the content part within the output item.

item_id
string

The unique identifier of the item to which the annotation is being added.

output_index
integer

The index of the output item in the response's output array.

sequence_number
integer

The sequence number of this event.

type
string

The type of the event. Always 'response.output_text.annotation.added'.

OBJECT response.output_text.annotation.added
{
"type": "response.output_text.annotation.added",
"item_id": "item-abc",
"output_index": 0,
"content_index": 0,
"annotation_index": 0,
"annotation": {
"type": "text_annotation",
"text": "This is a test annotation",
"start": 0,
"end": 10
},
"sequence_number": 1
}
response.queued
Emitted when a response is queued and waiting to be processed.

response
object

The full response object that is queued.

Show properties
sequence_number
integer

The sequence number for this event.

type
string

The type of the event. Always 'response.queued'.

OBJECT response.queued
{
"type": "response.queued",
"response": {
"id": "res_123",
"status": "queued",
"created_at": "2021-01-01T00:00:00Z",
"updated_at": "2021-01-01T00:00:00Z"
},
"sequence_number": 1
}
response.reasoning_summary.delta
Emitted when there is a delta (partial update) to the reasoning summary content.

delta
object

The partial update to the reasoning summary content.

item_id
string

The unique identifier of the item for which the reasoning summary is being updated.

output_index
integer

The index of the output item in the response's output array.

sequence_number
integer

The sequence number of this event.

summary_index
integer

The index of the summary part within the output item.

type
string

The type of the event. Always 'response.reasoning_summary.delta'.

OBJECT response.reasoning_summary.delta
{
"type": "response.reasoning_summary.delta",
"item_id": "item-abc",
"output_index": 0,
"summary_index": 0,
"delta": {
"text": "delta text"
},
"sequence_number": 1
}
response.reasoning_summary.done
Emitted when the reasoning summary content is finalized for an item.

item_id
string

The unique identifier of the item for which the reasoning summary is finalized.

output_index
integer

The index of the output item in the response's output array.

sequence_number
integer

The sequence number of this event.

summary_index
integer

The index of the summary part within the output item.

text
string

The finalized reasoning summary text.

type
string

The type of the event. Always 'response.reasoning_summary.done'.
