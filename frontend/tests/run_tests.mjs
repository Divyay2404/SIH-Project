/**
 * Fast, lightweight test runner using esbuild and Node.js built-in test runner.
 * No external test framework dependencies required.
 */
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import esbuild from 'esbuild';

const __dirname = dirname(fileURLToPath(import.meta.url));
const testEntries = [
  join(__dirname, 'weakness_heatmap.test.js'),
  join(__dirname, 'student_portal.test.js')
];
const compiledOutput = join(__dirname, '.compiled.test.mjs');

console.log('Compiling test suite with esbuild...');
await esbuild.build({
  entryPoints: testEntries,
  bundle: true,
  format: 'esm',
  platform: 'node',
  outdir: __dirname,
  entryNames: '[name].compiled',
  packages: 'external',
  loader: { '.js': 'jsx' },
  define: {
    'import.meta.env': 'process.env'
  }
});

const compiledFiles = testEntries.map((e) => {
  const base = e.replace(/\.js$/, '');
  return `${base}.compiled.js`;
});

console.log('Running test suite with node:test...');
const result = spawnSync(process.execPath, ['--test', ...compiledFiles], {
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'test' }
});

import { rmSync } from 'node:fs';

for (const file of compiledFiles) {
  try { rmSync(file, { force: true }); } catch (_) {}
}

process.exit(result.status ?? 0);
