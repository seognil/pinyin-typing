import { join } from "node:path";
import { file } from "bun";
import { dataDir, sourceDir } from "../../const";
import { charUnitMap } from "./chars";
import { getFuzzyGroups } from "./phonology";
import type { WordUnit } from "./types";
import { wordUnitToLine } from "./types";

// * ------------------------------------------------ build data

const eduWords = new Set(
  await file(join(sourceDir, "/cn/edu.tsv"))
    .text()
    .then((e) =>
      e
        .split("\n")
        .filter((e) => e)
        .map((e) => e.split("\t")[0]),
    ),
);

const modernWords = new Set(
  await file(join(sourceDir, "/cn/modern.tsv"))
    .text()
    .then((e) =>
      e
        .split("\n")
        .filter((e) => e)
        .map((e) => e.split("\t")[1]),
    ),
);

const file3: Record<string, string[][]> = await file(join(sourceDir, "/cn/phrase.json")).json();

const data = Object.entries(file3)
  .map(([word, pys], i) => {
    const pinyin = pys.flat().join(" ");
    const level = Math.max(...[...word].map((e) => charUnitMap.get(e)?.at(0)?.level ?? 9));

    return {
      word: word,
      pinyin: pinyin,
      level: level,
      freq: i + 1,
      groups: getFuzzyGroups(pinyin),
    } as WordUnit;
  })

  .filter((e) => e.word.length > 1)
  .filter((e) => !eduWords.has(e.word))
  .filter((e) => !modernWords.has(e.word));

const uniqData = Array.from(new Map(data.map((e) => [e.word, e])).values()).sort(
  (a, b) => a.word.length - b.word.length || a.level - b.level || a.freq - b.freq,
);

await file(join(dataDir, "/cn/phrase.tsv")).write(uniqData.map((e) => wordUnitToLine(e)).join("\n"));
