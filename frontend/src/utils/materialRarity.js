/** Heuristique de bordure carte (style Genshin). */
export function materialRarityClass(name) {
  const n = String(name).toLowerCase();
  if (n.includes("mora")) return "material-card--gold";
  if (
    /gem|diamond|lazurite|jade|agate|turquoise|amethyst|topaz|sapphire|emerald|ruby|silver|gold/.test(n)
  ) {
    return "material-card--gold";
  }
  if (
    /hero's wit|adventurer|wanderer|mystic enhancement|fine enhancement|enhancement ore/.test(n)
  ) {
    return "material-card--purple";
  }
  if (/chunk|fragment|sliver|dust|shimmering|glowing|brilliant|tile|debris|piece/.test(n)) {
    return "material-card--teal";
  }
  return "material-card--blue";
}
