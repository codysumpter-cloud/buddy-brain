#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";

const root = path.resolve(import.meta.dirname, "..");
const skillsDir = path.join(root, "skills");
const registryPath = path.join(skillsDir, "index.json");
const collectionDirectories = new Set(["media"]);

function fail(message) {
  console.error(`ERROR: ${message}`);
  process.exit(1);
}

function ensureFile(filePath, message) {
  if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) fail(message);
}

function section(text, heading, label) {
  const start = text.indexOf(heading);
  if (start === -1) fail(`${label} is missing section: ${heading}`);
  const remaining = text.slice(start + heading.length);
  const nextHeading = remaining.search(/\n## /);
  return nextHeading === -1 ? remaining : remaining.slice(0, nextHeading);
}

function validateCollectionDirectory(directory) {
  const readmePath = path.join(skillsDir, directory, "README.md");
  ensureFile(
    readmePath,
    `collection directory '${directory}' must have ${path.relative(root, readmePath).replaceAll("\\", "/")}`,
  );

  const text = fs.readFileSync(readmePath, "utf8");
  if (!text.includes("## Purpose")) {
    fail(`collection directory '${directory}' must document a ## Purpose section`);
  }
}

const registryRaw = fs.readFileSync(registryPath, "utf8");
const registry = JSON.parse(registryRaw);
const skills = registry.skills;

if (!skills || typeof skills !== "object" || Array.isArray(skills)) {
  fail("skills must be an object");
}

for (const [name, spec] of Object.entries(skills)) {
  if (!spec || typeof spec !== "object" || Array.isArray(spec)) {
    fail(`skill '${name}' must be an object`);
  }

  const triggers = spec.triggers;
  if (!Array.isArray(triggers) || triggers.length === 0) {
    fail(`skill '${name}' must have non-empty triggers list`);
  }
  if (triggers.some((trigger) => typeof trigger !== "string" || trigger.trim().length === 0)) {
    fail(`skill '${name}' has invalid trigger entries`);
  }
  if (new Set(triggers.map((trigger) => trigger.toLowerCase())).size !== triggers.length) {
    fail(`skill '${name}' has duplicate triggers (case-insensitive)`);
  }

  const actions = spec.actions;
  if (!Array.isArray(actions) || actions.length === 0) {
    fail(`skill '${name}' must have non-empty actions list`);
  }
  if (actions.some((action) => typeof action !== "string" || action.trim().length === 0)) {
    fail(`skill '${name}' has invalid actions`);
  }

  if (!actions.includes(spec.default_action)) {
    fail(`skill '${name}' default_action must be one of actions`);
  }

  const skillReadme = path.join(skillsDir, name, "README.md");
  ensureFile(skillReadme, `skill '${name}' must have ${path.relative(root, skillReadme).replaceAll("\\", "/")}`);

  const skillText = fs.readFileSync(skillReadme, "utf8");
  if (!skillText.includes("## Purpose")) {
    fail(`skill '${name}' must document a ## Purpose section`);
  }
}

const skillDirectories = fs
  .readdirSync(skillsDir, { withFileTypes: true })
  .filter((entry) => entry.isDirectory())
  .map((entry) => entry.name)
  .sort();

const registeredSkills = Object.keys(skills).sort();

for (const directory of skillDirectories) {
  if (collectionDirectories.has(directory)) {
    validateCollectionDirectory(directory);
    continue;
  }

  if (!skills[directory]) fail(`skills/${directory} exists but is missing from skills/index.json`);
}

for (const skillName of registeredSkills) {
  const skillDir = path.join(skillsDir, skillName);
  if (!fs.existsSync(skillDir) || !fs.statSync(skillDir).isDirectory()) {
    fail(`skill '${skillName}' is registered but skills/${skillName} is missing`);
  }
}

const skillsReadmePath = path.join(skillsDir, "README.md");
ensureFile(skillsReadmePath, "skills/README.md must exist");
const skillsReadme = fs.readFileSync(skillsReadmePath, "utf8");
if (!skillsReadme.includes("`skills/index.json`")) {
  fail("skills/README.md must point to skills/index.json");
}
const skillSetSection = section(skillsReadme, "## Current skill set", "skills/README.md");
for (const skillName of registeredSkills) {
  if (!skillSetSection.includes(`\`${skillName}/\``)) {
    fail(`skills/README.md must list \`${skillName}/\` in the current skill set`);
  }
}

const contextSkillsPath = path.join(root, "context", "skills", "SKILLS.md");
ensureFile(contextSkillsPath, "context/skills/SKILLS.md must exist");
const contextSkills = fs.readFileSync(contextSkillsPath, "utf8");
for (const token of ["`skills/README.md`", "`skills/index.json`"]) {
  if (!contextSkills.includes(token)) {
    fail(`context/skills/SKILLS.md must mention ${token}`);
  }
}

console.log("skills registry, collection bundles, and skill docs are valid");
