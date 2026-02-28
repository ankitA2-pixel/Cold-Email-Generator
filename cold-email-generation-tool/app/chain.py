import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()


class Chain:
    def __init__(self):
        self.llm = ChatGroq(
            temperature=0,
            groq_api_key=os.getenv("GROQ_API_KEY"),
            model_name="llama-3.3-70b-versatile"
        )

    def extract_jobs(self, page_data):

        prompt_extractor = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT:
            {page_data}

            Extract job postings in JSON format with:
            role, experience, skills, description.

            Only return valid JSON.
            """
        )

        chain_extract = prompt_extractor | self.llm
        res = chain_extract.invoke({"page_data": page_data})

        try:
            parser = JsonOutputParser()
            parsed = parser.parse(res.content)
        except OutputParserException:
            return []

        # Always return list
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            return [parsed]
        else:
            return []

    def write_mail(self, job, links):

        prompt_email = PromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_description}

            ### PORTFOLIO LINKS:
            {link_list}

            Write a cold email as Mohan, BDE at AtliQ.
            Do not add any preamble.
            """
        )

        chain_email = prompt_email | self.llm

        res = chain_email.invoke({
            "job_description": job,
            "link_list": links
        })

        return res.content