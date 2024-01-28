import asyncio
import urllib.request
import uuid


async def send_request_and_collect_response(identifier):
    url = 'http://localhost:9999'
    headers = {'X-UUID': str(identifier)}  # Include the UUID in the request headers

    with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as response:
        # Collect and return the response along with the identifier and response UUID
        response_data = response.read().decode('utf-8')
        print(f"Received response for identifier {identifier}: {response_data}")
        return identifier, response_data


async def main():
    identifiers = [uuid.uuid4() for _ in range(5000)]
    expected_responses = {}  # Dictionary to store expected responses with identifiers

    # Send concurrent requests using asyncio.gather
    tasks = [send_request_and_collect_response(identifier) for identifier in identifiers]
    responses = await asyncio.gather(*tasks)

    # Update expected_responses dictionary with the collected responses
    print(responses)
    for identifier, response in responses:
        expected_responses[identifier] = response

    # Perform assertions to ensure each client received the correct response
    for identifier, expected_response in expected_responses.items():
        # Assert that the received response contains the UUID
        assert str(identifier) in expected_response, f"UUID mismatch for identifier {identifier}"

asyncio.run(main())
