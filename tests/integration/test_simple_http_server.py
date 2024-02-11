import asyncio
import logging
import os
import threading
import urllib.request
import uuid

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.skipif("SKIP_LOAD_TEST" in os.environ and os.environ["SKIP_LOAD_TEST"] == "true",
                    reason="Skipping test in CI due to heavy load")
@pytest.mark.parametrize("concurrent_calls", [5000])
@pytest.mark.asyncio
async def test_simple_http_server_load_with_async_calls(
    simple_http_server, concurrent_calls
):
    logger.info("Inside the test")
    expected_responses = {}  # Dictionary to store expected responses with identifiers

    # Send concurrent requests using asyncio.gather, each call having a unique UUID
    tasks = []
    for _ in range(concurrent_calls):
        identifier = uuid.uuid4()
        tasks.append(send_request_and_collect_response(identifier))

    responses = await asyncio.gather(*tasks)

    # Update expected_responses dictionary with the collected responses
    for identifier, response in responses:
        expected_responses[identifier] = response

    # Perform assertions to ensure each client received the correct response
    for identifier, expected_response in expected_responses.items():
        # Assert that the received response contains the UUID
        assert (
            str(identifier) in expected_response
        ), f"UUID mismatch for identifier {identifier}"


@pytest.mark.skipif("SKIP_LOAD_TEST" in os.environ and os.environ["SKIP_LOAD_TEST"] == "true",
                    reason="Skipping test in CI due to heavy load")
@pytest.mark.parametrize("num_connections", [2])
def test_simple_http_server_load_with_sync_calls(simple_http_server, num_connections):
    logger.info("Inside the test")
    expected_responses = {}  # Dictionary to store expected responses with identifiers

    # Send concurrent requests using threading, each call having a unique UUID
    threads = []
    for _ in range(num_connections):
        identifier = uuid.uuid4()
        thread = threading.Thread(
            target=send_request_and_collect_response_sync,
            args=(identifier, expected_responses),
        )
        thread.start()
        threads.append(thread)

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Perform assertions to ensure each client received the correct response
    for identifier, expected_response in expected_responses.items():
        # Assert that the received response contains the UUID
        assert (
            str(identifier) in expected_response
        ), f"UUID mismatch for identifier {identifier}"


async def send_request_and_collect_response(identifier):
    url = "http://localhost:9999"
    headers = {"X-UUID": str(identifier)}  # Include the UUID in the request headers

    with urllib.request.urlopen(
        urllib.request.Request(url, headers=headers)
    ) as response:
        # Collect and return the response along with the identifier and response UUID
        response_data = response.read().decode("utf-8")
        print(f"Received response for identifier {identifier}: {response_data}")
        return identifier, response_data


def send_request_and_collect_response_sync(identifier, expected_responses):
    url = "http://localhost:9999"
    headers = {"X-UUID": str(identifier)}  # Include the UUID in the request headers

    # Send a simple HTTP GET request
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)

    # Collect and store the response along with the identifier
    response_data = response.read().decode("utf-8")
    print(f"Received response for identifier {identifier}: {response_data}")
    expected_responses[identifier] = response_data
