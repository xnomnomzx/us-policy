import os
from langchain_databricks.vectorstores import DatabricksVectorSearch
import openai
from flask import Flask, jsonify, request
import awsgi
import boto3

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb')
table_name = 'documents' 
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    event['queryStringParameters'] = event.get('queryStringParameters', {})
    event['queryStringParameters'] = event.get('queryStringParameters', {})
    event['httpMethod'] = event.get('httpMethod', 'POST')
    
    # Route based on path
    if event['path'] == '/documents':
        event['httpMethod'] = 'GET'
    elif event['path'] == '/chat':
        event['httpMethod'] = 'POST'
    response = awsgi.response(app, event, context, base64_content_types=['application/gzip'])

    # Add CORS headers to the response
    response['headers']['Access-Control-Allow-Origin'] = '*'
    response['headers']['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response['headers']['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    return response

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    if not user_message:
        return jsonify({"response": "Please provide a message."}), 400
    try:
        # Generate a response from GPT-4
        search_results = vector_search(user_message)
        output = generate_completion(context=search_results, question=user_message)

        return jsonify({"response": output})

    except Exception as e:
        return jsonify({"response": "An error occurred: " + str(e)}), 500
    return jsonify({"response": response})

def vector_search(query):
    vsc = DatabricksVectorSearch(
        endpoint='document-endpoint',
        index_name='us_policy.default.text',
    )
    results_array = []
    results = vsc.similarity_search(k=3, query=query)
    for doc in results:
        results_array.append(doc.page_content)

    return ", ".join(results_array)
    
def generate_completion(context, question):
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"""Pretend you are a politically progressive and left-leaning bot. The grave threat that right-wing politics poses to the sanctity of American Freedom. Please summarize the following text against the following query and be sure to use a grave tone as the document the text is referencing is a threat to democracy in America. Generate a response only using text from the following. Limit to 1 paragraph using layman terms. Do not answer questions about yourself.
                QUERY: {question}
        
                TEXT: {context}
                """,
            }
        ],
        max_tokens=250
    )
    return response.choices[0].message.content.strip()
    
@app.route('/documents', methods=['GET'])
def get_documents():
    try:
        # Scan the DynamoDB table to get all documents
        response = table.scan()
        documents_list = response.get('Items', [])
        
        # Convert the DynamoDB items into the desired JSON format
        documents_json = [{"id": item.get('id'), "title": item.get('document_name'), "source_url": item.get('url')} for item in documents_list]
        
        # Return the documents as JSON
        return jsonify(documents_json)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
