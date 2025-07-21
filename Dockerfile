FROM python:3.8.20-slim
RUN apt-get update && apt-get install -y \
    curl \
    jq \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app/
RUN apt-get update && apt-get install -y build-essential
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "\
import nltk; \
nltk.download('punkt', quiet=True); \
nltk.download('stopwords', quiet=True); \
nltk.download('wordnet', quiet=True); \
nltk.download('vader_lexicon', quiet=True); \
import spacy; \
from spacy.cli import download; \
download('en'); \
spacy.load('en_core_web_sm') \
"
RUN chmod +x run.sh
ENTRYPOINT ["./run.sh"]