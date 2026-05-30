const STATIC_GI = "https://static.nanoka.cc/assets/gi";

/** Icones d'attaque normale generiques par type d'arme (assets GI). */
const WEAPON_TYPE_ICONS = {
  Sword: `${STATIC_GI}/Skill_A_01.webp`,
  Bow: `${STATIC_GI}/Skill_A_02.webp`,
  Polearm: `${STATIC_GI}/Skill_A_03.webp`,
  Claymore: `${STATIC_GI}/Skill_A_04.webp`,
  Catalyst: `${STATIC_GI}/Skill_A_Catalyst_MD.webp`,
};

export function weaponTypeIconUrl(weaponType) {
  return WEAPON_TYPE_ICONS[String(weaponType || "").trim()] ?? "";
}
