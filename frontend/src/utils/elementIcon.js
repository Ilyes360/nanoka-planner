const STATIC_GI = "https://static.nanoka.cc/assets/gi";

/** Icones elementaires (meme convention que gi.nanoka.cc). */
const ELEMENT_ICONS = {
  Pyro: `${STATIC_GI}/Pyro.webp`,
  Hydro: `${STATIC_GI}/Hydro.webp`,
  Electro: `${STATIC_GI}/Electro.webp`,
  Cryo: `${STATIC_GI}/Cryo.webp`,
  Anemo: `${STATIC_GI}/Anemo.webp`,
  Geo: `${STATIC_GI}/Geo.webp`,
  Dendro: `${STATIC_GI}/Dendro.webp`,
};

export function elementIconUrl(element) {
  return ELEMENT_ICONS[String(element || "").trim()] ?? "";
}
