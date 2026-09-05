 # Credit to Ed Donner (https://gale.udemy.com/user/ed-donner-3/) for providing inspiration and guidance on some of this code

from agents import Agent, OpenAIChatCompletionsModel, Runner
from openai import AsyncOpenAI
import asyncio
from agents.mcp import MCPServerStdio
import os
from dotenv import load_dotenv
import markdown
from xhtml2pdf import pisa
from schemas.structured_output import WebSearchPlan, WebSearchItem, OutputReport
from prompts.prompts import generate_summarizer_agent_instructions, generate_search_query_agent_instructions, generate_web_search_agent_instructions

load_dotenv()

# Define the model
ollama_client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

USER_QUERY = "Outline the Pittsburgh job market for someone with a doctorate in Artificial Intelligence and 10 years of software engineering experience."
USER_QUERY_LIMIT = 4
QUERY_DEPTH_LIMIT = 1
MODEL = "qwen3.8:27b"

# Get a sample result from Tavily
async def run_search(item: WebSearchItem):
    async with MCPServerStdio(
            name="tavily",
            params={
                "command": "npx.cmd",
                "args": ["-y", "tavily-mcp"],
                "env": {"TAVILY_API_KEY": os.environ["TAVILY_API_KEY"]},
            },
    ) as ddg_server:
        search_agent = Agent(
            name="SearchAgent",
            instructions=generate_web_search_agent_instructions(QUERY_DEPTH_LIMIT),
            model=OpenAIChatCompletionsModel(
                model=MODEL,
                openai_client=ollama_client,
            ),
            mcp_servers=[ddg_server],
        )
        result = await Runner.run(search_agent, f"""Search Query: {item.search_term} Search Query Justification: {item.reason} Original Query: {USER_QUERY}""")
        return result.final_output

async def get_search_queries():

    term_retriever_agent = Agent(
        name="Internet Search Term Agent",
        instructions=generate_search_query_agent_instructions(USER_QUERY_LIMIT),
        model=OpenAIChatCompletionsModel(
            model=MODEL,
            openai_client=ollama_client,
        ),
        output_type=WebSearchPlan
    )

    result = await Runner.run(term_retriever_agent, USER_QUERY)
    return result.final_output

async def generate_summary_report(input):

    summarization_agent = Agent(
        name="Internet Search Term Agent",
        instructions=generate_summarizer_agent_instructions(),
        model=OpenAIChatCompletionsModel(
            model=MODEL,
            openai_client=ollama_client,
        ),
        output_type=OutputReport
    )

    summarization = await Runner.run(summarization_agent, input)

    report: OutputReport = summarization.final_output

    searches_md = "\n".join(
        f"- **{item.search_term}**: {item.reason}"
        for item in report.searches.searches
    )

    markdown_content = "\n".join([
        "# Report Summary",
        report.overview,
        "",
        "## Main Report",
        report.main_report,
        "",
        "## Further Research",
        report.further_research,
        "",
        "## Recommended Follow-Up Searches",
        searches_md,
    ])

    with open("output.pdf", "wb") as f:
        pisa.CreatePDF(markdown.markdown(markdown_content), dest=f)

async def main():

    search_terms_task = get_search_queries()
    result = await search_terms_task

    # Get the coreferences for each search task
    tasks = [run_search(item) for item in result.searches]

    # Execute in parallel
    results = await asyncio.gather(*tasks)

    generate_report_coroutine = generate_summary_report(f"""
        Query: {USER_QUERY} search strings: {result.searches} search results: {results}
    """)

    await generate_report_coroutine

asyncio.run(main())

