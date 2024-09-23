# UsPolicy.io - Policy Document Chat Interface

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Demo](#demo)
- [Technologies Used](#technologies-used)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)

## Overview

UsPolicy.io is an interactive chat interface designed to empower users to query and retrieve information from policy documents seamlessly. Leveraging cutting-edge technologies like Databricks vector search embeddings, AWS Lambda, Svelte, and OpenAI's GPT models, UsPolicy.io provides accurate, context-aware responses with direct references to source documents.

**Key Highlights:**

- **Natural Language Understanding:** Users can ask questions in plain English and receive precise answers derived from policy documents.
- **Contextual Responses:** Utilizes vector search embeddings to understand and retrieve relevant information from large datasets.
- **Scalable Backend:** AWS Lambda functions ensure a scalable and cost-effective backend infrastructure.
- **Enhanced User Experience:** Features like clickable PDF page links, typing animations, and mobile responsiveness make interactions intuitive and engaging.

## Features

- **Interactive Chat Interface:** User-friendly chat interface built with Svelte for real-time interactions.
- **Vector Search Integration:** Utilizes Databricks vector search embeddings to perform semantic searches across policy documents.
- **AI-Powered Responses:** Integrates OpenAI's GPT models to generate accurate and contextually relevant answers.
- **Clickable Source Links:** Provides direct hyperlinks to specific pages in PDF documents for source verification.
- **Typing Animation:** Simulates a natural typing effect for bot responses, enhancing user engagement.
- **Mobile Responsive Design:** Ensures optimal user experience across various devices and screen sizes.
- **Scalable Backend:** AWS Lambda functions handle backend logic, ensuring scalability and reliability.

## Demo

Experience a live demo of UsPolicy.io [here](https://www.uspolicy.io/).

## Technologies Used

- **Frontend:**
  - [Svelte](https://svelte.dev/) - Reactive JavaScript framework for building user interfaces.
  - [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework for rapid UI development.
  - [Lucide Svelte](https://lucide.dev/) - Open-source icon library for Svelte.
  
- **Backend:**
  - [AWS Lambda](https://aws.amazon.com/lambda/) - Serverless compute service for running backend functions.
  - [Databricks Vector Search](https://docs.databricks.com/machine-learning/vector-search/index.html) - Semantic search using vector embeddings.
  
- **AI Integration:**
  - [OpenAI GPT-4](https://openai.com/product/gpt-4) - Advanced language model for generating human-like text.
  
- **Others:**
  - [Marked](https://marked.js.org/) - Markdown parser for converting Markdown to HTML.

## Architecture

  ```mermaid
  graph TD
      A[User] -->|Interacts with| B["Frontend (Svelte)"]
      B -->|Sends Queries| C["API Gateway"]
      C -->|Triggers| D["AWS Lambda (Backend Functions)"]
      D -->|Performs Semantic Search| E["Databricks Vector Search"]
      E -->|Retrieves Relevant Data| F["Databricks Storage"]
      D -->|Generates Response| G["OpenAI GPT-4"]
      G -->|Returns Answer| D
      D -->|Sends Response| B
  ```

**Components:**

1. **Frontend (Svelte):**
   - Renders the chat interface.
   - Handles user interactions and displays messages.
   - Communicates with the backend via API calls.

2. **Backend (AWS Lambda):**
   - Processes incoming queries.
   - Utilizes Databricks vector search to retrieve relevant document segments.
   - Interfaces with OpenAI's GPT models to generate responses.

3. **Databricks:**
   - Stores and manages policy documents.
   - Generates and maintains vector embeddings for semantic search.

4. **OpenAI GPT-4:**
   - Generates context-aware responses based on retrieved document data.

## Installation

### Prerequisites

- **Node.js** (v14 or later)
- **npm** or **yarn**
- **AWS Account** (for deploying AWS Lambda functions)
- **Databricks Account** (for vector search)
- **OpenAI API Key**
- **Docker Desktop** (for deploying image to AWS Lambda)

### Frontend Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/xnomnomzx/uspolicy.git
   cd uspolicy

### Backend Setup

1.  Deploy AWS Lambda Functions: docker image can we found in /databricks/Dockerfile

    

2. Databricks Vector Search Configuration:

    Set up your Databricks workspace.
    Upload and index your policy documents.
    Generate vector embeddings for each document using Databricks' vector search capabilities.

3. OpenAI GPT Integration:

    Ensure your OpenAI API key is securely stored and accessible to your Lambda functions.
    Configure the Lambda functions to interact with OpenAI's GPT-4 API.

### Usage

- Select a Document:
        On the left sidebar, browse and select the policy document you want to query.

- Ask a Question:
        In the chat input field, type your question related to the selected policy document.

- Receive Responses:
        The assistant will process your query and provide a context-aware answer.
        Clickable hyperlinks to specific PDF pages are provided for source verification.

### Contributing

Contributions are welcome! Please follow the steps below to contribute to UsPolicy.io:

- Fork the Repository:

    Click the "Fork" button at the top-right corner of the repository page.

    Clone Your Fork:

        git clone https://github.com/xnomnomzx/uspolicy.git
        cd uspolicy

- Create a Feature Branch:

        git checkout -b feature/your-feature-name

- Make Your Changes:

    Implement your feature or bug fix.

- Commit Your Changes:
  
        git commit -m "Add your commit message"

- Push to Your Fork:

      git push origin feature/your-feature-name

- Create a Pull Request:

 Navigate to the original repository and create a pull request from your feature branch.
