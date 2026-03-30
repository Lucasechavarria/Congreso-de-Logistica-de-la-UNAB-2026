const fs = require('fs');
const path = require('path');

function getFiles(dir, files = []) {
  if (!fs.existsSync(dir)) return files;
  const list = fs.readdirSync(dir);
  for (const file of list) {
    const fullPath = path.resolve(dir, file);
    if (fs.statSync(fullPath).isDirectory()) {
      if (file !== 'node_modules' && file !== 'dist') getFiles(fullPath, files);
    } else {
      if (fullPath.endsWith('.ts') || fullPath.endsWith('.tsx')) {
        files.push(fullPath);
      }
    }
  }
  return files;
}

const clientDir = path.resolve(__dirname, 'client');
const files = getFiles(clientDir);
const index = new Map();

files.forEach(f => {
  index.set(f.toLowerCase(), f);
});

let errors = 0;

for (const file of files) {
  const content = fs.readFileSync(file, 'utf8');
  const importRegex = /from\s+['"]([^'"]+)['"]/g;
  let match;
  while ((match = importRegex.exec(content)) !== null) {
    let importPath = match[1];
    
    // Check aliases
    if (importPath.startsWith('@/')) {
      const relPath = importPath.replace('@/', '');
      const basePath = path.resolve(clientDir, relPath);
      
      const possiblePaths = [
        basePath + '.ts',
        basePath + '.tsx',
        path.join(basePath, 'index.ts'),
        path.join(basePath, 'index.tsx')
      ];
      
      let found = false;
      let incorrectCase = null;
      
      for (const p of possiblePaths) {
         if (fs.existsSync(p)) {
             // It exists locally! But does it match case exactly?
             const actualNameLower = p.toLowerCase();
             if (index.has(actualNameLower)) {
                 const actualName = index.get(actualNameLower);
                 if (actualName !== p) {
                     incorrectCase = { expected: actualName, got: p };
                 } else {
                     found = true;
                 }
                 break;
             }
         } else {
             const actualNameLower = p.toLowerCase();
             if (index.has(actualNameLower)) {
                 incorrectCase = { expected: index.get(actualNameLower), got: p };
                 break;
             }
         }
      }
      
      if (incorrectCase) {
          console.error(`Case mismatch in ${file}:\n  Import: ${importPath}\n  Expected file path: ${incorrectCase.expected}\n  But import resolves strictly to: ${incorrectCase.got}`);
          errors++;
      }
    }
  }
}

if (errors === 0) {
  console.log("No case mismatches found in aliases!");
}
