const STATIC_GI = "https://static.nanoka.cc/assets/gi";

const KNOWN_ITEM_IDS = {
  "Hero's Wit": 104003,
  "Adventurer's Experience": 104002,
  "Wanderer's Advice": 104001,
  "Mystic Enhancement Ore": 104013,
  "Fine Enhancement Ore": 104012,
  "Enhancement Ore": 104011,
};

/** URL d'icône pour une carte matériau (API ou fallback Nanoka static). */
export function resolveMaterialIcon(mat) {
  if (mat?.icon_url) return mat.icon_url;
  const id = mat?.item_id ?? KNOWN_ITEM_IDS[mat?.name];
  if (id != null && String(id).trim() !== "") {
    return `${STATIC_GI}/UI_ItemIcon_${id}.webp`;
  }
  return "";
}
