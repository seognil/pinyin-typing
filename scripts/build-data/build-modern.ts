import { join } from "node:path";
import { file } from "bun";
import { dataDir, sourceDir } from "../../const";
import { charUnitMap } from "./chars";
import { getFuzzyGroups, normalizePinyin } from "./phonology";
import type { WordUnit } from "./types";
import { wordUnitToLine } from "./types";

// * ------------------------------------------------

function rebuildWordPinyin(word: string, py2: string, py3: string, er: boolean) {
  if (word.length === 1) return [word, py3];

  // * ----------------

  const correctPy3List = /咱家|女红|胳肢窝|高粱面|便溺|虚与委蛇|属意|杭育|群氓|转文/;
  if (correctPy3List.test(word)) return [word, py3];

  const fixedPatch = {
    刀把子: ["刀把子", "dāo bà zi"],
  } as Record<string, string[]>;
  if (fixedPatch[word]) return fixedPatch[word];

  // 丢弃特殊字符词语
  if (/[a-zA-Z+·]/.test(word)) return ["", ""];

  // * ----------------

  let restPy2 = py2.toLowerCase().replace("，", "").replace(/、.*/, "");
  let restPy2N = normalizePinyin(restPy2);

  const chars: string[] = [];
  const pys: string[] = [];

  [...word.replaceAll("，", "")].forEach((c) => {
    restPy2 = restPy2.replace(/^(-|·|’|'|\s|\/\/)+/, "");
    restPy2N = restPy2N.replace(/^(-|·|’|'|\s|\/\/)+/, "");

    // 丢弃儿化音
    if (c === "儿" && restPy2.startsWith("r")) {
      restPy2 = restPy2.slice(1);
      restPy2N = restPy2N.slice(1);
      return;
    }

    const u = charUnitMap.get(c)!;

    const py =
      c === "亲"
        ? (restPy2.startsWith("qìng") && "qìng") || (restPy2.startsWith("qīn") && "qīn")
        : u.findLast((e) => restPy2N.startsWith(e.pinyinN ?? ""))?.pinyin;

    if (py) {
      chars.push(c);
      pys.push(restPy2.slice(0, py.length));
      restPy2 = restPy2.slice(py.length);
      restPy2N = restPy2N.slice(py.length);
    }
  });

  // ! debug
  if (restPy2.length) {
    console.log(word, py2, py3, pys, restPy2);
    throw Error("Check Dirty Word");
  }

  return [chars.join(""), pys.join(" ")];
}

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

const file2 = await file(join(sourceDir, "/cn/modern.tsv")).text();

const data = file2
  .split("\n")
  .filter((e) => e)
  .slice(1)
  .map((e, i) => {
    const [freq, word, _3, _4, _5, er, _7, py2, py3] = e.split("\t");
    const [wordClean, pinyinClean] = rebuildWordPinyin(word, py2, py3, er !== "0");

    const level = Math.max(...[...wordClean].map((e) => charUnitMap.get(e)?.at(0)?.level ?? 9));

    return {
      word: wordClean,
      pinyin: pinyinClean,
      level: level,
      freq: Number(freq),
      groups: getFuzzyGroups(pinyinClean),
    } as WordUnit;
  })

  .filter((e) => e.word.length > 1)
  .filter((e) => !eduWords.has(e.word));

const uniqData = Array.from(new Map(data.map((e) => [e.word, e])).values()).sort(
  (a, b) => a.word.length - b.word.length || a.level - b.level || a.freq - b.freq,
);

await file(join(dataDir, "/cn/modern.tsv")).write(uniqData.map((e) => wordUnitToLine(e)).join("\n"));
