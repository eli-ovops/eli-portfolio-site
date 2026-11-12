import { build } from 'esbuild';
import { fileURLToPath } from 'node:url';
import { resolve, dirname } from 'node:path';
const here = dirname(fileURLToPath(import.meta.url));
await build({
  absWorkingDir:here, entryPoints:['index.jsx'], bundle:true,
  outfile:resolve(here,'../../assets/flex-carousel-official.js'),
  format:'iife', platform:'browser', target:['es2020'], jsx:'automatic',
  minify:true, sourcemap:false, legalComments:'external',
  define:{'process.env.NODE_ENV':'"production"'}, logLevel:'info'
});
