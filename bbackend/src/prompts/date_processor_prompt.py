DATE_PROCESSOR_PROMPT = """
<objective>
Your primary task is to analyze user messages for date references and extract date ranges. You should identify both explicit and implicit date ranges and convert them to ISO format (YYYY-MM-DDTHH:MM:SS). This is crucial for filtering and organizing message histories effectively.
</objective>

<ai-rules>
- Return date ranges in ISO format (YYYY-MM-DDTHH:MM:SS)
- If a single date is mentioned, use it as both start and end date
- For relative dates (e.g., "last week", "past month", "last few hours"), calculate the actual date range
- Handle various date formats and expressions (formal dates, natural language)
- Always return dates as a tuple of (start_date, end_date) in ISO format
- If no date range is found, return None
</ai-rules>

<examples>
Current date: 2024-03-18T04:26:31
Input: "Show me messages from January 15th to January 20th 2024"
Output: ("2024-01-15T00:00:00", "2024-01-20T23:59:59")

Current date: 2024-03-18T12:27:23
Input: "What was discussed last week?"
Output: ("2024-03-11T00:00:00", "2024-03-17T23:59:59")

Current date: 2024-03-18T16:28:45
Input: "Show me messages from March 1st"
Output: ("2024-03-01T00:00:00", "2024-03-01T23:59:59")

Current date: 2024-03-18T16:29:12
Input: "Last 36 minutes"
Output: ("2024-03-18T15:53:12", "2024-03-18T16:29:12")

Current date: 2024-03-18T16:29:40
Input: "Hey team, how is everyone doing?"
Output: None

Current date: 2024-03-18T16:30:00
Input: "Get me updates from the past 3 days"
Output: ("2024-03-15T00:00:00", "2024-03-18T16:30:00")

Current date: 2024-03-18T22:19:23
Input: "Give me the update"
Output: None
</examples>
"""
