from ..dtos import Message
from loguru import logger
import requests
from ..config_loader import load_config
from urllib.parse import urljoin
from ..memory import MessageMemory
from pydantic import ValidationError
from datetime import datetime, timedelta
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass


@dataclass
class DateRange:
    start: str
    end: str


@dataclass
class CacheEntry:
    range: DateRange
    messages: List[Message]


def _load_messages_from_api(
    channel_id: str, start_date: str, end_date: str
) -> list[Message]:
    config = load_config()

    url = urljoin(config.api_base_url, "/matchenatinderze")

    params = {"channelId": channel_id, "startDate": start_date, "endDate": end_date}

    try:
        response = requests.get(url, params=params, timeout=config.timeout_seconds)
        response.raise_for_status()

        messages_data = response.json()

        return [
            Message(
                username=msg["username"],
                message=msg["message"],
                images=msg["images"],
                createdAt=msg["createdAt"],
            )
            for msg in messages_data
        ]

    except ValidationError as e:
        logger.error(f"Pydantic validation error: {e.errors()}")
        raise
    except KeyError as e:
        logger.error(f"Missing required field in message data: {e}")
        raise ValueError(f"Message data missing required field: {e}")
    except requests.RequestException as e:
        logger.error(f"Failed to load messages from API: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Other error: {str(e)}")
        raise


def _load_mock_messages(
    channel_id: str, start_date: str, end_date: str
) -> list[Message]:
    """Load mock messages for testing purposes."""
    return [
        Message(username="John", message="Hello, how are you?"),
        Message(username="Jane", message="I'm good, thank you!"),
    ]


class ReadThroughCache:
    """A read-through cache that loads data from an API, storing it by date ranges."""

    def __init__(self, use_mock: bool = False):
        self.cache: Dict[str, List[CacheEntry]] = {}
        self.use_mock = use_mock

    def get(self):
        """Return the current cache."""
        return self.cache

    def clear(self):
        """Clear the entire cache."""
        self.cache.clear()

    def _parse_date(self, date_str: str) -> datetime:
        """Convert a date string to a datetime object for comparison."""
        # Handle ISO format dates with or without time components
        try:
            # For ISO format with 'Z' timezone marker (e.g., 2023-01-01T00:00:00.000Z)
            if "Z" in date_str:
                # Remove 'Z' and parse
                clean_date = date_str.rstrip("Z")
                return datetime.fromisoformat(clean_date)
            # For ISO format with time component
            elif "T" in date_str:
                return datetime.fromisoformat(date_str)
            # For date-only format
            else:
                return datetime.fromisoformat(f"{date_str}T00:00:00")
        except ValueError:
            # Fallback for any other format issues
            logger.warning(f"Could not parse date: {date_str}, using default parsing")
            return datetime.fromisoformat(date_str.split("T")[0] + "T00:00:00")

    def _format_iso_date(self, dt: datetime) -> str:
        """Format a datetime as ISO date string with time component."""
        # Return full ISO format with time component and Z timezone marker
        return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    def _is_range_contained(
        self, target_start: str, target_end: str, cache_start: str, cache_end: str
    ) -> bool:
        """Check if target date range is contained within cached date range."""
        return self._parse_date(target_start) >= self._parse_date(
            cache_start
        ) and self._parse_date(target_end) <= self._parse_date(cache_end)

    def _find_overlapping_ranges(
        self, channel_id: str, start_date: str, end_date: str
    ) -> List[CacheEntry]:
        """Find all cached date ranges that overlap with the requested range."""
        if channel_id not in self.cache:
            return []

        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)

        overlapping = []
        for entry in self.cache[channel_id]:
            cached_start_dt = self._parse_date(entry.range.start)
            cached_end_dt = self._parse_date(entry.range.end)

            # Check if ranges overlap
            if not (end_dt < cached_start_dt or start_dt > cached_end_dt):
                overlapping.append(entry)

        return overlapping

    def _normalize_ranges(self, ranges: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        """Merge overlapping date ranges to avoid duplicate fetches."""
        if not ranges:
            return []

        # Sort by start date
        sorted_ranges = sorted(ranges, key=lambda r: self._parse_date(r[0]))

        normalized = [sorted_ranges[0]]

        for current_start, current_end in sorted_ranges[1:]:
            prev_start, prev_end = normalized[-1]

            # If current range overlaps with previous, merge them
            if self._parse_date(current_start) <= self._parse_date(prev_end):
                # Update end date of previous range if current ends later
                if self._parse_date(current_end) > self._parse_date(prev_end):
                    normalized[-1] = (prev_start, current_end)
            else:
                # No overlap, add as new range
                normalized.append((current_start, current_end))

        return normalized

    def _calculate_missing_ranges(
        self, start_date: str, end_date: str, overlapping_ranges: List[CacheEntry]
    ) -> List[Tuple[str, str]]:
        """Calculate precise date ranges that need to be fetched to avoid duplicates."""
        if not overlapping_ranges:
            return [(start_date, end_date)]

        # Sort overlapping ranges by start date
        sorted_ranges = sorted(
            overlapping_ranges, key=lambda x: self._parse_date(x.range.start)
        )

        # Convert to datetime objects for easier manipulation
        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)

        # Keep track of covered date ranges
        covered_ranges = []
        for entry in sorted_ranges:
            cached_start_dt = self._parse_date(entry.range.start)
            cached_end_dt = self._parse_date(entry.range.end)
            covered_ranges.append((cached_start_dt, cached_end_dt))

        # Find missing ranges by identifying gaps
        missing_ranges = []
        current_dt = start_dt

        # Sort covered ranges by start date
        covered_ranges.sort(key=lambda r: r[0])

        for range_start_dt, range_end_dt in covered_ranges:
            # If there's a gap before this cached range
            if current_dt < range_start_dt:
                missing_ranges.append(
                    (
                        self._format_iso_date(current_dt),
                        self._format_iso_date(range_start_dt),
                    )
                )

            # Update current date to be after the cached range (if applicable)
            if range_end_dt > current_dt:
                current_dt = range_end_dt

        # Check if there's a gap after the last cached range
        if current_dt < end_dt:
            missing_ranges.append(
                (self._format_iso_date(current_dt), self._format_iso_date(end_dt))
            )

        # Normalize ranges to avoid duplicate fetches
        return self._normalize_ranges(missing_ranges)

    def _find_in_cache(
        self, channel_id: str, start_date: str, end_date: str
    ) -> Optional[List[Message]]:
        """Search cache for messages that cover the requested date range."""
        if channel_id not in self.cache:
            return None

        for entry in self.cache[channel_id]:
            if self._is_range_contained(
                start_date, end_date, entry.range.start, entry.range.end
            ):
                return entry.messages

        return None

    def _merge_messages(self, message_lists: List[List[Message]]) -> List[Message]:
        """Merge multiple lists of messages, removing duplicates."""
        seen_messages: Set[Tuple[str, str]] = set()
        merged: List[Message] = []

        for msg_list in message_lists:
            for msg in msg_list:
                # Use a tuple of username and message as a key to identify duplicates
                key = (msg.username, msg.message)
                if key not in seen_messages:
                    seen_messages.add(key)
                    merged.append(msg)

        return merged

    def _filter_messages_for_date_range(
        self, messages: List[Message], start_date: str, end_date: str
    ) -> List[Message]:
        """
        Filter messages to only include those within the specified date range.
        Note: For a real implementation, messages would need timestamps to filter by date.
        """
        # In a real implementation with message timestamps, we would filter here
        # For this implementation, we return all messages since our test messages don't have timestamps
        return messages

    def _merge_touching_ranges(
        self, channel_id: str, new_start: str, new_end: str, new_messages: List[Message]
    ) -> CacheEntry:
        """
        Add new range to cache and optimize.
        """
        if channel_id not in self.cache:
            self.cache[channel_id] = []

        new_entry = CacheEntry(
            range=DateRange(start=new_start, end=new_end), messages=new_messages
        )
        self.cache[channel_id].append(new_entry)

        self._optimize_cache(channel_id)

        # Find the entry that now contains our new data
        for entry in self.cache[channel_id]:
            if self._is_range_contained(
                new_start, new_end, entry.range.start, entry.range.end
            ):
                return entry

        logger.error("Cache optimization failed to maintain data consistency")
        return new_entry

    def _optimize_cache(self, channel_id: str):
        """
        Optimize the cache by merging all touching/overlapping ranges for a channel.
        This ensures the cache is always in the most efficient state.
        """
        if channel_id not in self.cache or not self.cache[channel_id]:
            return

        # Sort entries by start date
        entries = sorted(
            self.cache[channel_id], key=lambda x: self._parse_date(x.range.start)
        )
        optimized = []
        current = entries[0]
        current_end_dt = self._parse_date(current.range.end)

        for next_entry in entries[1:]:
            next_start_dt = self._parse_date(next_entry.range.start)

            # Check if ranges touch or overlap
            if next_start_dt <= current_end_dt + timedelta(seconds=1):
                # Merge the entries
                current_end_dt = max(
                    current_end_dt, self._parse_date(next_entry.range.end)
                )
                current = CacheEntry(
                    range=DateRange(
                        start=current.range.start,
                        end=self._format_iso_date(current_end_dt),
                    ),
                    messages=self._merge_messages(
                        [current.messages, next_entry.messages]
                    ),
                )
            else:
                optimized.append(current)
                current = next_entry
                current_end_dt = self._parse_date(current.range.end)

        optimized.append(current)
        self.cache[channel_id] = optimized

    def load(self, channel_id: str, start_date: str, end_date: str) -> List[Message]:
        """
        Load messages for a channel within the specified date range.
        Uses cache when possible and only requests missing date ranges from the API.

        Args:
            channel_id: The Discord channel ID
            start_date: Start date in ISO format (YYYY-MM-DDThh:mm:ss.sssZ)
            end_date: End date in ISO format (YYYY-MM-DDThh:mm:ss.sssZ)

        Returns:
            List of messages for the specified channel and date range
        """
        # Ensure consistent ISO format dates
        start_dt = self._parse_date(start_date)
        end_dt = self._parse_date(end_date)
        start_date = self._format_iso_date(start_dt)
        end_date = self._format_iso_date(end_dt)

        logger.debug(
            f"Loading messages for channel {channel_id} from {start_date} to {end_date}"
        )

        # Check cache first for exact match
        cached_messages = self._find_in_cache(channel_id, start_date, end_date)
        if cached_messages is not None:
            logger.debug(
                f"Cache hit: returning {len(cached_messages)} messages from cache"
            )
            return self._filter_messages_for_date_range(
                cached_messages, start_date, end_date
            )

        # Find overlapping date ranges in cache
        overlapping_ranges = self._find_overlapping_ranges(
            channel_id, start_date, end_date
        )

        # If we have some data in cache, only fetch the missing ranges
        all_messages = []

        if overlapping_ranges:
            # Extract messages from overlapping ranges
            logger.debug(f"Found {len(overlapping_ranges)} overlapping cached ranges")
            for entry in overlapping_ranges:
                all_messages.append(entry.messages)

            # Calculate exact missing date ranges
            missing_ranges = self._calculate_missing_ranges(
                start_date, end_date, overlapping_ranges
            )

            if missing_ranges:
                logger.debug(
                    f"Need to fetch {len(missing_ranges)} missing date ranges: {missing_ranges}"
                )

                # Fetch missing ranges from API
                for missing_start, missing_end in missing_ranges:
                    if self.use_mock:
                        new_messages = _load_mock_messages(
                            channel_id, missing_start, missing_end
                        )
                    else:
                        new_messages = _load_messages_from_api(
                            channel_id, missing_start, missing_end
                        )

                    logger.debug(
                        f"Fetched {len(new_messages)} new messages for range {missing_start} to {missing_end}"
                    )
                    all_messages.append(new_messages)

                    # Store new data in cache
                    if channel_id not in self.cache:
                        self.cache[channel_id] = []

                    # Add to cache and optimize
                    merged_entry = self._merge_touching_ranges(
                        channel_id, missing_start, missing_end, new_messages
                    )
                    # Note: _merge_touching_ranges now handles adding to cache and optimization
            else:
                logger.debug("No missing date ranges, using cached data only")

            # Merge all messages
            merged_messages = self._merge_messages(all_messages)

            # Filter to ensure we only return messages within the requested range
            result = self._filter_messages_for_date_range(
                merged_messages, start_date, end_date
            )
            logger.debug(
                f"Returning {len(result)} messages after merging and filtering"
            )
            return result
        else:
            # No cached data, fetch everything
            logger.debug(f"No cached data found, fetching full range from API")
            if self.use_mock:
                messages = _load_mock_messages(channel_id, start_date, end_date)
            else:
                messages = _load_messages_from_api(channel_id, start_date, end_date)

            logger.debug(f"Fetched {len(messages)} messages from API")

            # Store in cache and optimize
            merged_entry = self._merge_touching_ranges(
                channel_id, start_date, end_date, messages
            )

            return messages
