/** Agrege matériaux / EXP jusqu'a un niveau cible. */

function addMaterial(map, mat) {
  const name = String(mat.name || "").trim();
  if (!name) return;
  const key = `${name}|${mat.item_id ?? ""}`;
  const prev = map.get(key) || {
    name,
    count: 0,
    item_id: mat.item_id,
    icon_url: mat.icon_url || "",
  };
  prev.count += Number(mat.count) || 0;
  map.set(key, prev);
}

function addBooksOrOres(map, items) {
  for (const row of items || []) {
    addMaterial(map, {
      name: row.name,
      count: row.count,
      item_id: row.item_id,
      icon_url: row.icon_url || "",
    });
  }
}

export function mergeMaterialMaps(maps) {
  const out = new Map();
  for (const m of maps) {
    for (const [k, v] of m) {
      const prev = out.get(k) || { ...v, count: 0 };
      prev.count += v.count;
      out.set(k, prev);
    }
  }
  return [...out.values()].sort((a, b) => a.name.localeCompare(b.name, "en"));
}

export const ASCENSION_LEVELS = [1, 20, 40, 50, 60, 70, 80, 90];
/** Paliers talent : 1 = niveau de base (aucun matériau). */
export const TALENT_LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

export function aggregateAscensionReport(asc, targetLevel, variant) {
  const materials = new Map();
  let ascensionMora = 0;
  let levelingMora = 0;

  for (const phase of asc.ascensions || []) {
    const cap = Number(phase.at_level) || 0;
    if (cap > targetLevel) continue;

    ascensionMora += Number(phase.mora) || 0;
    for (const m of phase.materials || []) addMaterial(materials, m);

    const lv = phase.leveling;
    if (lv && Number(lv.to_level) <= targetLevel) {
      levelingMora += Number(lv.mora_cost) || 0;
      if (variant === "character") addBooksOrOres(materials, lv.books);
      else addBooksOrOres(materials, lv.ores);
    }
  }

  const after = asc.leveling_after_last_ascension;
  if (after && targetLevel >= 90 && Number(after.to_level) <= targetLevel) {
    levelingMora += Number(after.mora_cost) || 0;
    addBooksOrOres(materials, after.ores);
  }

  return {
    materials: [...materials.values()].sort((a, b) => a.name.localeCompare(b.name, "en")),
    ascensionMora,
    levelingMora,
    totalMora: ascensionMora + levelingMora,
  };
}

function aggregateTalentTrack(track, targetLevel) {
  const trackNum = Number(track.track) || 0;
  if (targetLevel <= 1) {
    return { track: trackNum, materials: [], totalMora: 0 };
  }

  const materials = new Map();
  let totalMora = 0;

  for (const level of track.levels || []) {
    if (Number(level.level) > targetLevel) continue;
    totalMora += Number(level.mora ?? level.mora) || 0;
    for (const m of level.materials || []) addMaterial(materials, m);
  }

  return {
    track: trackNum,
    materials: [...materials.values()].sort((a, b) => a.name.localeCompare(b.name, "en")),
    totalMora,
  };
}

function resolveTrackLevel(levelsByTrack, trackNum) {
  if (levelsByTrack instanceof Map) {
    return levelsByTrack.get(trackNum) ?? levelsByTrack.get(String(trackNum));
  }
  return levelsByTrack[trackNum] ?? levelsByTrack[String(trackNum)];
}

/** Agrégation avec un niveau cible par piste (`Map` ou objet `{ [track]: level }`). */
export function aggregateTalentReportWithLevels(report, levelsByTrack) {
  const tracks = (report.talents || []).map((track) => {
    const trackNum = Number(track.track) || 0;
    const targetLevel = resolveTrackLevel(levelsByTrack, trackNum) ?? TALENT_LEVELS[0];
    return aggregateTalentTrack(track, targetLevel);
  });
  const totalMaterials = new Map();
  let totalMora = 0;
  for (const track of tracks) {
    totalMora += track.totalMora;
    for (const mat of track.materials) addMaterial(totalMaterials, mat);
  }
  const materials = [...totalMaterials.values()].sort((a, b) => a.name.localeCompare(b.name, "en"));

  return { tracks, total: { materials, totalMora } };
}

/** Même niveau pour toutes les pistes (rétrocompatibilité). */
export function aggregateTalentReportDetailed(report, targetLevel) {
  const levelsByTrack = {};
  for (const track of report.talents || []) {
    const trackNum = Number(track.track) || 0;
    levelsByTrack[trackNum] = targetLevel;
  }
  return aggregateTalentReportWithLevels(report, levelsByTrack);
}

export function aggregateTalentReport(report, targetLevel) {
  const { total } = aggregateTalentReportDetailed(report, targetLevel);
  return {
    materials: total.materials,
    totalMora: total.totalMora,
    ascensionMora: 0,
    levelingMora: total.totalMora,
  };
}

export function nearestMilestone(levels, value) {
  return levels.reduce((best, lv) => (Math.abs(lv - value) < Math.abs(best - value) ? lv : best), levels[0]);
}
