// Every row in this dataset (Ireland's Property Price Register) is already
// a completed historical sale - there's no live "currently for sale" feed
// in this project, so there's no genuine sold-vs-available split to color.
// Recency of sale is the real, honest signal available instead: a recent
// sale suggests an active market in that area, an older one less so.
const RECENT_SALE_WINDOW_DAYS = 90;

export function isRecentSale(saleDate: string | null | undefined): boolean {
  if (!saleDate) return false;
  const sold = new Date(saleDate);
  if (isNaN(sold.getTime())) return false;
  const daysSince = (Date.now() - sold.getTime()) / (1000 * 60 * 60 * 24);
  return daysSince >= 0 && daysSince <= RECENT_SALE_WINDOW_DAYS;
}
