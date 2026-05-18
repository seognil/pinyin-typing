const alphabets = "abcdefghijklmnopqrstuvwxyz";

const cons = `
b p m f
d t n l
g k h j q x
zh ch sh r z c s
y w
`
  .trim()
  .split(/\s/);

const vowels = `
a o e i u v
ai ei ui ao ou iu ie ve er
an en un in un vn
ang eng ing ong
`
  .trim()
  .split(/\s/);

const fuzzyCons = `
z-zh c-ch s-sh
g-k h-f
n-l r-l
`
  .trim()
  .split(/\s/);

const fuzzyVowels = `
an-ang en-eng in-ing
an-ai
eng-ong on-ong un-ong
ian-iang uan-uang un-iong
`
  .trim()
  .split(/\s/);

const tonesReg = {
  a: /[āáǎà]/g,
  o: /[ōóǒò]/g,
  e: /[ēéěè]/g,
  i: /[īíǐì]/g,
  u: /[ūúǔù]/g,
  v: /[üǖǘǚǜ]/g,
} as const;

/** 去除声调 */
export function normalizePinyin(pinyin: string) {
  let result = pinyin;
  Object.entries(tonesReg).forEach(([a, reg]) => {
    result = result.replace(reg, a);
  });
  return result;
}

export function splitPinyin(pinyin: string) {
  for (const c of cons) {
    if (pinyin.startsWith(c)) return [c, pinyin.slice(c.length)];
  }

  // 如果没有匹配辅音，可能是零声母
  return ["", pinyin];
}

function getFuzzyGroupsSingle(pinyin: string) {
  const [con, vowel] = splitPinyin(normalizePinyin(pinyin));

  return [
    //
    ...fuzzyCons.filter((group) => group.split("-").includes(con)),
    ...fuzzyVowels.filter((group) => group.split("-").includes(vowel)),
  ];
}

export function getFuzzyGroups(pinyin: string) {
  return Array.from(new Set(pinyin.split(" ").flatMap((py) => getFuzzyGroupsSingle(py))));
}
