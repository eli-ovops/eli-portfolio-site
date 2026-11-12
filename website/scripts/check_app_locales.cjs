// Execute both startup branches: syntax checks alone cannot catch temporal dead zones.
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../app.js'), 'utf8');
for (const lang of ['zh-CN', 'en']) {
  const context = {
    document: {documentElement: {lang}, querySelector: () => null,
      querySelectorAll: () => [], getElementById: () => null},
    window: {}
  };
  vm.runInNewContext(source, context, {filename: 'app.js'});
  console.log(`PASS: ${lang} startup`);
}
