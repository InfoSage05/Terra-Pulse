# TerraPulse Data Sources

Registry of all external data sources used by the TerraPulse ingestion layer.

## 1. Residential Property Price Register (PSRA)
- **Primary URL**: https://www.propertypriceregister.ie/
- **Alternative API**: https://priceregister.civictech.ie/ (Note: CivicTech API currently returns 404, fallback to CSV parsing used).
- **Access Restrictions**: Official CSVs are publicly available. Use CP1252 encoding.
- **Last Checked**: June 2026

## 2. OpenStreetMap (OSM)
- **Overpass API Endpoint**: https://overpass-api.de/api/interpreter
- **Access Restrictions**: Public API. Heavily rate limited. Ensure queries are scoped to bounding boxes and timeouts are set appropriately.
- **Last Checked**: June 2026

## 3. Central Statistics Office (CSO)
- **Data Portal**: https://data.cso.ie/
- **Access Restrictions**: Public PxStat API for Census tables. (Stub implementation currently used).
- **Last Checked**: June 2026

## 4. Crime Statistics (Garda)
- **Data Portal**: https://data.cso.ie/ (Recorded Crime)
- **Access Restrictions**: Available at Garda Division level only (coarser than postal districts or small areas).
- **Last Checked**: June 2026
