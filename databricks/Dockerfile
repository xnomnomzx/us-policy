FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}

RUN pip install databricks-vectorsearch==0.40 openai==1.35.3 flask langchain-databricks aws-wsgi boto3 flask-cors 

COPY lambda_function.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]
