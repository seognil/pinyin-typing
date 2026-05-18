import { join } from "node:path";
import { file } from "bun";
import { dataDir, sourceDir } from "../../const";
import { charUnitMap } from "./chars";
import { getFuzzyGroups, normalizePinyin } from "./phonology";
import type { WordUnit } from "./types";
import { wordUnitToLine } from "./types";

// * ------------------------------------------------

function rebuildWordPinyin(word: string, pinyin: string) {
  const chars = [...word];
  if (chars.length === 1) return [word, pinyin];

  let restPy = pinyin;
  let restPyN = normalizePinyin(restPy);
  const pys: string[] = [];

  chars.forEach((c) => {
    restPy = restPy.replace(/^(-|·|’|'|\s|\/\/)+/, "");
    restPyN = restPyN.replace(/^(-|·|’|'|\s|\/\/)+/, "");

    const u = charUnitMap.get(c)!;
    const py = u.findLast((e) => restPyN.startsWith(e.pinyinN ?? ""))?.pinyin;
    if (py) {
      pys.push(restPy.slice(0, py.length));
      restPy = restPy.slice(py.length);
      restPyN = restPyN.slice(py.length);
    }
  });

  // 省略儿化音
  if (word.at(-1) === "儿" && restPy === "r") return [word.slice(0, -1), pys.join(" ")];

  // ! debug
  if (restPy.length) {
    console.error(word, pys, pinyin, restPy, restPyN);
    throw Error("Check Dirty Word");
  }

  return [word, pys.join(" ")];
}

// * ------------------------------------------------ build data

const file1 = await file(join(sourceDir, "/cn/edu.tsv")).text();

const data = file1
  .split("\n")
  .filter((e) => e)
  .slice(1)
  .map((e, i) => {
    const [word, pinyin, part, level] = e.split("\t");
    const [wordClean, pinyinClean] = rebuildWordPinyin(word, pinyin.toLowerCase());

    return {
      word: wordClean,
      pinyin: pinyinClean,
      level: Number(level),
      freq: i + 1,
      groups: getFuzzyGroups(pinyinClean),
    } as WordUnit;
  })
  .filter((e) => e.word.length > 1);

const uniqData = Array.from(new Map(data.map((e) => [e.word, e])).values()).sort(
  (a, b) => a.word.length - b.word.length || a.level - b.level || a.freq - b.freq,
);

await file(join(dataDir, "/cn/edu.tsv")).write(uniqData.map((e) => wordUnitToLine(e)).join("\n"));
