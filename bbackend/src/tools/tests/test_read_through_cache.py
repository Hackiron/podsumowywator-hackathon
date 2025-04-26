import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta

from src.tools.read_through_cache import ReadThroughCache


class TestReadThroughCache:
    """Test cases for the ReadThroughCache class."""

    @patch("requests.get")
    def test_load_calls_api(self, mock_get):
        """Test that load method calls the API with correct parameters."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"username": "TestUser1", "message": "Test message 1", "images": []},
            {"username": "TestUser2", "message": "Test message 2", "images": []},
        ]
        mock_get.return_value = mock_response

        # Create cache and call load
        cache = ReadThroughCache()
        channel_id = "test-channel"
        start_date = "2023-01-01T00:00:00.000Z"
        end_date = "2023-01-10T00:00:00.000Z"

        messages = cache.load(channel_id, start_date, end_date)

        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        # Extract the call arguments
        args, kwargs = mock_get.call_args

        # Check the URL params contain the expected values
        assert kwargs["params"]["channelId"] == channel_id
        assert kwargs["params"]["startDate"] == start_date
        assert kwargs["params"]["endDate"] == end_date

        # Verify response was processed correctly
        assert len(messages) == 2
        assert messages[0].username == "TestUser1"
        assert messages[0].message == "Test message 1"
        assert messages[1].username == "TestUser2"
        assert messages[1].message == "Test message 2"

    @patch("requests.get")
    def test_no_api_call_for_cached_data(self, mock_get):
        """Test that API is not called a second time for the same parameters."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"username": "TestUser1", "message": "Test message 1", "images": []},
            {"username": "TestUser2", "message": "Test message 2", "images": []},
        ]
        mock_get.return_value = mock_response

        # Create cache
        cache = ReadThroughCache()
        channel_id = "test-channel"
        start_date = "2023-01-01T00:00:00.000Z"
        end_date = "2023-01-10T00:00:00.000Z"

        # First call should hit the API
        first_messages = cache.load(channel_id, start_date, end_date)

        # Second call with same parameters should use cache
        second_messages = cache.load(channel_id, start_date, end_date)

        # Verify the API was called exactly once
        mock_get.assert_called_once()

        # Verify both responses have the same data
        assert len(first_messages) == len(second_messages)
        assert first_messages[0].username == second_messages[0].username
        assert first_messages[0].message == second_messages[0].message
        assert first_messages[1].username == second_messages[1].username
        assert first_messages[1].message == second_messages[1].message

    @patch("requests.get")
    def test_partial_cache_hit(self, mock_get):
        """Test that only missing date ranges are requested when there's a partial overlap."""
        # Setup initial cache with data for 2025-04-03 to 2025-04-06
        mock_response1 = MagicMock()
        mock_response1.json.return_value = [
            {"username": "User1", "message": "Cached message 1", "images": []},
            {"username": "User2", "message": "Cached message 2", "images": []},
        ]

        # Setup response for missing range (2025-04-01 to 2025-04-03)
        mock_response2 = MagicMock()
        mock_response2.json.return_value = [
            {"username": "User3", "message": "New message 1", "images": []},
            {"username": "User4", "message": "New message 2", "images": []},
        ]

        # The mock will return different responses for different calls
        mock_get.side_effect = [mock_response1, mock_response2]

        # Create cache and populate with initial data
        cache = ReadThroughCache()
        channel_id = "test-channel"

        # First, load data for 2025-04-03 to 2025-04-06
        cache_start = "2025-04-03T00:00:00.000Z"
        cache_end = "2025-04-06T00:00:00.000Z"
        cache.load(channel_id, cache_start, cache_end)

        # Reset the mock to clear the call history
        mock_get.reset_mock()

        # Now request a range that partially overlaps (2025-04-01 to 2025-04-05)
        request_start = "2025-04-01T00:00:00.000Z"
        request_end = "2025-04-05T00:00:00.000Z"
        messages = cache.load(channel_id, request_start, request_end)

        # Verify API was called only for the missing range
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args

        # The API should be called with the missing range parameters
        assert kwargs["params"]["channelId"] == channel_id
        assert kwargs["params"]["startDate"] == request_start
        assert kwargs["params"]["endDate"] == cache_start

        # Verify we got 4 messages (2 from cache + 2 from API)
        assert len(messages) == 4

        # Check if the messages from both ranges are present
        message_texts = [msg.message for msg in messages]
        assert "New message 1" in message_texts
        assert "New message 2" in message_texts
        assert "Cached message 1" in message_texts
        assert "Cached message 2" in message_texts 

    @patch("requests.get")
    def test_cache_optimization(self, mock_get):
        """Test that cache gets optimized by merging touching/overlapping ranges."""
        # Setup responses for initial ranges
        mock_response1 = MagicMock()
        mock_response1.json.return_value = [
            {"username": "User1", "message": "Range 1 message 1", "images": []},
            {"username": "User2", "message": "Range 1 message 2", "images": []},
        ]

        mock_response2 = MagicMock()
        mock_response2.json.return_value = [
            {"username": "User3", "message": "Range 2 message 1", "images": []},
            {"username": "User4", "message": "Range 2 message 2", "images": []},
        ]

        mock_response3 = MagicMock()
        mock_response3.json.return_value = [
            {"username": "User5", "message": "Overlapping message 1", "images": []},
            {"username": "User6", "message": "Overlapping message 2", "images": []},
        ]

        mock_get.side_effect = [mock_response1]

        cache = ReadThroughCache()
        channel_id = "test-channel"

        # Load first range and verify count
        first_messages = cache.load(
            channel_id, "2025-04-01T00:00:00.000Z", "2025-04-03T00:00:00.000Z"
        )
        assert len(first_messages) == 2
        assert len(cache.cache[channel_id][0].messages) == 2  # Verify cache content

        mock_get.side_effect = [mock_response2]

        # Load second range and verify count
        second_messages = cache.load(
            channel_id, "2025-04-06T00:00:00.000Z", "2025-04-10T00:00:00.000Z"
        )
        assert len(second_messages) == 2
        assert len(cache.cache[channel_id]) == 2
        assert (
            sum(len(entry.messages) for entry in cache.cache[channel_id]) == 4
        )  # Total cached messages

        mock_get.side_effect = [mock_response3]

        # Load overlapping range and verify final merged state
        third_messages = cache.load(
            channel_id, "2025-04-02T00:00:00.000Z", "2025-04-07T00:00:00.000Z"
        )

        # Verify cache optimization resulted in a single range with all messages
        assert len(cache.cache[channel_id]) == 1
        cached_entry = cache.cache[channel_id][0]
        assert cached_entry.range.start == "2025-04-01T00:00:00.000Z"
        assert cached_entry.range.end == "2025-04-10T00:00:00.000Z"

        # Verify all messages are preserved in the merged range
        all_messages = cached_entry.messages

        # Verify message order (from oldest to newest based on range order)
        expected_order = [
            ("User1", "Range 1 message 1"),      # From first range (oldest)
            ("User2", "Range 1 message 2"),
            ("User5", "Overlapping message 1"),  # From overlapping range
            ("User6", "Overlapping message 2"),
            ("User3", "Range 2 message 1"),      # From second range (newest)
            ("User4", "Range 2 message 2"),
        ]
        
        for i, (exp_user, exp_msg) in enumerate(expected_order):
            assert all_messages[i].username == exp_user, f"Wrong message order at position {i}"
            assert all_messages[i].message == exp_msg, f"Wrong message order at position {i}"
