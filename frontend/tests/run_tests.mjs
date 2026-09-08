/**
 * Fast, lightweight test runner using esbuild and Node.js built-in test runner.
 * No external test framework dependencies required.
 */
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import esbuild from 'esbuild';

const __dirname = dirname(fileURLToPath(import.meta.url));
const testEntry = join(__dirname, 'weakness_heatmap.test.js');
const compiledOutput = join(__dirname, '.compiled.test.mjs');

console.log('Compiling test suite with esbuild...');
await esbuild.build({
  entryPoints: [testEntry],
  bundle: true,
  format: 'esm',
  platform: 'node',
  outfile: compiledOutput,
  packages: 'external',
  define: {
    'import.meta.env': 'process.env'
  }
});

console.log('Running test suite with node:test...');
const result = spawnSync(process.execPath, ['--test', compiledOutput], {
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'test' }
});

process.exit(result.status ?? 0);
