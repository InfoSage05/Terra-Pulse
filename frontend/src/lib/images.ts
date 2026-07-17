// Curated, live-verified Unsplash photo IDs (residential exteriors + Dublin/Ireland
// street & skyline shots). The backend has no property/area photo field, so cards
// are assigned a deterministic photo by entity id — same entity always renders the
// same image, and nothing here is a picsum.photos/placeholder URL.

const HOUSE_PHOTO_IDS = [
  "photo-1568605114967-8130f3a36994",
  "photo-1600585154340-be6161a56a0c",
  "photo-1512917774080-9991f1c4c750",
  "photo-1570129477492-45c003edd2be",
  "photo-1600596542815-ffad4c1539a9",
  "photo-1613977257363-707ba9348227",
  "photo-1564013799919-ab600027ffc6",
  "photo-1600607687939-ce8a6c25118c",
  "photo-1590490360182-c33d57733427",
  "photo-1543039625-14cbd3802e7d",
  "photo-1596178060810-72f53ce9a65c",
  "photo-1502005229762-cf1b2da7c5d6",
];

// Only IDs individually visually confirmed as real Dublin/Ireland streetscapes
// belong here - four previously listed IDs turned out to be unrelated stock
// (a bus in snow, a bus on a US street, rolled yoga mats, an alpine chalet)
// despite plausible-sounding filenames, so verify with a real screenshot
// before adding more rather than trusting the ID alone.
const AREA_PHOTO_IDS = [
  "photo-1549918864-48ac978761a4", // Dublin street w/ St. Ann's Church (also used for the hero)
  "photo-1489515217757-5fd1be406fef", // Cobh, Co. Cork - colourful terraced houses + cathedral
];

export const HERO_IMAGE_URL =
  "https://images.unsplash.com/photo-1549918864-48ac978761a4?q=80&w=1920&auto=format&fit=crop";

function pick(ids: string[], seed: number): string {
  const idx = Math.abs(Math.trunc(seed)) % ids.length;
  return ids[idx];
}

export function propertyPhotoUrl(id: number, width = 800): string {
  return `https://images.unsplash.com/${pick(HOUSE_PHOTO_IDS, id)}?q=80&w=${width}&auto=format&fit=crop`;
}

export function areaPhotoUrl(id: number, width = 600): string {
  return `https://images.unsplash.com/${pick(AREA_PHOTO_IDS, id)}?q=80&w=${width}&auto=format&fit=crop`;
}
