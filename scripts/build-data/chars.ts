import { join } from "node:path";
import { file } from "bun";
import { dataDir } from "../../const";
import { getFuzzyGroups, normalizePinyin } from "./phonology";
import type { WordUnit } from "./types";
import { wordLineToUnit } from "./types";

const file0 = await file(join(dataDir, "/cn/chars.tsv")).text();

const units = file0
  .split("\n")
  .filter((e) => e)
  .map((e) => wordLineToUnit(e));

const charUnitMap = new Map<string, WordUnit[]>();

units.forEach((e) => {
  if (!charUnitMap.has(e.word)) charUnitMap.set(e.word, []);
  e.pinyinN = normalizePinyin(e.pinyin);
  charUnitMap.get(e.word)?.push(e);
});

export { charUnitMap };
