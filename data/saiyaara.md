from openai import OpenAI

client = OpenAI()

response = client.responses.create(
model="gpt-4.1",
input="Tell me a three sentence bedtime story about a unicorn."
)

print(response)

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
from openai import OpenAI

client = OpenAI()

response = client.responses.create(
model="gpt-4.1",
input="Tell me a three sentence bedtime story about a unicorn."
)

print(response)
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
from openai import OpenAI
client = OpenAI()

response = client.responses.retrieve("resp_123")
print(response)
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
from openai import OpenAI
client = OpenAI()

response = client.responses.delete("resp_123")
print(response)
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
from openai import OpenAI
client = OpenAI()

response = client.responses.cancel("resp_123")
print(response)
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
from openai import OpenAI
client = OpenAI()

response = client.responses.input_items.list("resp_123")
print(response.data)
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
