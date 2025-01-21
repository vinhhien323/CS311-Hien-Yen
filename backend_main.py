import argparse
import os
import json
import faiss
from llama_index.llms.gemini import Gemini
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document, PromptTemplate, StorageContext
from llama_index.core.node_parser import TokenTextSplitter, JSONNodeParser
from llama_index.readers.json import JSONReader
from llama_index.embeddings.gemini import GeminiEmbedding
from llama_index.vector_stores.faiss import FaissVectorStore

class Chatbot:
    def __init__(self, data_dir):
        google_gemini_api = 'AIzaSyCiEDbg9BZVP9lAg9Q2HCFXNgEBCNHS0Zw'
        os.environ["GOOGLE_API_KEY"] = google_gemini_api
        os.environ["MODEL_NAME"] = "models/gemini-1.5-flash-latest"
        # LLM model
        self.llm = Gemini(model_name="models/gemini-1.5-flash-latest", api_key=os.environ["GOOGLE_API_KEY"])
        self.embed_model = GeminiEmbedding(api_key= google_gemini_api, model="models/gemini-1.5-flash-latest")
        self.reader = JSONReader()
        self.splitter = TokenTextSplitter(chunk_size=500, chunk_overlap=10, separator="},",)
        self.index = None
        self.query_engine = None
        QA_PROMPT_TMPL = (
            "Your task is to answer all the questions that users ask based only on the context information provided below.\n"
            "Please answer the question at length and in detail, with full meaning.\n"
            "In the answer there is no sentence such as: based on the context provided.\n"
            "Context information is below.\n"
            "------------------------------------------\n"
            "{context_str}\n"
            "The topics may be included in Title"
            "------------------------------------------\n"
            "Given the context information and not prior knowledge, "
            "answer the query.\n"
            "Query: {query_str}\n"
            "Answer: "
            "The answer should be in the following format:"
            "1. Title"
            "2. Topic"
            "3. Type of questions"
            "4. Origin: Book Title and page details"
        )
        self.qa_prompt = PromptTemplate(QA_PROMPT_TMPL)
        self.vector_store = FaissVectorStore(faiss_index=faiss.IndexFlatL2(1536))
        self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        self.insert_data(data_dir)
        self.update_engine()




    def read_data(self, data_dir):
        file_list = os.listdir(data_dir)
        documents = []
        for file_name in file_list:
            with open(f'{data_dir}/{file_name}','r',encoding='utf-8') as inp:
                data = json.load(inp)
            new_documents = [Document(text=json.dumps(item)) for item in data]
            documents += new_documents
        return documents

    def insert_data(self, data_dir):
        documents = self.read_data(data_dir)
        nodes = self.splitter.get_nodes_from_documents(documents)
        self.index = VectorStoreIndex(nodes, embed_model=self.embed_model, storage_context=self.storage_context)
        self.index.storage_context.persist(persist_dir="")

    def update_engine(self):
        self.query_engine = self.index.as_query_engine(similarity_top_k=10, llm=self.llm)
        self.query_engine.update_prompts(
            {"response_synthesizer:text_qa_template": self.qa_prompt}
        )

    def query(self, prompt):
        return self.query_engine.query(prompt)
