import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

describe("apiClient cache", () => {
  beforeEach(() => {
    vi.resetModules();
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetches once and serves cached responses", async () => {
    const payload = [{ id: "1", name: "Tester" }];
    fetch.mockResolvedValue({
      ok: true,
      json: async () => payload,
    });

    const { apiClient } = await import("../src/apiClient.js");
    await expect(apiClient.characters()).resolves.toEqual(payload);
    await expect(apiClient.characters()).resolves.toEqual(payload);
    expect(fetch).toHaveBeenCalledTimes(1);
    expect(fetch).toHaveBeenCalledWith("/api/characters");
  });

  it("throws when the response is not ok", async () => {
    fetch.mockResolvedValue({
      ok: false,
      status: 500,
      text: async () => "Server error",
    });

    const { apiClient } = await import("../src/apiClient.js");
    await expect(apiClient.weapon("11401")).rejects.toThrow("Server error");
  });
});
