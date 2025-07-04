# backup_snapshot_service.py

import os
import logging
from apscheduler.schedulers.blocking import BlockingScheduler

from helper_qdrant import createSnapshot, listSnapshot, downloadSnapshot
from helper_aws    import upload_file_to_s3

# ─── Configurações ───────────────────────────────────────────
COLLECTION   = "base_conhecimento"
API_KEY      = os.getenv("QDRANT_API_KEY", "abra@102030")
DOWNLOAD_DIR = "/tmp/qdrant_snapshots"   # diretório para salvar o snapshot
# ──────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s — %(message)s"
)


def do_backup_cycle():
    try:
        logging.info("Iniciando ciclo de backup de snapshot")

        # 1) Cria snapshot
        resp = createSnapshot(collection=COLLECTION)
        logging.info(f"Snapshot criado: {resp.name}")

        # 2) Lista snapshots e seleciona o mais recente
        snaps = listSnapshot(collection=COLLECTION)
        if not snaps:
            raise RuntimeError("Nenhum snapshot encontrado após criação.")
        latest = snaps[-1].name
        logging.info(f"Snapshot mais recente: {latest}")

        # 3) Faz o download para disco, retornando o caminho absoluto
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        abs_path = downloadSnapshot(
            collection=COLLECTION,
            snapshotName=latest
        )
        logging.info(f"Download do snapshot concluído em: {abs_path}")

        # 4) Envia ao S3
        result = upload_file_to_s3(abs_path)
        if result["success"]:
            logging.info(f"Upload concluído: {result['file_url']}")
        else:
            raise RuntimeError(f"Falha no upload: {result['error']}")

    except Exception as e:
        logging.error(f"Erro no ciclo de backup: {e}", exc_info=True)


if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="America/Manaus")

    # Agenda para rodar todo dia às 00:02 (horário Manaus)
    scheduler.add_job(
        do_backup_cycle,
        trigger="cron",
        hour=19, minute=18,
        id="daily_qdrant_backup"
    )

    logging.info("Serviço de backup agendado e em execução.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Serviço de backup finalizado pelo usuário.")
