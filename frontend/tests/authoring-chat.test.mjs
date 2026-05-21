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

function loadTypeScriptModule(relativePath) {
  const filename = path.join(root, relativePath);
  const source = fs.readFileSync(filename, "utf8");
  const { outputText } = ts.transpileModule(source, {
    compilerOptions: {
      module: ts.ModuleKind.CommonJS,
      target: ts.ScriptTarget.ES2020,
    },
  });
  const cjsModule = { exports: {} };
  vm.runInNewContext(outputText, {
    URLSearchParams,
    encodeURIComponent,
    exports: cjsModule.exports,
    module: cjsModule,
    process: { env: {} },
    require,
  });
  return cjsModule.exports;
}

const authoring = loadTypeScriptModule("src/lib/authoring-chat.ts");

test("authoring start path includes week and day query params", () => {
  assert.equal(
    authoring.authoringStartPath({ week: 1, day: 3 }),
    "/api/dev/learning/sessions/start?week=1&day=3",
  );
});

test("authoring websocket omits token and uses dev path", () => {
  assert.equal(
    authoring.learningWebSocketUrl("http://localhost:8000", "abc", {
      authoring: true,
      token: "secret",
    }),
    "ws://localhost:8000/dev/ws/learning/abc",
  );
});

test("production websocket keeps token on production path", () => {
  assert.equal(
    authoring.learningWebSocketUrl("http://localhost:8000", "abc", {
      authoring: false,
      token: "secret",
    }),
    "ws://localhost:8000/ws/learning/abc?token=secret",
  );
});

test("restart path switches in authoring mode", () => {
  assert.equal(
    authoring.learningRestartPath("a/b", true),
    "/api/dev/learning/sessions/a%2Fb/restart",
  );
  assert.equal(
    authoring.learningRestartPath("a/b", false),
    "/api/learning/sessions/a%2Fb/restart",
  );
});
