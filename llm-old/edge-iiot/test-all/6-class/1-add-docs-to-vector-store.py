import pandas as pd
import os
from tabulate import tabulate

# Load dateset
df = pd.read_csv(os.getcwd() + '/../../data/edge-iiot/Edge-IIoTset dataset/Selected dataset for ML and DL/ML-EdgeIIoT-dataset.csv', low_memory=False)

# Split dataset according to attack type
normal_df = df[df['Attack_type'].isin(["Normal"])]
ddos_df = df[df['Attack_type'].isin(["DDoS_HTTP", "DDoS_TCP", "DDoS_UDP", "DDoS_ICMP"])]
injection_df = df[df['Attack_type'].isin(["Uploading", "SQL_injection", "XSS"])]
mitm_df = df[df['Attack_type'].isin(["MITM"])]
malware_df = df[df['Attack_type'].isin(["Ransomware", "Password", "Backdoor"])]
scanning_df = df[df['Attack_type'].isin(["Fingerprinting", "Port_Scanning", "Vulnerability_scanner"])]

# Drop columns
normal_df = normal_df.drop(columns=['Attack_label', 'Attack_type'])
ddos_df = ddos_df.drop(columns=['Attack_label', 'Attack_type'])
injection_df = injection_df.drop(columns=['Attack_label', 'Attack_type'])
mitm_df = mitm_df.drop(columns=['Attack_label', 'Attack_type'])
malware_df = malware_df.drop(columns=['Attack_label', 'Attack_type'])
scanning_df = scanning_df.drop(columns=['Attack_label', 'Attack_type'])

# Split dataset into training and test set
normal_df_train = normal_df.sample(frac=0.8, random_state=42)
normal_df_test = normal_df.drop(normal_df_train.index)
ddos_df_train = ddos_df.sample(frac=0.8, random_state=42)
ddos_df_test = ddos_df.drop(ddos_df_train.index)
injection_df_train = injection_df.sample(frac=0.8, random_state=42)
injection_df_test = injection_df.drop(injection_df_train.index)
mitm_df_train = mitm_df.sample(frac=0.8, random_state=42)
mitm_df_test = mitm_df.drop(mitm_df_train.index)
malware_df_train = malware_df.sample(frac=0.8, random_state=42)
malware_df_test = malware_df.drop(malware_df_train.index)
scanning_df_train = scanning_df.sample(frac=0.8, random_state=42)
scanning_df_test = scanning_df.drop(scanning_df_train.index)

# Print dataset sizes in a table
data = [
    ["Normal", normal_df.shape[0], normal_df_train.shape[0], normal_df_test.shape[0]],
    ["DDoS", ddos_df.shape[0], ddos_df_train.shape[0], ddos_df_test.shape[0]],
    ["Injection", injection_df.shape[0], injection_df_train.shape[0], injection_df_test.shape[0]],
    ["MITM", mitm_df.shape[0], mitm_df_train.shape[0], mitm_df_test.shape[0]],
    ["Malware", malware_df.shape[0], malware_df_train.shape[0], malware_df_test.shape[0]],
    ["Scanning", scanning_df.shape[0], scanning_df_train.shape[0], scanning_df_test.shape[0]]
]
print(tabulate(data, headers=["Atack type", "Total", "Train", "Test"], tablefmt="grid"))

from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from tqdm import tqdm

# Initialize embeddings
embeddings = HuggingFaceEmbeddings()

# Initialize vector store
vector_store = Chroma(
    collection_name="edge-iiotset",
    embedding_function=embeddings, 
    persist_directory="./chroma_db_binary")

# Add batched documents to vector store
batch_size = 16
datasets = {
    "normal": normal_df_train, 
    "ddos": ddos_df_train, 
    "injection": injection_df_train, 
    "mitm": mitm_df_train, 
    "malware": malware_df_train, 
    "scanning": scanning_df_train
}

for attack_type, dataset in datasets.items():
    total_documents = dataset.shape[0]
    for i in tqdm(range(0, total_documents, batch_size), ncols=100, desc=f"Adding {attack_type} documents to vector store"):
        documents = [Document(page_content=str(dataset.iloc[i+j].to_list()), metadata={"source": "edge-iiotset", "label": attack_type}) for j in range(min(batch_size, total_documents-i))]
        vector_store.add_documents(documents)
    print(f"Added {total_documents} {attack_type} documents to vector store")