#!/usr/bin/env node
/**
 * 把包内的 skills/ 落到 DSH 家目录，供 cordis.patch.yml 里的 customSkillDirs 使用。
 *
 * 目标：$DSH_HOME/.agent-presets/prism/skills
 * 幂等：已存在同名目录时跳过（不会覆盖你自己改过的副本），加 --force 才覆盖。
 *
 * 用法:
 *   node scripts/sync-assets.mjs
 *   node scripts/sync-assets.mjs --force
 *   DSH_HOME=/tmp/test node scripts/sync-assets.mjs
 */

import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const src = path.join(root, "skills");
const home = process.env.DSH_HOME || path.join(os.homedir(), ".dsh");
const dest = path.join(home, ".agent-presets", "prism", "skills");
const force = process.argv.includes("--force");

if (!fs.existsSync(src)) {
  console.error(`[prism] 找不到 skills/ 目录: ${src}`);
  process.exit(1);
}

fs.mkdirSync(dest, { recursive: true });

let copied = 0;
let skipped = 0;
for (const name of fs.readdirSync(src)) {
  const from = path.join(src, name);
  if (!fs.statSync(from).isDirectory()) continue;
  const to = path.join(dest, name);
  if (fs.existsSync(to) && !force) {
    skipped += 1;
    continue;
  }
  fs.cpSync(from, to, { recursive: true, force: true });
  copied += 1;
}

console.log(`[prism] skills -> ${dest}`);
console.log(`[prism] 复制 ${copied} 个，跳过 ${skipped} 个（已存在）`);
if (skipped && !force) {
  console.log("[prism] 想覆盖已有副本：node scripts/sync-assets.mjs --force");
}
