export interface WordUnit {
  /** 字/词 */
  word: string;
  /** 带音调拼音 */
  pinyin: string;

  /** 不带声调拼音 */
  pinyinN?: string;

  /** 字表/词表 分级 */
  level: number;
  /** 词频顺序 */
  freq: number;
  /** 模糊音组 */
  groups: string[];
}

export function wordUnitToLine(unit: WordUnit): string {
  const { word, pinyin, level, freq, groups } = unit;
  return [word, pinyin, level, freq, groups].join("\t");
}

export function wordLineToUnit(line: string): WordUnit {
  const [word, pinyin, level, freq, groups] = line.split("\t");
  return { word, pinyin, level: Number(level), freq: Number(freq), groups: groups.split(",") };
}
