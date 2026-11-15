# AI Jira / Web Testing Agent



An AI-assisted web testing application built with Python, Groq, Playwright and Streamlit. It generates test cases, executes browser automation, captures evidence and creates downloadable execution reports.



## Live Application



[Open the hosted AI Web Testing Agent](https://ai-jira-test-agent-public-w7dlrqylpjtzahledrk9mp.streamlit.app/)



The hosted application runs on Streamlit Cloud. Browser automation runs on the cloud server in headless mode. It does not open a browser window on your personal computer.



## Current Features



- AI-assisted test generation using Groq.

- Browser automation using Playwright.

- Eight predefined SauceDemo test scenarios (TC_LOGIN_001 to TC_LOGIN_008).

- Positive and negative login testing.

- End-to-end shopping and checkout validation.

- Execution summaries and individual test-step results.

- Downloadable JSON, Word and Excel reports.



## Current Application Scope



The current application is configured for SauceDemo:



https://www.saucedemo.com



Enter the website URL and describe the scenarios you want to execute. Include the relevant test IDs in your instructions.



The current version supports eight predefined SauceDemo scenarios. It is not yet a general-purpose testing platform for arbitrary websites.



## Technology Stack



- Python

- Streamlit

- Groq API

- Playwright

- Pydantic

- OpenAI-compatible Python SDK

- PyAutoGUI (Windows local execution)

- Python-docx

- OpenPyXL



## Run Locally on Windows



### 1. Prerequisites



Install Python and Git.



Playwright will install its own Chromium browser, so a separate Chrome installation is not required.



### 2. Clone the repository



Open PowerShell:



```powershell

git clone https://github.com/Sambit2198/AI-Jira-Test-Agent-Public.git

cd AI-Jira-Test-Agent-Public

```



### 3. Create a virtual environment



```powershell

python -m venv .venv

```



### 4. Install dependencies



```powershell

.\.venv\Scripts\python.exe -m pip install -r requirements.txt

```



### 5. Install Chromium



```powershell

.\.venv\Scripts\python.exe -m playwright install chromium

```



### 6. Configure the Groq API key



Create a folder named `.streamlit` in the project root if it does not exist.



Inside it, create a file named `secrets.toml`.



Add:



```toml

GROQ_API_KEY = "your_groq_api_key"

```



Replace the placeholder with your own Groq API key.



Never publish this file or share your API key. The repository's `.gitignore` excludes this file.



The application uses SauceDemo's standard test credentials by default:



- Username: `standard_user`

- Password: `secret_sauce`



### 7. Start the application



```powershell

.\.venv\Scripts\python.exe -m streamlit run app.py

```



Open the local URL displayed in the terminal, normally:



http://localhost:8501



On Windows, local execution uses a visible browser and physical mouse interaction by default.



## How to Execute Tests



1\. Open the application.

2\. Enter `https://www.saucedemo.com`.

3\. Describe the test scenarios you want to execute.

4\. Include the required test IDs, such as TC_LOGIN_001 or TC_LOGIN_002.

5\. Click **Generate and Execute Tests**.

6\. Review the execution summary and individual test results.

7\. Download the JSON, Word or Excel report.



## Reports



Generated execution reports are stored in the local `reports/` directory.



Available formats:



- JSON: structured execution results.

- Word: formatted execution report.

- Excel: spreadsheet execution report.



Reports can also be downloaded directly from the Streamlit application.



## Execution Environments



**Local Windows execution**



- Runs on your computer.

- Uses visible Chromium browser automation.

- Uses PyAutoGUI for physical mouse interaction by default.



**Streamlit Cloud execution**



- Runs on the hosted server.

- Uses headless Chromium.

- Uses Playwright locator-based clicks instead of physical mouse interaction.

- Does not display the cloud browser on your local desktop.



## Security



- Never commit API keys, passwords or private configuration files.

- Keep `.streamlit/secrets.toml` and `.env` out of Git.

- Use your own Groq API key when running a local copy.

- Avoid putting private credentials in test prompts or public reports.



## Repository Structure



```text

AI-Jira-Test-Agent-Public/

├── app.py

├── main.py

├── requirements.txt

├── README.md

├── .gitignore

├── config/

├── src/

│   ├── ai_agent/

│   ├── browser/

│   └── reporting/

├── web_app/

├── test-data/

└── tests/

```



## Disclaimer



This is an evolving project. The current public Streamlit workflow is initially configured for SauceDemo and its eight predefined test scenarios. Features and integrations may change as development continues.
