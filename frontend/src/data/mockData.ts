export interface MockProperty {
  id: number;
  area_id: number;
  area_name: string;
  address_raw: string;
  price_eur: number;
  sale_date: string;
  property_type: string;
  lat: number;
  lng: number;
  needs_human_review: boolean;
}

export const MOCK_PROPERTIES: MockProperty[] = [
  { id: 1, area_id: 1, area_name: "Dublin 1", address_raw: "12 O'Connell Street, Dublin 1", price_eur: 385000, sale_date: "2024-03-15", property_type: "Apartment", lat: 53.3490, lng: -6.2605, needs_human_review: false },
  { id: 2, area_id: 1, area_name: "Dublin 1", address_raw: "45 Parnell Street, Dublin 1", price_eur: 420000, sale_date: "2024-01-22", property_type: "Terraced", lat: 53.3505, lng: -6.2630, needs_human_review: false },
  { id: 3, area_id: 1, area_name: "Dublin 1", address_raw: "7 Lower Gardiner Street, Dublin 1", price_eur: 365000, sale_date: "2024-04-10", property_type: "Apartment", lat: 53.3510, lng: -6.2580, needs_human_review: true },
  { id: 4, area_id: 2, area_name: "Dublin 2", address_raw: "88 Baggot Street, Dublin 2", price_eur: 520000, sale_date: "2023-11-30", property_type: "Terraced", lat: 53.3360, lng: -6.2480, needs_human_review: false },
  { id: 5, area_id: 2, area_name: "Dublin 2", address_raw: "15 Merrion Square, Dublin 2", price_eur: 890000, sale_date: "2024-02-14", property_type: "Semi-Detached", lat: 53.3390, lng: -6.2500, needs_human_review: false },
  { id: 6, area_id: 2, area_name: "Dublin 2", address_raw: "32 Fitzwilliam Square, Dublin 2", price_eur: 950000, sale_date: "2023-12-05", property_type: "Detached", lat: 53.3365, lng: -6.2525, needs_human_review: false },
  { id: 7, area_id: 3, area_name: "Dublin 3", address_raw: "56 Clontarf Road, Dublin 3", price_eur: 610000, sale_date: "2024-01-08", property_type: "Semi-Detached", lat: 53.3620, lng: -6.2180, needs_human_review: false },
  { id: 8, area_id: 3, area_name: "Dublin 3", address_raw: "23 Fairview Strand, Dublin 3", price_eur: 445000, sale_date: "2024-03-20", property_type: "Terraced", lat: 53.3580, lng: -6.2410, needs_human_review: false },
  { id: 9, area_id: 4, area_name: "Dublin 4", address_raw: "7 Ailesbury Road, Dublin 4", price_eur: 1450000, sale_date: "2024-05-02", property_type: "Detached", lat: 53.3250, lng: -6.2220, needs_human_review: false },
  { id: 10, area_id: 4, area_name: "Dublin 4", address_raw: "28 Shelbourne Road, Dublin 4", price_eur: 720000, sale_date: "2024-02-28", property_type: "Semi-Detached", lat: 53.3310, lng: -6.2320, needs_human_review: false },
  { id: 11, area_id: 4, area_name: "Dublin 4", address_raw: "91 Pembroke Road, Dublin 4", price_eur: 680000, sale_date: "2023-10-15", property_type: "Terraced", lat: 53.3290, lng: -6.2370, needs_human_review: true },
  { id: 12, area_id: 6, area_name: "Dublin 6", address_raw: "44 Ranelagh Road, Dublin 6", price_eur: 750000, sale_date: "2024-04-18", property_type: "Terraced", lat: 53.3260, lng: -6.2580, needs_human_review: false },
  { id: 13, area_id: 6, area_name: "Dublin 6", address_raw: "12 Dartmouth Road, Dublin 6", price_eur: 820000, sale_date: "2024-01-30", property_type: "Semi-Detached", lat: 53.3230, lng: -6.2630, needs_human_review: false },
  { id: 14, area_id: 6, area_name: "Dublin 6", address_raw: "67 Harold's Cross Road, Dublin 6", price_eur: 495000, sale_date: "2024-03-05", property_type: "Apartment", lat: 53.3190, lng: -6.2770, needs_human_review: false },
  { id: 15, area_id: 8, area_name: "Dublin 8", address_raw: "19 Thomas Street, Dublin 8", price_eur: 380000, sale_date: "2024-02-10", property_type: "Apartment", lat: 53.3430, lng: -6.2770, needs_human_review: false },
  { id: 16, area_id: 8, area_name: "Dublin 8", address_raw: "55 Cork Street, Dublin 8", price_eur: 410000, sale_date: "2024-04-22", property_type: "Terraced", lat: 53.3385, lng: -6.2830, needs_human_review: true },
  { id: 17, area_id: 8, area_name: "Dublin 8", address_raw: "3 Portobello Road, Dublin 8", price_eur: 560000, sale_date: "2023-12-18", property_type: "Semi-Detached", lat: 53.3300, lng: -6.2700, needs_human_review: false },
  { id: 18, area_id: 9, area_name: "Dublin 9", address_raw: "14 Griffith Avenue, Dublin 9", price_eur: 580000, sale_date: "2024-03-28", property_type: "Semi-Detached", lat: 53.3720, lng: -6.2610, needs_human_review: false },
  { id: 19, area_id: 9, area_name: "Dublin 9", address_raw: "88 Drumcondra Road, Dublin 9", price_eur: 465000, sale_date: "2024-01-15", property_type: "Terraced", lat: 53.3680, lng: -6.2540, needs_human_review: false },
  { id: 20, area_id: 9, area_name: "Dublin 9", address_raw: "22 Home Farm Road, Dublin 9", price_eur: 510000, sale_date: "2024-05-08", property_type: "Semi-Detached", lat: 53.3750, lng: -6.2680, needs_human_review: false },
  { id: 21, area_id: 14, area_name: "Dublin 14", address_raw: "5 Mount Anville Road, Dublin 14", price_eur: 920000, sale_date: "2024-02-20", property_type: "Detached", lat: 53.3060, lng: -6.2480, needs_human_review: false },
  { id: 22, area_id: 14, area_name: "Dublin 14", address_raw: "31 Dundrum Road, Dublin 14", price_eur: 780000, sale_date: "2024-04-05", property_type: "Semi-Detached", lat: 53.2950, lng: -6.2490, needs_human_review: false },
  { id: 23, area_id: 14, area_name: "Dublin 14", address_raw: "18 Nutgrove Avenue, Dublin 14", price_eur: 650000, sale_date: "2023-11-12", property_type: "Terraced", lat: 53.2880, lng: -6.2610, needs_human_review: false },
  { id: 24, area_id: 15, area_name: "Dublin 15", address_raw: "44 Castleknock Road, Dublin 15", price_eur: 550000, sale_date: "2024-03-10", property_type: "Detached", lat: 53.3730, lng: -6.3680, needs_human_review: false },
  { id: 25, area_id: 15, area_name: "Dublin 15", address_raw: "12 Blanchardstown Road, Dublin 15", price_eur: 370000, sale_date: "2024-01-25", property_type: "Apartment", lat: 53.3870, lng: -6.3800, needs_human_review: false },
  { id: 26, area_id: 15, area_name: "Dublin 15", address_raw: "67 Ongar Village, Dublin 15", price_eur: 420000, sale_date: "2024-04-30", property_type: "Semi-Detached", lat: 53.3950, lng: -6.4050, needs_human_review: false },
  { id: 27, area_id: 24, area_name: "Dublin 24", address_raw: "9 Tallaght Road, Dublin 24", price_eur: 340000, sale_date: "2024-02-12", property_type: "Terraced", lat: 53.2880, lng: -6.3470, needs_human_review: false },
  { id: 28, area_id: 24, area_name: "Dublin 24", address_raw: "33 Firhouse Road, Dublin 24", price_eur: 395000, sale_date: "2024-05-14", property_type: "Semi-Detached", lat: 53.2780, lng: -6.3420, needs_human_review: false },
  { id: 29, area_id: 24, area_name: "Dublin 24", address_raw: "55 Jobstown, Dublin 24", price_eur: 280000, sale_date: "2023-09-20", property_type: "Apartment", lat: 53.2720, lng: -6.3710, needs_human_review: true },
  { id: 30, area_id: 99, area_name: "Blackrock", address_raw: "23 Rock Road, Blackrock, Co. Dublin", price_eur: 850000, sale_date: "2024-04-25", property_type: "Detached", lat: 53.3010, lng: -6.1780, needs_human_review: false },
  { id: 31, area_id: 99, area_name: "Blackrock", address_raw: "8 Newtown Avenue, Blackrock, Co. Dublin", price_eur: 1100000, sale_date: "2024-03-08", property_type: "Detached", lat: 53.3025, lng: -6.1750, needs_human_review: false },
  { id: 32, area_id: 99, area_name: "Blackrock", address_raw: "45 Carysfort Avenue, Blackrock, Co. Dublin", price_eur: 720000, sale_date: "2024-01-18", property_type: "Semi-Detached", lat: 53.2980, lng: -6.1800, needs_human_review: false },
  { id: 33, area_id: 100, area_name: "Dun Laoghaire", address_raw: "17 Marine Road, Dun Laoghaire, Co. Dublin", price_eur: 680000, sale_date: "2024-02-28", property_type: "Semi-Detached", lat: 53.2930, lng: -6.1370, needs_human_review: false },
  { id: 34, area_id: 100, area_name: "Dun Laoghaire", address_raw: "4 Clarinda Park, Dun Laoghaire, Co. Dublin", price_eur: 920000, sale_date: "2024-05-01", property_type: "Detached", lat: 53.2920, lng: -6.1330, needs_human_review: false },
  { id: 35, area_id: 100, area_name: "Dun Laoghaire", address_raw: "31 George's Street, Dun Laoghaire, Co. Dublin", price_eur: 435000, sale_date: "2023-10-28", property_type: "Apartment", lat: 53.2940, lng: -6.1400, needs_human_review: false },
  { id: 36, area_id: 7, area_name: "Dublin 7", address_raw: "62 Phibsborough Road, Dublin 7", price_eur: 425000, sale_date: "2024-03-22", property_type: "Terraced", lat: 53.3580, lng: -6.2720, needs_human_review: false },
  { id: 37, area_id: 7, area_name: "Dublin 7", address_raw: "18 North Circular Road, Dublin 7", price_eur: 490000, sale_date: "2024-04-11", property_type: "Semi-Detached", lat: 53.3600, lng: -6.2780, needs_human_review: false },
  { id: 38, area_id: 7, area_name: "Dublin 7", address_raw: "5 Stoneybatter, Dublin 7", price_eur: 380000, sale_date: "2023-12-08", property_type: "Apartment", lat: 53.3500, lng: -6.2800, needs_human_review: true },
  { id: 39, area_id: 5, area_name: "Dublin 5", address_raw: "24 Raheny Road, Dublin 5", price_eur: 520000, sale_date: "2024-01-30", property_type: "Semi-Detached", lat: 53.3750, lng: -6.1800, needs_human_review: false },
  { id: 40, area_id: 5, area_name: "Dublin 5", address_raw: "11 Kilbarrack Road, Dublin 5", price_eur: 410000, sale_date: "2024-04-15", property_type: "Terraced", lat: 53.3850, lng: -6.1550, needs_human_review: false },
  { id: 41, area_id: 6, area_name: "Dublin 6W", address_raw: "38 Templeogue Road, Dublin 6W", price_eur: 480000, sale_date: "2024-03-30", property_type: "Semi-Detached", lat: 53.3100, lng: -6.2920, needs_human_review: false },
  { id: 42, area_id: 12, area_name: "Dublin 12", address_raw: "7 Kimmage Road, Dublin 12", price_eur: 395000, sale_date: "2024-02-05", property_type: "Terraced", lat: 53.3220, lng: -6.2950, needs_human_review: false },
  { id: 43, area_id: 12, area_name: "Dublin 12", address_raw: "29 Crumlin Road, Dublin 12", price_eur: 350000, sale_date: "2024-05-20", property_type: "Terraced", lat: 53.3250, lng: -6.3100, needs_human_review: false },
  { id: 44, area_id: 16, area_name: "Dublin 16", address_raw: "13 Ballinteer Road, Dublin 16", price_eur: 590000, sale_date: "2024-04-02", property_type: "Detached", lat: 53.2750, lng: -6.2680, needs_human_review: false },
  { id: 45, area_id: 18, area_name: "Dublin 18", address_raw: "44 Carrickmines, Dublin 18", price_eur: 670000, sale_date: "2024-02-18", property_type: "Semi-Detached", lat: 53.2530, lng: -6.1830, needs_human_review: false },
  { id: 46, area_id: 18, area_name: "Dublin 18", address_raw: "21 Glenageary Road, Dublin 18", price_eur: 780000, sale_date: "2024-01-12", property_type: "Detached", lat: 53.2600, lng: -6.1550, needs_human_review: false },
  { id: 47, area_id: 4, area_name: "Dublin 4", address_raw: "66 Sandymount Avenue, Dublin 4", price_eur: 1300000, sale_date: "2024-05-22", property_type: "Detached", lat: 53.3280, lng: -6.2180, needs_human_review: false },
  { id: 48, area_id: 2, area_name: "Dublin 2", address_raw: "41 Leeson Street, Dublin 2", price_eur: 720000, sale_date: "2024-04-28", property_type: "Semi-Detached", lat: 53.3320, lng: -6.2530, needs_human_review: false },
  { id: 49, area_id: 3, area_name: "Dublin 3", address_raw: "5 Vernon Avenue, Dublin 3", price_eur: 540000, sale_date: "2023-11-15", property_type: "Terraced", lat: 53.3640, lng: -6.2100, needs_human_review: false },
  { id: 50, area_id: 8, area_name: "Dublin 8", address_raw: "78 Francis Street, Dublin 8", price_eur: 360000, sale_date: "2024-03-12", property_type: "Apartment", lat: 53.3410, lng: -6.2750, needs_human_review: false },
];

export const AREA_SCORES_MOCK: Record<number, { affordability: number | null; safety: number | null; livability: number | null; needs_human_review: boolean }> = {
  1: { affordability: 72, safety: 48, livability: 65, needs_human_review: true },
  2: { affordability: 45, safety: 78, livability: 82, needs_human_review: false },
  3: { affordability: 58, safety: 62, livability: 71, needs_human_review: false },
  4: { affordability: 35, safety: 85, livability: 90, needs_human_review: false },
  5: { affordability: 55, safety: 68, livability: 74, needs_human_review: false },
  6: { affordability: 42, safety: 72, livability: 80, needs_human_review: false },
  7: { affordability: 60, safety: 55, livability: 67, needs_human_review: false },
  8: { affordability: 50, safety: 58, livability: 70, needs_human_review: true },
  9: { affordability: 48, safety: 65, livability: 73, needs_human_review: false },
  12: { affordability: 55, safety: 63, livability: 68, needs_human_review: false },
  14: { affordability: 40, safety: 80, livability: 85, needs_human_review: false },
  15: { affordability: 65, safety: 70, livability: 72, needs_human_review: false },
  16: { affordability: 52, safety: 67, livability: 75, needs_human_review: false },
  18: { affordability: 45, safety: 76, livability: 83, needs_human_review: false },
  24: { affordability: 72, safety: 50, livability: 55, needs_human_review: true },
  99: { affordability: 38, safety: 88, livability: 91, needs_human_review: false },
  100: { affordability: 40, safety: 82, livability: 88, needs_human_review: false },
};

export type PropertyType = "Apartment" | "Terraced" | "Semi-Detached" | "Detached";
export type SortOption = "price_asc" | "price_desc" | "recent" | "score";

export interface FilterState {
  minPrice: number | null;
  maxPrice: number | null;
  propertyType: PropertyType | null;
}
