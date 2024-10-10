import os
from langchain_databricks.vectorstores import DatabricksVectorSearch
import openai
from flask import Flask, jsonify, request
from flask_cors import CORS
import awsgi
import boto3
import re
# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
dynamodb = boto3.resource('dynamodb')
table_name = 'documents' 
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    event['queryStringParameters'] = event.get('queryStringParameters', {})
    response = awsgi.response(app, event, context, base64_content_types=['application/gzip'])
    return response

@app.route('/uspolicy/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    doc_id = request.json.get('documentId', '')
    source_url = request.json.get('source_url', '')
    
    if not user_message or not doc_id:
        return jsonify({"response": "Please select a document and provide a message."}), 400
    try:
        # Perform vector search
        search_results = vector_search(user_message, doc_id)
        
        if not search_results:
            return jsonify({"response": "No results found for the given query and document ID."}), 404
        
        # Unpack the array and prepare the context including page numbers
        page_contents = [f"\"{item['page_content']}\"" for item in search_results]
        page_numbers = [str(int(item['page_number'])) for item in search_results]
        
        content_with_pages = [
            f"Page {page}: {content}" for content, page in zip(page_contents, page_numbers)
        ]
        context = '\n\n'.join(content_with_pages)
        # Generate a response from OpenAI
        output = generate_completion(context=context, question=user_message)
        
        def replace_page_numbers(match):
            pages_str = match.group(1)  # Extract the string containing page numbers
            page_numbers = re.findall(r'\d+', pages_str)  # Find all page numbers
            links = [f'<a href="{source_url}#page={page}">(Page {page})</a>' for page in page_numbers]
            return ', '.join(links)

        # Updated regex to capture multiple page numbers
        html_output = re.sub(r'%&\(Pg\.([^)]+)\)', replace_page_numbers, output)

        return jsonify({"response": html_output})

    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}"}), 500

def vector_search(query, doc_id):
    vsc = DatabricksVectorSearch(
        endpoint='uspolicy',
        index_name='us_policy.default.vector_text',
    )
    # Apply a filter on 'document_id' during the similarity search
    results = vsc.similarity_search(
        k=3,
        query=query,
        filter={'document_id': doc_id}
    )
    
    # Collect page content and page number
    results_array = []
    for doc in results:
        page_content = doc.page_content
        page_number = doc.metadata.get('page_number', 'N/A')  # Default to 'N/A' if not available
        results_array.append({
            'page_content': page_content,
            'page_number': page_number
        })
    
    return results_array

def generate_completion(context, question):
    system_prompt = os.getenv('OPENAI_PROMPT_SYSTEM', '')
    if not system_prompt:
        raise ValueError("OPENAI_PROMPT_SYSTEM environment variable is not set.")
        
    user_message = f"QUERY: {question}\n\nTEXT: {context}"    
    
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        ai_response = response.choices[0].message.content.strip()
        return ai_response
        
    except Exception as e:
        raise e
    
@app.route('/uspolicy/documents', methods=['GET'])
def get_documents():
    try:
        # Scan the DynamoDB table to get all documents
        response = table.scan()
        documents_list = response.get('Items', [])
        
        # Convert the DynamoDB items into the desired JSON format
        documents_json = [
            {
                "id": item.get('id'),
                "title": item.get('document_name'),
                "source_url": item.get('url')
            } for item in documents_list
        ]
        
        return jsonify(documents_json) 
    except Exception as e:
        return jsonify({"error": str(e)}), 500
