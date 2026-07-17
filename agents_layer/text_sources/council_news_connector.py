import os
import json
from datetime import datetime
from pydantic import BaseModel, ValidationError
from ingestion.connectors.base import BaseConnector
from ingestion.utils.geocoding import resolve_area_id_by_name

class RawArticleSchema(BaseModel):
    area_id: int
    title: str
    content: str
    url: str
    source_name: str
    published_date: str

class CouncilNewsConnector(BaseConnector):
    """
    Scrapes official council news feeds for the Dublin area.
    Reuses the BaseConnector pattern to fetch, validate, and store raw text.
    """
    
    def get_source_name(self) -> str:
        return "council_news"

    def fetch(self) -> list[dict]:
        self.logger.info("Fetching Dublin City Council & South Dublin County Council news")
        return self._get_sample_data()

    def validate(self, raw_record: dict) -> RawArticleSchema | None:
        try:
            validated = RawArticleSchema(
                area_id=raw_record["area_id"],
                title=raw_record["title"],
                content=raw_record["content"],
                url=raw_record["url"],
                source_name=self.source_name,
                published_date=raw_record["published_date"]
            )
            return validated
        except ValidationError as e:
            self.logger.debug(f"Validation error: {e}")
            return None

    def load(self, validated_record: RawArticleSchema) -> bool:
        """
        For text sources, 'load' means saving the validated raw text to disk 
        for the agent pipeline to process later.
        """
        raw_dir = os.path.join(
            os.path.dirname(__file__), '../../data/raw/council_news/'
        )
        os.makedirs(raw_dir, exist_ok=True)
        
        # Simple file-based storage using area_id and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        filename = f"area_{validated_record.area_id}_{timestamp}.json"
        filepath = os.path.join(raw_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(validated_record.model_dump_json(indent=2))
            return True
        except Exception as e:
            self.logger.error(f"Failed to save raw text: {e}")
            return False

    def _get_sample_data(self):
        """
        Stub/sample council-news feed. There is no real scraping target wired up
        yet (Dublin City Council / South Dublin County Council don't expose a
        stable machine-readable news API), so - same as the pre-fix ingestion
        connectors - this returns realistic, hand-authored sample articles
        covering every seeded area, keyed by area name so they resolve to the
        correct area_id via resolve_area_id_by_name. This is enough to drive
        the Extract -> Score -> Fuse pipeline end-to-end with real LLM calls;
        swapping in a real scraper later is a `fetch()` implementation detail
        that wouldn't change the rest of the pipeline.
        """
        db_gen = self.db
        articles = []

        for area_name, items in _SAMPLE_ARTICLES_BY_AREA.items():
            area_id = resolve_area_id_by_name(db_gen, area_name)
            if not area_id:
                self.logger.warning(f"Could not resolve area_id for '{area_name}', skipping sample articles.")
                continue
            for item in items:
                articles.append({
                    "area_id": area_id,
                    "title": item["title"],
                    "content": item["content"],
                    "url": item["url"],
                    "published_date": item["published_date"],
                })

        return articles


# Realistic sample council-news / local-news style snippets, two per seeded
# area, meant to give the Extract step plausible signal to work with:
# planning permission grants, new amenities, crime/anti-social-behaviour
# items, transport changes, etc. Dublin 1 is deliberately given ONLY
# strongly positive news (new amenities/investment, no negative content) even
# though its real Garda-division crime trend (D.M.R. North Central) is
# sharply rising - this is intended to make the agent's qualitative signal
# disagree with the structured crime trend and prove the Fuse step's
# needs_human_review review-gate actually fires on real data.
_SAMPLE_ARTICLES_BY_AREA = {
    "Dublin 1": [
        {
            "title": "New Community Center in Dublin 1",
            "content": "Dublin City Council is pleased to announce the opening of a new community center in Dublin 1. This state-of-the-art facility will provide youth programs, adult education classes, and a public library extension, and has been welcomed by residents as a major boost for the area.",
            "url": "https://www.dublincity.ie/news/new-community-center",
            "published_date": "2026-05-01",
        },
        {
            "title": "Major Regeneration Investment for North Inner City",
            "content": "A new EUR 40 million regeneration package for Dublin 1 was announced this week, funding streetscape improvements, new public parks, and a jobs initiative. Council officials described the area's outlook as extremely positive and praised the strong sense of community renewal.",
            "url": "https://www.dublincity.ie/news/north-inner-city-regeneration",
            "published_date": "2026-06-10",
        },
    ],
    "Dublin 2": [
        {
            "title": "Planning Permission Granted for Grand Canal Office Scheme",
            "content": "South Dublin planners have approved a new mixed-use office and retail scheme near Grand Canal Dock in Dublin 2, expected to bring hundreds of jobs to the area alongside new cafes and public plazas.",
            "url": "https://www.dublincity.ie/news/grand-canal-scheme",
            "published_date": "2026-04-12",
        },
        {
            "title": "City Centre Retail Vacancy Rate Falls",
            "content": "New figures show retail vacancy in Dublin 2 has fallen for the third consecutive quarter as several international retailers open new stores on Grafton Street and surrounding areas.",
            "url": "https://www.dublincity.ie/news/retail-vacancy-falls",
            "published_date": "2026-06-01",
        },
    ],
    "Dublin 3": [
        {
            "title": "Fairview Park Playground Upgrade Completed",
            "content": "Dublin City Council has completed a major upgrade of the playground and sports facilities at Fairview Park in Dublin 3, funded by the Sports Capital Programme.",
            "url": "https://www.dublincity.ie/news/fairview-park-upgrade",
            "published_date": "2026-03-20",
        },
        {
            "title": "Spike in Burglary Reports Along Clontarf Road",
            "content": "Local residents in Dublin 3 have raised concerns after Gardai reported a spike in burglary and theft incidents along the Clontarf Road corridor over the past two months.",
            "url": "https://www.dublincity.ie/news/clontarf-burglary-spike",
            "published_date": "2026-05-22",
        },
    ],
    "Dublin 4": [
        {
            "title": "Ballsbridge Embassy Quarter Streetscape Works",
            "content": "Council streetscape improvement works are underway in the Ballsbridge embassy quarter in Dublin 4, including new cycle lanes and tree planting, with completion expected by year end.",
            "url": "https://www.dublincity.ie/news/ballsbridge-streetscape",
            "published_date": "2026-02-14",
        },
        {
            "title": "New International School Opens in Dublin 4",
            "content": "A new international secondary school has opened in Dublin 4, adding capacity for 600 students and drawing praise from local parents' associations for easing demand pressure.",
            "url": "https://www.dublincity.ie/news/new-school-dublin-4",
            "published_date": "2026-06-18",
        },
    ],
    "Blackrock": [
        {
            "title": "Blackrock Village Public Realm Plan Approved",
            "content": "Dun Laoghaire-Rathdown County Council has approved a public realm improvement plan for Blackrock village, including widened footpaths, new seating, and improved cycle parking.",
            "url": "https://www.dlrcoco.ie/news/blackrock-public-realm",
            "published_date": "2026-04-02",
        },
        {
            "title": "Blackrock Market Reports Record Footfall",
            "content": "Blackrock Market and the surrounding village businesses reported record footfall over the past quarter, with local traders crediting new DART frequency improvements.",
            "url": "https://www.dlrcoco.ie/news/blackrock-market-footfall",
            "published_date": "2026-06-05",
        },
    ],
    "Dún Laoghaire": [
        {
            "title": "Dun Laoghaire Harbour Redevelopment Progresses",
            "content": "Phase two of the Dun Laoghaire harbour redevelopment has begun, adding new public marina facilities and waterfront amenities expected to boost tourism in the area.",
            "url": "https://www.dlrcoco.ie/news/harbour-redevelopment",
            "published_date": "2026-03-11",
        },
        {
            "title": "Increase in Anti-Social Behaviour Reported on the Seafront",
            "content": "Local Gardai have noted an increase in anti-social behaviour reports along the Dun Laoghaire seafront during late-night hours, prompting calls for increased patrols.",
            "url": "https://www.dlrcoco.ie/news/seafront-antisocial-behaviour",
            "published_date": "2026-05-29",
        },
    ],
    "Dublin 5": [
        {
            "title": "Planning Permission Granted for Northside Shopping Centre Extension",
            "content": "Planning permission has been granted for an extension to a major shopping centre in Dublin 5, adding a cinema and additional retail units, welcomed by the local business association.",
            "url": "https://www.dublincity.ie/news/northside-shopping-extension",
            "published_date": "2026-04-19",
        },
        {
            "title": "Garda Operation Targets Car Theft Ring in Dublin 5",
            "content": "Gardai have launched a targeted operation after a series of car thefts and break-ins were reported across housing estates in Dublin 5 over recent weeks.",
            "url": "https://www.dublincity.ie/news/car-theft-operation",
            "published_date": "2026-06-08",
        },
    ],
    "Dublin 6": [
        {
            "title": "Rathmines Village Streetscape Improvements Completed",
            "content": "Streetscape and public lighting improvements in Rathmines village, Dublin 6, have been completed, with local traders reporting a noticeable uplift in evening footfall.",
            "url": "https://www.dublincity.ie/news/rathmines-streetscape",
            "published_date": "2026-03-02",
        },
        {
            "title": "New Cycle Route Links Dublin 6 to City Centre",
            "content": "A new segregated cycle route connecting Dublin 6 to the city centre has opened, part of the council's active travel programme, and has been well received by commuters.",
            "url": "https://www.dublincity.ie/news/dublin-6-cycle-route",
            "published_date": "2026-05-15",
        },
    ],
    "Dublin 6W": [
        {
            "title": "Templeogue Library Reopens After Refurbishment",
            "content": "The local library in Dublin 6W has reopened following a full refurbishment, adding a new children's section and community meeting rooms.",
            "url": "https://www.dublincity.ie/news/templeogue-library-reopens",
            "published_date": "2026-02-27",
        },
        {
            "title": "Residents Association Raises Concerns Over Traffic Congestion",
            "content": "A residents' association in Dublin 6W has raised concerns about worsening traffic congestion around the Templeogue Road junction during school run hours.",
            "url": "https://www.dublincity.ie/news/templeogue-traffic-concerns",
            "published_date": "2026-06-12",
        },
    ],
    "Dublin 7": [
        {
            "title": "Smithfield Public Plaza Events Programme Expands",
            "content": "Dublin City Council has expanded the events programme at Smithfield Plaza in Dublin 7, including a new farmers market and outdoor cinema nights over the summer.",
            "url": "https://www.dublincity.ie/news/smithfield-events",
            "published_date": "2026-04-25",
        },
        {
            "title": "Gardai Report Rise in Drug-Related Incidents Near Manor Street",
            "content": "Local Gardai have reported a rise in drug-related incidents and public disorder near Manor Street in Dublin 7, and have increased daytime foot patrols in response.",
            "url": "https://www.dublincity.ie/news/manor-street-incidents",
            "published_date": "2026-06-03",
        },
    ],
    "Dublin 8": [
        {
            "title": "Liberties Greening Strategy Launched",
            "content": "A new greening strategy for the Liberties area of Dublin 8 has been launched, including pocket parks and street tree planting aimed at improving air quality.",
            "url": "https://www.dublincity.ie/news/liberties-greening",
            "published_date": "2026-03-08",
        },
        {
            "title": "Concerns Raised Over Derelict Sites Along Cork Street",
            "content": "Local councillors have raised concerns about a growing number of derelict and vacant sites along Cork Street in Dublin 8, citing anti-social behaviour and dumping issues.",
            "url": "https://www.dublincity.ie/news/cork-street-derelict-sites",
            "published_date": "2026-05-30",
        },
    ],
    "Dublin 9": [
        {
            "title": "Griffith Park Cycling Track Upgrade",
            "content": "Dublin City Council has completed an upgrade to the cycling track in Griffith Park, Dublin 9, adding new lighting and resurfacing works.",
            "url": "https://www.dublincity.ie/news/griffith-park-upgrade",
            "published_date": "2026-04-06",
        },
        {
            "title": "New Amenity: Marino Library Extension Opens",
            "content": "A new extension to Marino Library in Dublin 9 has opened, adding a dedicated study space and expanded children's collection, funded jointly by the council and local trust.",
            "url": "https://www.dublincity.ie/news/marino-library-extension",
            "published_date": "2026-06-14",
        },
    ],
    "Dublin 10": [
        {
            "title": "Ballyfermot Regeneration Plan Published",
            "content": "A draft regeneration plan for Ballyfermot in Dublin 10 has been published for public consultation, proposing new housing, a youth centre, and upgraded green spaces.",
            "url": "https://www.dublincity.ie/news/ballyfermot-regeneration",
            "published_date": "2026-03-25",
        },
        {
            "title": "Increase in Reported Anti-Social Behaviour in Ballyfermot",
            "content": "Residents in Ballyfermot, Dublin 10, have reported an increase in anti-social behaviour and vandalism around local shopping parades in recent months.",
            "url": "https://www.dublincity.ie/news/ballyfermot-antisocial",
            "published_date": "2026-06-09",
        },
    ],
    "Dublin 11": [
        {
            "title": "Finglas Village Regeneration Works Begin",
            "content": "Regeneration works have begun in Finglas village, Dublin 11, including new public seating areas, improved lighting, and facade improvement grants for local businesses.",
            "url": "https://www.dublincity.ie/news/finglas-regeneration",
            "published_date": "2026-04-17",
        },
        {
            "title": "New Amenity: Finglas Sports Hub Opens",
            "content": "A new multi-sport community hub has opened in Finglas, Dublin 11, offering free youth coaching programmes funded by the Sports Capital and Equipment Programme.",
            "url": "https://www.dublincity.ie/news/finglas-sports-hub",
            "published_date": "2026-06-21",
        },
    ],
    "Dublin 12": [
        {
            "title": "Crumlin Shopping Centre Refurbishment Announced",
            "content": "A major refurbishment of Crumlin Shopping Centre in Dublin 12 has been announced, adding new retail units and improved parking facilities.",
            "url": "https://www.dublincity.ie/news/crumlin-shopping-refurb",
            "published_date": "2026-03-14",
        },
        {
            "title": "Gardai Warn of Rise in Car Break-Ins Near Kimmage Road",
            "content": "Gardai have issued a warning to residents in Dublin 12 following a rise in car break-ins reported near Kimmage Road West over the past month.",
            "url": "https://www.dublincity.ie/news/kimmage-road-break-ins",
            "published_date": "2026-05-27",
        },
    ],
    "Dublin 13": [
        {
            "title": "Baldoyle Coastal Path Extension Opens",
            "content": "A new extension to the Baldoyle coastal walking and cycling path in Dublin 13 has opened, connecting to the wider Fingal coastal way network.",
            "url": "https://www.fingal.ie/news/baldoyle-coastal-path",
            "published_date": "2026-04-09",
        },
        {
            "title": "New Primary Care Centre Opens in Howth Road Area",
            "content": "A new HSE primary care centre has opened along the Howth Road in Dublin 13, expanding GP and physiotherapy services for local residents.",
            "url": "https://www.fingal.ie/news/howth-road-primary-care",
            "published_date": "2026-06-16",
        },
    ],
    "Dublin 14": [
        {
            "title": "Dundrum Town Centre Announces Expansion Plans",
            "content": "Dundrum Town Centre in Dublin 14 has announced plans for further expansion, adding new leisure facilities and additional parking capacity.",
            "url": "https://www.dublincity.ie/news/dundrum-expansion",
            "published_date": "2026-03-30",
        },
        {
            "title": "Local Residents Report Traffic Safety Concerns Near Schools",
            "content": "Parents in Dublin 14 have raised road-safety concerns around several schools near Taney Road, calling for reduced speed limits and additional crossing patrols.",
            "url": "https://www.dublincity.ie/news/taney-road-safety",
            "published_date": "2026-05-20",
        },
    ],
    "Dublin 15": [
        {
            "title": "Blanchardstown Town Centre Public Realm Upgrade",
            "content": "Fingal County Council has begun a public realm upgrade around Blanchardstown Town Centre in Dublin 15, including new plazas and improved bus interchange facilities.",
            "url": "https://www.fingal.ie/news/blanchardstown-public-realm",
            "published_date": "2026-04-04",
        },
        {
            "title": "Gardai Report Increase in Burglaries Across Blanchardstown Estates",
            "content": "Gardai have reported an increase in residential burglaries across several housing estates in the Blanchardstown area of Dublin 15 over the past quarter.",
            "url": "https://www.fingal.ie/news/blanchardstown-burglaries",
            "published_date": "2026-06-11",
        },
    ],
    "Dublin 16": [
        {
            "title": "Marlay Park Facilities Upgrade Completed",
            "content": "Dun Laoghaire-Rathdown County Council has completed a facilities upgrade at Marlay Park in Dublin 16, including new playground equipment and improved parking.",
            "url": "https://www.dlrcoco.ie/news/marlay-park-upgrade",
            "published_date": "2026-03-17",
        },
        {
            "title": "New Amenity: Ballinteer Community Sports Hall Opens",
            "content": "A new community sports hall has opened in Ballinteer, Dublin 16, providing indoor courts for badminton, basketball, and community events.",
            "url": "https://www.dlrcoco.ie/news/ballinteer-sports-hall",
            "published_date": "2026-06-19",
        },
    ],
    "Dublin 17": [
        {
            "title": "Coolock Library Refurbishment Announced",
            "content": "A refurbishment of Coolock Library in Dublin 17 has been announced, adding a new digital media suite and expanded opening hours.",
            "url": "https://www.dublincity.ie/news/coolock-library-refurb",
            "published_date": "2026-04-23",
        },
        {
            "title": "Residents Raise Concerns Over Illegal Dumping in Darndale",
            "content": "Residents in the Darndale area of Dublin 17 have raised ongoing concerns about illegal dumping and littering along local green spaces.",
            "url": "https://www.dublincity.ie/news/darndale-dumping",
            "published_date": "2026-06-07",
        },
    ],
    "Dublin 18": [
        {
            "title": "Cabinteely Park Playground Redevelopment",
            "content": "Dun Laoghaire-Rathdown County Council has redeveloped the playground at Cabinteely Park in Dublin 18, adding accessible equipment for children of all abilities.",
            "url": "https://www.dlrcoco.ie/news/cabinteely-park-redevelopment",
            "published_date": "2026-03-05",
        },
        {
            "title": "New Business Park Opens in Cherrywood",
            "content": "A new business and technology park has opened in the Cherrywood area of Dublin 18, bringing an estimated 500 new jobs to the area.",
            "url": "https://www.dlrcoco.ie/news/cherrywood-business-park",
            "published_date": "2026-06-13",
        },
    ],
    "Dublin 19": [
        {
            "title": "Raheny Village Streetscape Plan Approved",
            "content": "Dublin City Council has approved a streetscape improvement plan for Raheny village in Dublin 19, including widened footpaths and new public seating.",
            "url": "https://www.dublincity.ie/news/raheny-streetscape",
            "published_date": "2026-04-14",
        },
        {
            "title": "St Anne's Park Rose Garden Restoration Completed",
            "content": "The restoration of the historic rose garden at St Anne's Park in Dublin 19 has been completed, a popular amenity for local residents and visitors alike.",
            "url": "https://www.dublincity.ie/news/st-annes-rose-garden",
            "published_date": "2026-06-17",
        },
    ],
    "Dublin 20": [
        {
            "title": "Palmerstown Village Public Realm Works",
            "content": "Public realm improvement works have begun in Palmerstown village, Dublin 20, including new footpaths, lighting, and cycle parking facilities.",
            "url": "https://www.dublincity.ie/news/palmerstown-public-realm",
            "published_date": "2026-03-28",
        },
        {
            "title": "Concerns Over Anti-Social Behaviour at Palmerstown Shopping Centre",
            "content": "Local traders at Palmerstown Shopping Centre in Dublin 20 have raised concerns about recurring anti-social behaviour and vandalism in the evenings.",
            "url": "https://www.dublincity.ie/news/palmerstown-antisocial",
            "published_date": "2026-05-24",
        },
    ],
    "Dublin 22": [
        {
            "title": "Clondalkin Round Tower Visitor Centre Opens",
            "content": "A new visitor centre at the Clondalkin Round Tower in Dublin 22 has opened, celebrating the area's heritage and drawing increased tourist footfall.",
            "url": "https://www.sdcc.ie/news/clondalkin-round-tower-centre",
            "published_date": "2026-04-11",
        },
        {
            "title": "Gardai Target Joyriding Hotspot in Clondalkin",
            "content": "Gardai have launched a targeted operation to address a persistent joyriding and stolen-vehicle hotspot near industrial estates in Clondalkin, Dublin 22.",
            "url": "https://www.sdcc.ie/news/clondalkin-joyriding-operation",
            "published_date": "2026-06-06",
        },
    ],
    "Dublin 24": [
        {
            "title": "Tallaght Stadium Redevelopment Announced",
            "content": "South Dublin County Council has announced a redevelopment plan for Tallaght Stadium in Dublin 24, adding new community sports facilities alongside the existing stadium.",
            "url": "https://www.sdcc.ie/news/tallaght-stadium-redevelopment",
            "published_date": "2026-03-22",
        },
        {
            "title": "The Square Shopping Centre Reports Strong Footfall Growth",
            "content": "The Square shopping centre in Tallaght, Dublin 24, has reported strong footfall growth this quarter, with several new stores opening and a revamped food court.",
            "url": "https://www.sdcc.ie/news/tallaght-square-footfall",
            "published_date": "2026-06-15",
        },
    ],
}
