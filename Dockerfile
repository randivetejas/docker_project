FROM python:3.14-slim
#define base image as python:3.14-slim, which is a lightweight version of Python 3.14.

#install dependencies
pip install streamlit pandas plotly

# set working directory
WORKDIR /var    

#copy file 
COPY app.py .

#run streamlit app
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]