import os
from langchain_databricks.vectorstores import DatabricksVectorSearch
import openai
from flask import Flask, jsonify, request
from flask_cors import CORS
import awsgi
import boto3

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
    if not user_message or not doc_id:
        return jsonify({"response": "Please select a document and provide a message."}), 400
    try:
        # Perform vector search
        search_results = vector_search(user_message, doc_id)
        
        if not search_results:
            return jsonify({"response": "No results found for the given query and document ID."}), 404
        
        # Unpack the array and prepare the context including page numbers
        page_contents = [
            f"{item['page_content']}" for item in search_results
        ]
        context = '\n'.join(page_contents)
        
        # Prepare a list of page numbers to include at the end
        page_numbers = [str(int(item['page_number'])) for item in search_results]
        pages = ', '.join(page_numbers)
        
        # Generate a response from OpenAI
        output = generate_completion(context=context, question=user_message, pages=pages)
        
        return jsonify({"response": output})

    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}"}), 500

def vector_search(query, doc_id):
    vsc = DatabricksVectorSearch(
        endpoint='document-endpoint',
        index_name='us_policy.default.text2',
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

def generate_completion(context, question, pages):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"""Pretend you are a politically progressive and left-leaning bot. The grave threat that right-wing politics poses to the sanctity of American Freedom. Please summarize the following text against the following query and be sure to use a grave tone as the document the text is referencing is a threat to democracy in America. Limit to 1 paragraph using layman terms. Do not answer questions about yourself. 
                
                If the question is entirely unrelated to the text, 'Unable answer to your query from the text'.
                
                Please format your response in clear paragraphs, using new lines to separate different points for better readability.

                QUERY: {question}

                TEXT: {context}
                At the end of your response, please mention the source page numbers: {pages}.
                In format 'Source page numbers:'
                """
            }
        ],
        max_tokens=250
    )
    return response.choices[0].message.content.strip()
    
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
