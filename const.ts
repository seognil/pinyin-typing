import { join } from "node:path";

export const projectRoot = import.meta.dir;

export const sourceDir = join(projectRoot, ".source");
export const dataDir = join(projectRoot, "data/shards");
