const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { execFileSync } = require("node:child_process");
const { assertCleanSource } = require("./capture.cjs");

function repository(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "bim-doctor-source-guard-"));
  const git = args => execFileSync("git", args, { cwd: root, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] }).trim();
  git(["init", "--quiet"]);
  for (const file of ["rules/check.json", "projects/manifest.json"]) {
    fs.mkdirSync(path.dirname(path.join(root, file)), { recursive: true });
    fs.writeFileSync(path.join(root, file), "{}\n");
  }
  git(["add", "."]);
  git(["-c", "user.name=Public source guard test", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "fixture"]);
  t.after(() => {
    assert.equal(path.dirname(root), fs.realpathSync(os.tmpdir()));
    assert.ok(path.basename(root).startsWith("bim-doctor-source-guard-"));
    fs.rmSync(root, { recursive: true, force: true, maxRetries: 3, retryDelay: 50 });
  });
  return { root, git, sha: git(["rev-parse", "HEAD"]) };
}

test("clean committed repository passes without launching a browser", t => {
  const { root, sha } = repository(t);
  assert.doesNotThrow(() => assertCleanSource(root, sha));
});

test("modified tracked rule outside the former whitelist is rejected", t => {
  const { root, sha } = repository(t);
  fs.writeFileSync(path.join(root, "rules/check.json"), '{"changed":true}\n');
  assert.throws(() => assertCleanSource(root, sha));
});

test("modified tracked project manifest is rejected", t => {
  const { root, sha } = repository(t);
  fs.writeFileSync(path.join(root, "projects/manifest.json"), '{"changed":true}\n');
  assert.throws(() => assertCleanSource(root, sha));
});

test("staged changes are rejected even when the worktree matches HEAD", t => {
  const { root, sha, git } = repository(t);
  const file = path.join(root, "projects/manifest.json");
  fs.writeFileSync(file, '{"changed":true}\n');
  git(["add", "projects/manifest.json"]);
  fs.writeFileSync(file, "{}\n");
  assert.throws(() => assertCleanSource(root, sha));
});

test("untracked runtime file is rejected", t => {
  const { root, sha } = repository(t);
  fs.writeFileSync(path.join(root, "rules/new-check.js"), "module.exports = true;\n");
  assert.throws(() => assertCleanSource(root, sha), /entire Git worktree/);
});
