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

// Real, individually-screenshot-verified Dublin street photos from Wikimedia
// Commons (public domain / CC-licensed, hotlinkable via Special:FilePath).
// A prior Unsplash-ID-guessing approach here was unreliable - IDs "verified"
// by description alone turned out to be unrelated stock (a bus in snow, a
// beach, a chair, zebras...), and there were only 2 working IDs left, which
// is why every area card rendered the same couple of images. Every URL below
// was fetched and visually confirmed to actually show a Dublin street/square
// before being added.
const AREA_PHOTO_URLS = [
  "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Tara_Street%2C_Dublin_%28DSC06440%29.jpg/960px-Tara_Street%2C_Dublin_%28DSC06440%29.jpg",
  "https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Store_Street%2C_Dublin_%28_DSC6326%29.jpg/960px-Store_Street%2C_Dublin_%28_DSC6326%29.jpg",
  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Moore_Street_market%2C_Dublin.jpg/960px-Moore_Street_market%2C_Dublin.jpg",
  "https://upload.wikimedia.org/wikipedia/commons/thumb/4/49/Dublin_Stephen%27s_Green-44_edit.jpg/960px-Dublin_Stephen%27s_Green-44_edit.jpg",
  "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e8/Dublin_-_Merrion_Square_-_Georgian_Terraced_Houses_-_geograph.org.uk_-_1616458.jpg/960px-Dublin_-_Merrion_Square_-_Georgian_Terraced_Houses_-_geograph.org.uk_-_1616458.jpg",
  "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Rows_of_Georgian_Terrace_Houses_in_Fitzwilliam_St_Dublin_-_panoramio.jpg/960px-Rows_of_Georgian_Terrace_Houses_in_Fitzwilliam_St_Dublin_-_panoramio.jpg",
  "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/2008-05-23_The_Temple_Bar%2C_Dublin%2C_Ireland.jpg/960px-2008-05-23_The_Temple_Bar%2C_Dublin%2C_Ireland.jpg",
];

export const HERO_IMAGE_URL =
  "https://upload.wikimedia.org/wikipedia/commons/thumb/8/86/Tara_Street%2C_Dublin_%28DSC06440%29.jpg/1920px-Tara_Street%2C_Dublin_%28DSC06440%29.jpg";

function pick(items: string[], seed: number): string {
  const idx = Math.abs(Math.trunc(seed)) % items.length;
  return items[idx];
}

export function propertyPhotoUrl(id: number, width = 800): string {
  return `https://images.unsplash.com/${pick(HOUSE_PHOTO_IDS, id)}?q=80&w=${width}&auto=format&fit=crop`;
}

export function areaPhotoUrl(id: number, _width = 600): string {
  // Wikimedia thumbnails are served at fixed widths baked into the URL
  // (see the /960px-.../1920px-... path segments above), unlike Unsplash's
  // ?w= query param, so _width is intentionally unused here.
  return pick(AREA_PHOTO_URLS, id);
}
