import time
import logging

from storage.scripts.db_connect import get_db
from storage.models.db_models import Area, AreaAgentSummary
from agents_layer.jobs.run_agent_pipeline import run_agent_pipeline
from agents_layer.text_sources.council_news_connector import CouncilNewsConnector

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def main():
    db = next(get_db())
    CouncilNewsConnector(db).run()

    done_ids = {r[0] for r in db.query(AreaAgentSummary.area_id).distinct().all()}
    areas = db.query(Area).filter(~Area.id.in_(done_ids)).all() if done_ids else db.query(Area).all()
    print(f"Remaining areas to process: {len(areas)}", flush=True)

    for area in areas:
        print(f"Processing area {area.id} - {area.name}", flush=True)
        run_agent_pipeline(area.id, run_connector=False)
        time.sleep(2)

    print("BATCH_DONE", flush=True)


if __name__ == "__main__":
    main()
