
from pydantic import BaseModel, Field

class WebSearchItem(BaseModel):
    search_term: str = Field(description="The query string that will retrieve results from the internet.")
    reason: str = Field(description="Your reasoning for why this search is important for the query.")

class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem] = Field(description="A list of web searches to perform for answering a given query.")

class OutputReport(BaseModel):
    overview: str = Field(description="A 3-4 sentence  summary of the overall report.")
    main_report: str = Field(description="The main markdown report highlighting the details and results of the search.")
    searches: WebSearchPlan = Field(description="Recommended queries for further research to help uncover unanswered or unclear questions.")
    further_research: str = Field(description="An honest assessment of the limitations of the research and recommended future research.")