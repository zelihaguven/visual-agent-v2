import { describe, expect, it } from "vitest";

import { groupDocuments, groupOf, readableName } from "./documentGroups";

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
    const groups = groupDocuments([{ filename: "x.sql" }, { filename: "y.pdf" }, { filename: "z.pdf" }]);

    expect(groups.map((entry) => [entry.group, entry.documents.length])).toEqual([
      ["PDF", 2],
      ["SQL", 1],
    ]);
  });
});

describe("readableName", () => {
  it.each([
    ["dikim-excel", "dikim excel"],
    ["08_Setup_part1.md", "08 Setup part1"],
    ["PNT-1126 ölçü föyü", "PNT-1126 ölçü föyü"],
    ["Main Menu - Setup", "Main Menu - Setup"],
  ])("reads %s as %s", (title, readable) => {
    expect(readableName(title)).toBe(readable);
  });
});
