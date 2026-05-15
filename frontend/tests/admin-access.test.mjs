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
    exports: cjsModule.exports,
    module: cjsModule,
    require,
  });
  return cjsModule.exports;
}

const adminAccess = loadTypeScriptModule("src/lib/admin-access.ts");

test("admin sidebar items render from the expected navigation model", () => {
  assert.equal(
    JSON.stringify(adminAccess.ADMIN_NAV_ITEMS.map((item) => item.label)),
    JSON.stringify([
      "Dashboard",
      "Users",
      "Task Templates",
      "Payments",
      "Subscriptions",
      "AI Logs",
      "Feedback Review",
      "Audit Logs",
      "Roles & Permissions",
    ]),
  );
});

test("learner users do not see the admin console button", () => {
  assert.equal(
    adminAccess.shouldShowAdminConsoleButton({
      role: "learner",
      roles: ["learner"],
      is_superuser: false,
    }),
    false,
  );
});

test("admin and super_admin users can access admin surfaces", () => {
  assert.equal(adminAccess.canAccessAdmin({ roles: ["admin"] }), true);
  assert.equal(adminAccess.canAccessAdmin({ roles: ["super_admin"] }), true);
});

test("only super admins can see role-management surfaces", () => {
  assert.equal(adminAccess.canManageRoles({ roles: ["admin"] }), false);
  assert.equal(adminAccess.canManageRoles({ roles: ["super_admin"] }), true);
});
