import { describe, expect, it } from "vitest";

import { groupDocuments, groupOf } from "./documentGroups";

describe("groupOf", () => {
  it.each([
    ["a.PDF", "PDF"],
    ["b.docx", "Word"],
    ["c.rtf", "Word"],
    ["d.xls", "Excel"],
    ["e.md", "Markdown"],
    ["f.sql", "SQL"],
    ["g.tiff", "Görsel"],
    ["h.pptx", "Diğer"],
    ["adsiz", "Diğer"],
  ])("puts %s under %s", (filename, group) => {
    expect(groupOf(filename)).toBe(group);
  });
});

describe("groupDocuments", () => {
  it("keeps a fixed group order and leaves out empty groups", () => {
    const groups = groupDocuments([
      { filename: "x.sql" },
      { filename: "y.pdf" },
      { filename: "z.pdf" },
    ]);

    expect(
      groups.map((entry) => [entry.group, entry.documents.length]),
    ).toEqual([
      ["PDF", 2],
      ["SQL", 1],
    ]);
  });
});

describe("groupDocuments by topic", () => {
  it("groups by topic first and keeps documents without a topic under their file type", () => {
    const groups = groupDocuments([
      { filename: "a.pdf", topic: "Ürün ölçü föyleri" },
      { filename: "b.md", topic: "Yazılım kullanım kılavuzu" },
      { filename: "c.pdf", topic: "Ürün ölçü föyleri" },
      { filename: "d.xlsx", topic: null },
      { filename: "e.docx" },
    ]);

    expect(
      groups.map((entry) => [entry.group, entry.documents.length]),
    ).toEqual([
      ["Ürün ölçü föyleri", 2],
      ["Yazılım kullanım kılavuzu", 1],
      ["Word", 1],
      ["Excel", 1],
    ]);
  });
});
