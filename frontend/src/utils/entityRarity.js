/** Modificateurs CSS partagés pour cadres et puces de filtre. */

const RARITY_FRAME_CLASS = {
  "5★": "rarity-frame--gold",
  "4★": "rarity-frame--purple",
  "3★": "rarity-frame--blue",
  "2★": "rarity-frame--green",
  "1★": "rarity-frame--gray",
};

export function rarityFrameClass(rarity) {
  return RARITY_FRAME_CLASS[String(rarity || "").trim()] ?? "";
}

/** Classe complete pour l'icone de carte (liste). */
export function entityIconRarityClass(rarity) {
  const frame = rarityFrameClass(rarity);
  return frame ? `entity-card__icon ${frame}` : "entity-card__icon";
}

/** Classe de cadre pour avatar planificateur (personnage / arme). */
export function plannerAvatarClass(baseClass, rarity) {
  const frame = rarityFrameClass(rarity);
  return frame ? `${baseClass} ${frame}` : baseClass;
}

/** Theme de puce filtre selon le groupe et la valeur (rarete uniquement). */
export function filterChipThemeClass(groupKey, value) {
  if (groupKey === "rarity") return rarityFrameClass(value);
  return "";
}
