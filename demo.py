import warnings

from crewai import Agent, Crew, Task, LLM, Process
from src.agentic_rag.tools.custom_tool import DocumentSearchTool
from src.agentic_rag.tools.custom_tool import FireCrawlWebSearchTool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

warnings.filterwarnings("ignore")

# Initialize LLM
llm = LLM(
    model="ollama/llama3:latest",
    base_url="http://127.0.0.1:11434"
)


# Initialize PDF tool
pdf_tool = DocumentSearchTool(file_path='/Users/ShahYash/Desktop/Projects/rag project/agentic_rag/knowledge/Smart Wardrobe_ipd paper.pdf')

web_search_tool = FireCrawlWebSearchTool()

retriever_agent = Agent(
    role="""Retrieve relevant information to answer the user query: {query}""",
    goal="""Retrieve the most relevant information from the available sources 
            for the user query: {query}, always try to use the pdf search tool first. 
            If you are not able to retrieve the information from the pdf search tool 
            then try to use the web search tool.""",
    backstory="""You're a meticulous analyst with a keen eye for detail. 
                You're known for your ability understand the user query: {query} 
                and retrieve knowlege from the most suitable knowledge base.""",
    verbose=True,
    tools=[
        pdf_tool,
        web_search_tool
    ],
    llm=llm
)

response_synthesizer_agent = Agent(
    role="""Response synthesizer agent for the user query: {query}""",
    goal="""Synthesize the retrieved information into a concise and coherent response 
            based on the user query: {query}. If you are not able to retrieve the 
            information then respond with "I'm sorry, I couldn't find the information 
            you're looking for.""",
    backstory="""You're a skilled communicator with a knack for turning complex 
                information into clear and concise responses.""",
    verbose=True,
    llm=llm
)

retrieval_task = Task(
    description="""Retrieve the most relevant information from the available 
                   sources for the user query: {query}""",
    expected_output="""The most relevant information in form of text as retrieved
                       from the sources.""",
    agent=retriever_agent
)

response_task = Task(
    description="""Synthesize the final response for the user query: {query}""",
    expected_output="""A concise and coherent response based on the retrieved infromation
                       from the right source for the user query: {query}. If you are not 
                       able to retrieve the information then respond with 
                       I'm sorry, I couldn't find the information you're looking for.""",
    agent=response_synthesizer_agent
)

crew = Crew(
			agents=[retriever_agent, response_synthesizer_agent], 
			tasks=[retrieval_task, response_task],
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

result = crew.kickoff(inputs={"query": "Who is the current prime minister of India?"})
print(result)

