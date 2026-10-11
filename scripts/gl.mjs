import { existsSync, readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const installed = resolve(root, 'node_modules/genlayer/package.json');
const wrapper = resolve(root, `node_modules/.bin/genlayer${process.platform === 'win32' ? '.cmd' : ''}`);
if (!existsSync(installed) || !existsSync(wrapper)) {
  console.error('ERROR: local genlayer CLI missing. Run npm install in this repository.');
  process.exit(2);
}
const version = JSON.parse(readFileSync(installed, 'utf8')).version;
if (version !== '0.39.1') {
  console.error(`ERROR: local CLI is ${version}; required exactly 0.39.1`);
  process.exit(2);
}
const args = process.argv.slice(2);
if (args.some(a => /studio-dev|studio-next|0\.40\.0rc/i.test(a))) {
  console.error('ERROR: Studio Dev/Next references are forbidden for this project.');
  process.exit(2);
}
if (args.includes('--network')) {
  console.error('ERROR: --network override forbidden. Use explicit StudioNet RPC.');
  process.exit(2);
}
if (args.includes('--rpc')) {
  const idx = args.indexOf('--rpc');
  if (args[idx + 1] !== 'https://studio.genlayer.com/api') {
    console.error('ERROR: only StudioNet RPC is supported.');
    process.exit(2);
  }
}
const result = spawnSync(wrapper, args, {
  cwd: root,
  stdio: 'inherit',
  shell: process.platform === 'win32',
  env: process.env,
});
if (result.error) {
  console.error(result.error.message);
  process.exit(2);
}
process.exit(result.status ?? 2);
