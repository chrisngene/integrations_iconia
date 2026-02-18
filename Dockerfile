FROM python:3.11.1


WORKDIR /usr/src/application


RUN pip install --upgrade pip


COPY requirements.txt ./


RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for logs
RUN mkdir /usr/src/application/logs


# Create a directory for logs
RUN mkdir /usr/src/application/company


# Create a directory for logs
RUN mkdir /usr/src/application/products

# Set permissions for the log directory
RUN chmod 777 /usr/src/application/company


# Set permissions for the log directory
RUN chmod 777 /usr/src/application/products


# Set permissions for the log directory
RUN chmod 777 /usr/src/application/logs


COPY . .


CMD ["uvicorn", "api_v1.main:app", "--host", "0.0.0.0", "--port", "8006"]
