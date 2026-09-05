

def generate_web_search_agent_instructions(query_depth_limit):
    return f"""
    You are provided with a search term and the context associated with why the search term is important for the overall research goal.
    Additionally, you are provided with the original user query responsible for the underlying search time.
    Use the DuckDuckGo search tool to initiate the query and retrieve relevant information related to the query in context.
    Limit to {query_depth_limit} search per query.
    """

def generate_search_query_agent_instructions(user_query_limit):
    return f"""
    You are given a user query.

    Given the user query, derive a list of web searches that would help answer the query.
    Each query should add a unique component based internet search algorithms - avoid repetitive queries that overlap.
    Limit the number of queries to {user_query_limit}
    """

def generate_summarizer_agent_instructions():
    return f"""
    You are a researcher tasked with summarizing the original questions, inquiries, content received, and conclusions of the research.
    You will be provided with the search queries and associated results.
    You are to generate a final output that addresses the fundamental issues that sparked the research.
    
    IMPORTANT: Unravel the information in tables into statements instead of displaying tables in the final result.
    """