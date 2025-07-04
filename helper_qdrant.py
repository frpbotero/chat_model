from qdrant_client import QdrantClient
import requests
import os

client = QdrantClient(url="http://localhost:6333")

def createSnapshot(collection:str):
    response = client.create_snapshot(collection_name=collection)
    return response


def listSnapshot(collection:str):
    response = client.list_snapshots(collection_name=collection)
    return response

def downloadSnapshot(collection:str, snapshotName:str):
    response = requests.get(
        f"http://localhost:6333/collections/{collection}/snapshots/{snapshotName}",
        headers={"api-key": "abra@102030"},
        stream=True
    )
    response.raise_for_status()

    local_filename =   snapshotName
    with open(local_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    abs_path = os.path.abspath(local_filename)
    print(f"Snapshot salvo em {abs_path}")
    return abs_path


