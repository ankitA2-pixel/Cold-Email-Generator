import pandas as pd
import chromadb
import uuid


class Portfolio:

    def __init__(self, file_path="my_portfolio.xlsx"):
        self.file_path = file_path
        self.data = pd.read_excel(file_path)
        self.chroma_client = chromadb.PersistentClient('vectorstore')
        self.collection = self.chroma_client.get_or_create_collection(name="portfolio")

    def load_portfolio(self):
        if self.collection.count() == 0:
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=[str(row["Techstack"])],
                    metadatas=[{"links": str(row["Links"])}],
                    ids=[str(uuid.uuid4())]
                )

    def query_links(self, skills):
        # 🔥 SAFETY CHECK (fixes your error)
        if not skills:
            return []

        if isinstance(skills, str):
            skills = [skills]

        try:
            results = self.collection.query(
                query_texts=skills,
                n_results=2
            )
            return results.get('metadatas', [])
        except Exception:
            return []