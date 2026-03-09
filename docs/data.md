# 数据

## 当前数据模型

- 当前数据层生成四个运行时 tier：`chars`、`edu`、`modern`、`phrase`。
- `chars` 保持官方 `8105` 标准字顺序和等级划分。
- 词语数据采用增量式课程分层：
  - `edu` = 归一化后的 `义务教育常用词表（草案）`
  - `modern` = 相对 `edu` 的 `现代汉语常用词表（第2版）` 增量层
  - `phrase` = 相对 `edu + modern` 的 `phrases_dict.json` 增量层
- 词语 tiers 保持互斥，避免同一词在不同层重复出现。

## 数据来源

- `zispace/hanzi-words-cycb` - `https://github.com/zispace/hanzi-words-cycb`
- `mozillazg/python-pinyin` - `https://github.com/mozillazg/python-pinyin`
- `iDvel/The-Table-of-General-Standard-Chinese-Characters` - `https://github.com/iDvel/The-Table-of-General-Standard-Chinese-Characters`

当前活跃的 source 文件包括：

- `.source/hanzi-words-cycb/义务教育常用词表（草案）.tsv`
- `.source/hanzi-words-cycb/现代汉语常用词表（第2版）.tsv`
- `.source/python-pinyin/phrases_dict.json`
- `.source/general-standard-chars/1-8105纯汉字（按顺序排列）.txt`
- `.source/general-standard-chars/3-单个汉字+发音（带声调）.txt`

## build 流程

构建入口：

1. `python3 -m scripts.build_data`

构建流程分为六步：

### Stage 1: 抓取 sources

- 上游原始文件统一缓存在 `.source/` 下。
- 把抓取到的文件元数据写入 `.source/manifest.json`。
- 每次构建都检查 source；如果本地文件已存在且非空，则跳过重复下载。

### Stage 2: 构建归一化行

- 用官方 `8105` 顺序文件和单字发音文件构建 `chars`。
- 校验去重后的单字发音顺序与官方 `8105` 顺序完全一致。
- 从 `义务教育常用词表（草案）.tsv` 构建 `edu`。
- 从 `现代汉语常用词表（第2版）.tsv` 构建 `modern`。
- 从 `phrases_dict.json` 构建 `phrase`。
- 从 `pm` 解析混淆组，并编码成紧凑字段。
- 从官方 `8105` 单字主干解析字级信息，并编码成位图。
- 过滤包含官方 `8105` 之外字符的行。

### Stage 3: 构建增量词语 tiers

- `edu` 是归一化后的校内课程词层。
- `modern` 只保留未被 `edu` 覆盖的词。
- `phrase` 只保留未被 `edu + modern` 覆盖的词。

### Stage 4: 重建全局词语顺序

- `chars` 保持官方单字顺序。
- 词语部分会重建一条全局 `fr` 顺序，供运行时训练使用。
- 当前词语顺序为：
  - `edu-1`
  - `edu-2`
  - `edu-3`
  - `edu-4`
  - `modern`
  - `phrase`
- 每个 `edu-*` 分桶内部：
  - 如果该词也存在于 `modern`，优先复用 `modern` 顺序
  - `edu` 独有词接在该等级末尾
- 最后把整条词语序列重新编号成连续的 `fr`。

### Stage 5: 写入 shards

- 所有运行时数据统一使用 `t<TAB>pm<TAB>fr<TAB>g<TAB>l`。
- 每行不保存 `tier`，由 shard 元数据提供。
- shards 写入 `data/shards/`。
- 先按 `tier` 分桶，再对词语 tiers 按 `len` 分桶，然后按目标文件大小继续切分。
- 目前 shard 目标大小为 `256 * 1024` 字节。
- 不再按混淆组或等级预切文件，保证每一行只写一次。

### Stage 6: 写入元数据

- 把 shard 元数据和课程分桶范围写入 `data/manifest.json`。
- 把脏数据复核文件写入 `.source/output-exclude/*.tsv`。
- 把总量、分桶范围、长度等级分布和过滤统计写入 `data/meta.md`。

## 运行时产物

- 运行时 shards：`data/shards/*.tsv`
- 运行时清单：`data/manifest.json`
- 人工阅读摘要：`data/meta.md`
- 脏数据复核导出：`.source/output-exclude/*.tsv`

这些产物的职责边界是：

- `data/manifest.json`：给运行时消费，描述分桶和 shard 边界。
- `data/meta.md`：给人看，汇总当前 build 结果。
- `docs/`：解释结构、规则和设计决策，不重复抄写会随 build 变化的数字。

## 行结构

统一行格式：

```text
认真\trèn zhēn\t1024\ten-eng,r-l\t1
```

- 第 1 列：`t`
- 第 2 列：`pm`
- 第 3 列：`fr`
- 第 4 列：`g`
- 第 5 列：`l`

每行不保存 `tier`；它由 shard 名称和 `data/manifest.json` 提供。

### `fr`

- 在 `chars` 中，`fr` 就是官方 `8105` 单字顺序。
- 在词语 tiers 中，`fr` 是统一的运行时训练顺序，而不是原始 source 行号。
- 词语 `fr` 的全局顺序为：
  - `edu-1`
  - `edu-2`
  - `edu-3`
  - `edu-4`
  - `modern`
  - `phrase`

### `g`

- `g` 保存命中的混淆组，顺序由固定的 `GROUP_ORDER` 决定。
- 空 `g` 表示该行属于 `rest`。

### `l`

- `l` 是基于官方 `8105` 等级表生成的位图。
- 对单字行来说，`l` 只会是 `1`、`2` 或 `4`。

## 单字主干规则

- 官方 `1-8105纯汉字（按顺序排列）.txt` 是单字覆盖范围的单一事实来源。
- 单字等级直接由该顺序决定：
  - `1..3500 -> level 1`
  - `3501..6500 -> level 2`
  - `6501..8105 -> level 3`
- 发音文件只负责补 `pm`，不决定覆盖范围和等级。

## manifest 结构

`data/manifest.json` 包含：

- `sources`：已抓取 source 的元数据
- `totals`：各 tier 的总量
- `word_buckets`：统一词语 `fr` 上的课程分桶范围
- `shards`：物理 shard 元数据

每条 `word_buckets` 记录包含：

- `id`
- `tier`
- `rows`
- `fr_start`
- `fr_end`
- 可选的 `edu_level`

每条 shard 记录包含：

- `path`
- `tier`
- `len`
- `rows`
- `bytes`
- `fr_min`
- `fr_max`

## 复核导出

构建阶段还会输出仅供人工复核的脏数据文件：

- `.source/output-exclude/edu.tsv`
- `.source/output-exclude/modern.tsv`
- `.source/output-exclude/phrase.tsv`

每行格式为：

```text
text\tpm_raw\tfr\treason
```

当前脏数据原因包括：

- `non_8105`
- `invalid_pm`
- `no_valid_candidate`

正常产品过滤，如跨 tier 重复或长度不在范围内，不导出到复核文件，只在 `data/meta.md` 中统计。

## 已冻结的数据决策

- 官方 `8105` 表是单字覆盖、单字 `fr` 和单字等级的单一事实来源。
- 单字拼音只从发音表补充，并且要先通过严格顺序校验。
- 词语 `fr` 不再是原始 source 行号，而是面向训练重建后的统一顺序。
- `edu` 先按 `分级` 排，再在每个等级内部优先复用 `modern` 顺序；`edu` 独有词接在该级末尾。
- `modern` 和 `phrase` 继续作为追加在 `edu` 后面的增量层。
- `manifest` 额外记录课程分桶范围，供运行时把训练选择映射到全局词语顺序上。
