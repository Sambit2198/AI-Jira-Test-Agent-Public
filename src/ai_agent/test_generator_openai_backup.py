
import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


# Load API key from .env
load_dotenv()


# Define the structure of an individual test step
class TestStep(BaseModel):
    action: str
    expected_result: str


# Define test data
class TestData(BaseModel):
    name: str
    value: str


# Define an individual test case
class TestCase(BaseModel):
    id: str
    title: str
    preconditions: str
    steps: list[TestStep]
    expected_result: str
    test_data: list[TestData]


# Define the complete test suite
class TestSuite(BaseModel):
    test_cases: list[TestCase]


class AITestGenerator:

    def __init__(self):

        api_key = os.getenv("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Check your .env file."
            )

        self.client = OpenAI(api_key=api_key)

    def generate_test_cases(self, user_prompt):

        instructions = """
        You are an expert software QA test case generation agent.

        Convert the user's plain-English testing request into
        detailed, structured software test cases.

        Rules:
        1. Identify all relevant positive and negative scenarios.
        2. Generate unique test case IDs.
        3. Include clear preconditions.
        4. Break each test into sequential actions.
        5. Give an expected result for each step.
        6. Include an overall expected result.
        7. Include relevant test data.
        8. Do not invent actual website credentials.
        9. If test data is unknown, use clearly marked placeholders.
        10. Do not assume application-specific behaviour that
            the user has not described.
        11. Generate only test cases relevant to the user's request.
        12. Return an empty test_cases list if the request is
            unrelated to software testing.
        """

        response = self.client.responses.parse(
            model="gpt-5-mini",
            input=[
                {
                    "role": "developer",
                    "content": instructions
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            text_format=TestSuite
        )

        result = response.output_parsed

        if result is None:
            raise ValueError(
                "The AI did not return structured test cases."
            )

        test_cases = [
            test_case.model_dump()
            for test_case in result.test_cases
        ]

        return {
            "message": "AI test cases generated successfully.",
            "total_test_cases": len(test_cases),
            "test_cases": test_cases
        }


if __name__ == "__main__":

    try:
        generator = AITestGenerator()

        prompt = input(
            "\nDescribe what you want to test: "
        )

        result = generator.generate_test_cases(prompt)

        print("\nAI GENERATED TEST CASES\n")

        print(
            json.dumps(
                result,
                indent=4,
                ensure_ascii=False
            )
        )

    except Exception as error:
        print(f"\nError: {error}")
