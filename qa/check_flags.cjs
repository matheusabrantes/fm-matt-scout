const {chromium}=require('/Users/matheus/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {spawn}=require('node:child_process');
const fs=require('node:fs/promises'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');
(async()=>{
 const root=path.resolve(__dirname,'..'),temp=await fs.mkdtemp(path.join(os.tmpdir(),'matt-flags-'));
 const child=spawn(path.join(root,'.venv/bin/python'),['server.py','--storage',path.join(temp,'scout.sqlite3')],{cwd:root,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
 let stderr='';child.stderr.on('data',d=>stderr+=d);
 const url=await new Promise((resolve,reject)=>{child.stdout.once('data',d=>resolve(d.toString().trim()));child.once('exit',code=>reject(Error(`${code}: ${stderr}`)));});
 const browser=await chromium.launch({headless:true,executablePath:process.env.SCOUT_QA_BROWSER||chromium.executablePath()});
 try{
  const errors=[];
  const names=Object.values(JSON.parse(await fs.readFile(path.join(root,'nation-names.json'),'utf8')));
  const files=(await fs.readdir(path.join(root,'web/flags'))).filter(name=>/\.(png|svg)$/.test(name));
  for(let round=0;round<8;round++){
   const page=await browser.newPage();
   page.on('pageerror',e=>errors.push(e.message));
   page.on('console',m=>{if(m.type()==='error')errors.push(m.text()+' '+m.location().url.replaceAll(url,'<local>/'));});
   await page.goto(url);await page.locator('#save-list .save-option').first().waitFor();await page.waitForLoadState('networkidle');
   const result=await page.evaluate(async({files,names})=>{
    const missing=names.filter(name=>!window.fmScoutFlags.html(name));
    const images=await Promise.all(files.map(file=>new Promise(resolve=>{
     const img=new Image();img.onload=()=>{resolve(img.naturalWidth>0);img.remove();};img.onerror=()=>{resolve(false);img.remove();};img.src='flags/'+file;document.body.append(img);
    })));
    return {missing,loaded:images.filter(Boolean).length};
   },{files,names});
   assert.deepEqual(result.missing,[]);assert.equal(result.loaded,files.length);
   assert(!(await page.request.get(url+'flags/README.md')).ok());await page.close();
  }
  assert.deepEqual(errors,[]);
  console.log(`PASS: ${names.length} FM nations mapped; ${files.length} local flags loaded in 8 consecutive rounds, zero browser errors`);
 }finally{await browser.close();child.kill('SIGTERM');}
})().catch(e=>{console.error(e);process.exitCode=1;});
