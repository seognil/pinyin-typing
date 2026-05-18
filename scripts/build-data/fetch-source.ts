import { join } from "node:path";
import { file } from "bun";
import { sourceDir } from "../../const";

// * ------------------------------------------------

const list = [
  [
    "chars-raw.txt",
    "https://raw.githubusercontent.com/iDvel/The-Table-of-General-Standard-Chinese-Characters/master/1-8105纯汉字（按顺序排列）.txt",
  ],
  [
    "chars-tone.txt",
    "https://raw.githubusercontent.com/iDvel/The-Table-of-General-Standard-Chinese-Characters/master/3-单个汉字+发音（带声调）.txt",
  ],
  ["edu.tsv", "https://raw.githubusercontent.com/zispace/hanzi-words-cycb/main/义务教育常用词表（草案）.tsv"],
  ["modern.tsv", "https://raw.githubusercontent.com/zispace/hanzi-words-cycb/main/现代汉语常用词表（第2版）.tsv"],
  ["phrase.json", "https://raw.githubusercontent.com/mozillazg/python-pinyin/master/pypinyin/phrases_dict.json"],
];

// * ------------------------------------------------ fetch raw source

list.forEach(async ([f, url]) => {
  const distfile = file(join(sourceDir, "/cn/", f));
  if (await distfile.exists()) return;
  const content = await fetch(url);
  await distfile.write(content);
});
