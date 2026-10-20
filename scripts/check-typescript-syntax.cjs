// Pemeriksaan sintaks saja memakai compiler yang diberikan sebagai argumen.
// Bukan pengganti tsc -b: dependensi tipe harus tersedia untuk pemeriksaan penuh.
const fs=require('node:fs'),path=require('node:path')
const ts=require(process.argv[2])
const root=path.resolve(__dirname,'../frontend')
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)])}
let count=0,errors=0
for(const file of [...files(path.join(root,'src')),path.join(root,'vite.config.ts')].filter(f=>/\.tsx?$/.test(f))){
  const source=ts.createSourceFile(file,fs.readFileSync(file,'utf8'),ts.ScriptTarget.Latest,true,file.endsWith('.tsx')?ts.ScriptKind.TSX:ts.ScriptKind.TS)
  const diagnostics=source.parseDiagnostics
  count++
  for(const diagnostic of diagnostics){errors++;console.error(file,ts.flattenDiagnosticMessageText(diagnostic.messageText,'\n'))}
}
console.log(`Syntax TypeScript: ${count} berkas, ${errors} error. Pemeriksaan tipe/build belum dilakukan.`)
process.exitCode=errors?1:0
