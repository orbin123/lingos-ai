import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import vm from "node:vm";
import ts from "typescript";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, "..");
const require = createRequire(import.meta.url);

const moduleCache = new Map();

function loadTypeScriptModule(relativePath) {
  const normalized = relativePath.replace(/^\.\.\//, "");
  if (moduleCache.has(normalized)) {
    return moduleCache.get(normalized);
  }

  const filename = path.join(root, normalized);
  const source = fs.readFileSync(filename, "utf8");
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2020,
      esModuleInterop: true,
    },
  });
  const cjsModule = { exports: {} };
  const localRequire = (request) => {
    if (request.startsWith("@/")) {
      return loadTypeScriptModule(path.join("src", `${request.slice(2)}.ts`));
    }
    return require(request);
  };
  vm.runInNewContext(outputText, {
    exports: cjsModule.exports,
    module: cjsModule,
    require: localRequire,
  });
  moduleCache.set(normalized, cjsModule.exports);
  return cjsModule.exports;
}

const progression = loadTypeScriptModule("src/lib/progression-chart.ts");

test("computeProgressionYAxis returns exactly three ticks", () => {
  const axis = progression.computeProgressionYAxis([2.1, 2.3, 2.4]);
  assert.equal(axis.ticks.length, 3);
  assert.equal(axis.ticks[0], axis.yMin);
  assert.equal(axis.ticks[2], axis.yMax);
});

test("computeProgressionYAxis zooms low scores without a zero tick", () => {
  const axis = progression.computeProgressionYAxis([1.8, 2.1, 2.5]);
  assert.equal(axis.yMax, 3);
  assert.ok(axis.ticks.every((tick) => tick > 0));
  assert.ok(axis.yMin > 0);
});

test("computeProgressionYAxis uses the mid band for scores up to six", () => {
  const axis = progression.computeProgressionYAxis([2.4, 3.8, 5.2]);
  assert.equal(axis.yMin, 2);
  assert.equal(axis.yMax, 6);
  assert.equal(axis.ticks[0], 2);
  assert.equal(axis.ticks[1], 4);
  assert.equal(axis.ticks[2], 6);
});

test("computeProgressionYAxis shifts upward once scores exceed six", () => {
  const axis = progression.computeProgressionYAxis([4.5, 6.2, 7.1]);
  assert.equal(axis.yMax, 8);
  assert.equal(axis.yMin, 4);
  assert.equal(axis.ticks[0], 4);
  assert.equal(axis.ticks[1], 6);
  assert.equal(axis.ticks[2], 8);
});

test("normalizeSelectedSkills keeps at most four known keys", () => {
  const normalized = progression.normalizeSelectedSkills([
    "grammar",
    "vocabulary",
    "pronunciation",
    "fluency",
    "tone",
    "unknown",
  ]);
  assert.equal(normalized.length, 4);
  assert.equal(normalized[0], "grammar");
  assert.equal(normalized[1], "vocabulary");
  assert.equal(normalized[2], "pronunciation");
  assert.equal(normalized[3], "fluency");
});

test("default progression skills match the core four", () => {
  assert.equal(progression.DEFAULT_PROGRESSION_SKILLS.length, 4);
  assert.equal(progression.DEFAULT_PROGRESSION_SKILLS[0], "pronunciation");
  assert.equal(progression.DEFAULT_PROGRESSION_SKILLS[1], "grammar");
  assert.equal(progression.DEFAULT_PROGRESSION_SKILLS[2], "vocabulary");
  assert.equal(progression.DEFAULT_PROGRESSION_SKILLS[3], "fluency");
});

test("skillColor resolves canonical and aliased keys", () => {
  assert.equal(progression.skillColor("pronunciation"), "#ef4444");
  assert.equal(progression.skillColor("thought_org"), "#f59e0b");
});
