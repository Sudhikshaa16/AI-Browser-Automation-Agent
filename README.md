# AI Browser Automation Agent

An AI-powered browser automation agent that converts natural-language tasks into autonomous browser workflows. The system uses an LLM to plan browser actions, Playwright to interact with webpages, optional vision-based reasoning for screenshots, and verification to confirm task completion.

## Overview

Traditional browser automation relies on predefined scripts and fixed sequences of actions. This project uses an agent-based approach where the browser workflow is dynamically determined based on the current webpage state.

For example, a user can provide a task such as:

> Open Wikipedia and search for Artificial Intelligence.

The agent analyzes the webpage, determines the appropriate action, executes it through Playwright, observes the updated page, and continues until the task is completed or the maximum number of steps is reached.

The system can also use screenshots for additional visual reasoning and can re-plan when an action fails.

## Features

* Natural-language browser task execution
* LLM-based browser action planning
* Autonomous browser control using Playwright
* DOM-based webpage observation
* Optional screenshot-based visual reasoning
* Automatic re-planning after failed actions
* Task completion verification
* Domain allowlist for safer execution
* Step-by-step execution logging
* Run performance metrics
* FastAPI backend
* Web interface for submitting browser tasks
* Interactive API documentation

## System Architecture

```text
User Task
    |
    v
FastAPI Server
    |
    v
LLM Planner
    |
    v
Browser Observation
(DOM + Page State)
    |
    v
Playwright
    |
    +-------------------+
    |                   |
    v                   v
Browser Action     Screenshot
                        |
                        v
                  Vision Model
    |                   |
    +---------+---------+
              |
              v
        Result Verification
              |
              v
        Final Task Result
```

## Project Structure

```text
AI-Browser-Automation-Agent/
│
├── agent.py
├── config.py
├── evaluator.py
├── llm.py
├── server.py
├── requirements.txt
├── README.md
│
├── static/
│   └── index.html
│
├── logs/
│   └── execution_logs.json
│
└── screenshots/
    └── browser_screenshots.png
```

## Components

### agent.py

Contains the core browser-agent loop. It manages browser sessions, observes webpages, selects actions, executes actions, records execution history, and handles task completion.

### config.py

Contains application configuration such as:

* LLM model settings
* Maximum execution steps
* Browser mode
* Allowed domains
* Environment variables

### llm.py

Handles communication with the LLM through OpenRouter. It is responsible for:

* Action planning
* Vision-based reasoning
* Task verification

### server.py

Contains the FastAPI application and API endpoints used to communicate with the browser agent.

### evaluator.py

Processes execution logs and generates performance statistics such as completion rate, average steps, and action failure rate.

### static/index.html

Provides the web interface through which users can submit browser automation tasks and view results.

## Technologies

* Python
* FastAPI
* Playwright
* OpenRouter
* Large Language Models
* Vision-capable AI models
* HTML
* JavaScript
* JSON
* Uvicorn

## How It Works

### 1. Task Input

The user provides a task in natural language.

Example:

```text
Open Wikipedia and search for Artificial Intelligence
```

### 2. Page Observation

The agent examines the current browser page and extracts relevant information such as:

* Page URL
* Visible text
* Links
* Buttons
* Input fields
* Other relevant DOM elements

### 3. LLM Planning

The task and current browser state are sent to the LLM.

The model selects the next action required to achieve the goal.

Supported actions include:

```text
open(url)
click(selector)
type(selector, text)
press(key)
scroll(direction, amount)
wait(seconds)
extract(selector)
verify
done(message)
```

### 4. Browser Execution

The selected action is executed using Playwright.

Example:

```text
LLM
 |
 | click search box
 v
Playwright
 |
 | locate element
 v
Browser
 |
 | click
 v
Updated Page
```

The updated webpage is then observed again so that the agent can determine the next action.

### 5. Vision Reasoning

When enabled, the agent captures a screenshot of the webpage and sends it to a vision-capable model.

This provides additional visual context when DOM information alone may not be sufficient.

### 6. Error Recovery

If an action fails, the agent can observe the updated browser state and ask the LLM to generate a new action instead of immediately terminating the task.

### 7. Verification

After completing the required actions, the system verifies the current page state to determine whether the original task was actually completed.

Only after successful verification is the task reported as completed.

## API

### Health Check

```http
GET /health
```

Example response:

```json
{
  "status": "healthy"
}
```

### Metrics

```http
GET /metrics
```

Returns execution statistics including:

* Total number of runs
* Completion rate
* Average number of steps
* Action failure rate

### Submit Task

```http
POST /command
```

Example request:

```json
{
  "query": "Open Wikipedia and search for Artificial Intelligence",
  "headless": false,
  "max_steps": 10,
  "use_vision": true
}
```

Example response:

```json
{
  "status": "success",
  "message": "Task completed successfully",
  "session_id": "20260908_123456_123456",
  "steps": [],
  "final_url": "https://www.wikipedia.org/"
}
```

## Installation

### 1. Clone the repository

```bash
git clone git@github.com:Sudhikshaa16/AI-Browser-Automation-Agent.git
cd AI-Browser-Automation-Agent
```

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Chromium

```bash
python -m playwright install chromium
```

## Environment Configuration

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=minimax/minimax-m3:free
OPENROUTER_VISION_MODEL=minimax/minimax-m3:free
MAX_STEPS=15
HEADLESS=false
ALLOWED_DOMAINS=youtube.com,wikipedia.org,google.com,amazon.com
```

Do not commit the `.env` file to GitHub.

Add the following to `.gitignore`:

```text
.env
venv/
.venv/
__pycache__/
*.pyc
node_modules/
```

## Running the Application

Start the FastAPI server:

```bash
python -m uvicorn server:app --reload
```

Open the application:

```text
http://127.0.0.1:8000/
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

## Safety

The application uses a domain allowlist to restrict browser automation to approved websites.

Example:

```env
ALLOWED_DOMAINS=youtube.com,wikipedia.org,google.com,amazon.com
```

The agent should only be used in controlled and authorized environments.

It should not be used for:

* Financial transactions
* Password changes
* Account deletion
* Sensitive administrative actions
* Irreversible operations
* Unauthorized automation

## Logging and Evaluation

Each browser-agent execution can be recorded in the `logs/` directory.

Screenshots captured during execution are stored in the `screenshots/` directory.

These records can be used to:

* Debug failed tasks
* Analyze agent decisions
* Evaluate task completion
* Measure browser-agent performance
* Compare different planning strategies

## Performance Metrics

The system provides metrics including:

| Metric              | Description                                |
| ------------------- | ------------------------------------------ |
| Run Count           | Total number of agent executions           |
| Completion Rate     | Percentage of successfully completed tasks |
| Average Steps       | Average number of actions per task         |
| Action Failure Rate | Percentage of failed browser actions       |

## Use Cases

This project demonstrates practical applications of Agentic AI and browser automation, including:

* Autonomous web navigation
* LLM-based task planning
* Intelligent web interaction
* Vision-assisted browser automation
* Self-correcting AI agents
* Goal-driven browser workflows
* Automated information retrieval


