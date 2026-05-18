import { join } from "node:path";
import { file } from "bun";
import { dataDir, sourceDir } from "../../const";
import { getFuzzyGroups } from "./phonology";
import type { WordUnit } from "./types";
import { wordUnitToLine } from "./types";

// * --------------------------------

const file1 = await file(join(sourceDir, "/cn/chars-raw.txt")).text();

const chars = file1.split("\n").filter((e) => e);
// const c1 = chars.slice(0, 3500);
// const c2 = chars.slice(3500, 6500);
// const c3 = chars.slice(6500);

// * --------------------------------

const file2 = await file(join(sourceDir, "/cn/chars-tone.txt")).text();

const data = file2
  .split("\n")
  .filter((e) => e)
  .map((line, i) => {
    let [word, pinyin] = line.split("\t");
    pinyin = pinyin.toLowerCase();

    const lvIndex = chars.indexOf(word);
    const level = lvIndex > 6500 ? 3 : lvIndex > 3500 ? 2 : 1;

    const groups = getFuzzyGroups(pinyin);

    const data = { word, pinyin, level, freq: i + 1, groups } satisfies WordUnit;
    return data;
  });

data.push(
  ...["磺 huáng", "矽 xī"].map((e) => {
    const [word, pinyin] = e.split(" ");
    return { word, pinyin, level: 9, freq: 10000, groups: getFuzzyGroups(pinyin) } as WordUnit;
  }),
);

await file(join(dataDir, "/cn/chars.tsv")).write(data.map((e) => wordUnitToLine(e)).join("\n"));
