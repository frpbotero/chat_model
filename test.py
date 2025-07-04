from helper_qdrant  import createSnapshot,downloadSnapshot,listSnapshot
from helper_aws import upload_file_to_s3, download_file_from_s3
collection = "base_conhecimento"
response = ''
snapshots = []


# response = createSnapshot(collection=collection)

# if(response != ""):
#     snapshots = listSnapshot(collection=collection)
#     print(snapshots[-1].name)


if(len(snapshots) != 0):
    abs_path = downloadSnapshot(collection=collection,snapshotName=snapshots[-1].name)


# result = upload_file_to_s3(abs_path)
# if result["success"]:
#     print("URL:", result["file_url"])
# else:
#     print("Erro:", result["error"])

path = "/home/fbotero/Documents/Eldorado/Poc_botero/chat_IA/chat_demo/"



snapshot_key = "base_conhecimento-4789786763902179-2025-07-03-20-53-19.snapshot"
local_path   = "/home/fbotero/Documents/Eldorado/Poc_botero/chat_IA/chat_demo/" + snapshot_key

result = download_file_from_s3(key=snapshot_key, destination_path=local_path)
if result["success"]:
    print(f"Arquivo baixado em: {result['path']}")
else:
    print(f"Erro ao baixar: {result['error']}")