from src.tools.date_processor import date_processor_agent_tool
from src.tools.read_through_cache import ReadThroughCache
from src.tools.load_messages import create_load_messages
from src.tools.summarizer import summarizer_agent_tool

def get_tools(cache: ReadThroughCache):
   return [create_load_messages(cache), summarizer_agent_tool, date_processor_agent_tool]
