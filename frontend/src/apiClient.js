const CACHE_TTL_MS = 5 * 60 * 1000;
const cache = new Map();

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return res.json();
}

function getCached(url) {
  const hit = cache.get(url);
  if (!hit) return null;
  if (Date.now() - hit.at > CACHE_TTL_MS) {
    cache.delete(url);
    return null;
  }
  return hit.data;
}

function setCached(url, data) {
  cache.set(url, { at: Date.now(), data });
}

async function fetchCached(url) {
  const hit = getCached(url);
  if (hit !== null) return hit;
  const data = await fetchJson(url);
  setCached(url, data);
  return data;
}

/** HTTP client for the Nanoka Planner backend API. */
export const apiClient = {
  characters: () => fetchCached("/api/characters"),
  character: (id) => fetchCached(`/api/characters/${id}`),
  weapons: () => fetchCached("/api/weapons"),
  weapon: (id) => fetchCached(`/api/weapons/${id}`),
};
