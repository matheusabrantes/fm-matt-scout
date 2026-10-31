const {chromium}=require('/Users/matheus/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const {spawn}=require('node:child_process');
const fs=require('node:fs/promises'),path=require('node:path'),os=require('node:os'),assert=require('node:assert/strict');

(async()=>{
  const root=path.resolve(__dirname,'..'),temp=await fs.mkdtemp(path.join(os.tmpdir(),'matt-column-search-'));
  const child=spawn(path.join(root,'.venv/bin/python'),['server.py','--storage',path.join(temp,'scout.sqlite3')],{cwd:root,env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});
  let browser,stderr='',stdout='';child.stderr.on('data',data=>stderr+=data);
  try{
    const url=await new Promise((resolve,reject)=>{
      const timer=setTimeout(()=>reject(Error('Server startup timed out')),15000);
      child.stdout.on('data',data=>{stdout+=data;if(stdout.startsWith('http')&&stdout.includes('\n')){clearTimeout(timer);resolve(stdout.split('\n')[0]);}});
      child.once('error',error=>{clearTimeout(timer);reject(error);});
      child.once('exit',code=>{clearTimeout(timer);reject(Error(`Server exited ${code}: ${stderr}`));});
    });
    const status=await(await fetch(url+'api/status')).json();
    const fixture={...status,saves:[],shortlist_count:0,meta:{file:'Column search fixture',path:'/fixture/not-a-real-save.fm',date:'2026-10-31',build:'fixture',counts:{players:0,staff:0,clubs:0},managed:[],warnings:[]}};
    browser=await chromium.launchPersistentContext(path.join(temp,'browser'),{headless:true,executablePath:process.env.SCOUT_QA_BROWSER||chromium.executablePath(),args:['--disk-cache-size=0','--media-cache-size=0'],viewport:{width:1440,height:900},colorScheme:'light',reducedMotion:'reduce'});
    const page=await browser.newPage(),errors=[];
    page.setDefaultTimeout(10000);
    page.on('pageerror',error=>errors.push(error.message));
    page.on('console',message=>{if(message.type()==='error')errors.push(message.text());});
    await page.route('**/api/**',async route=>{
      const endpoint=new URL(route.request().url()).pathname.split('/api/')[1];
      const data=endpoint==='status'?fixture:endpoint==='options'?{clubs:[],nations:[],competitions:[],based:[],regions:{},staff_roles:{},staff_areas:{}}:endpoint==='rows'?{rows:[],total:0,shortlist_count:0}:endpoint==='salaries'?{currency:'EUR',period:'month',rate:null,money_rate:null}:undefined;
      if(endpoint==='load')throw Error('This check must never load a real save');
      if(data!==undefined)await route.fulfill({json:data});else await route.continue();
    });
    const ready=()=>page.waitForFunction(()=>document.getElementById('workspace').getAttribute('aria-busy')==='false');
    const open=async()=>{await page.locator('#columns').click();await page.locator('#columns-dialog').evaluate(el=>Promise.all(el.getAnimations().map(animation=>animation.finished)));assert(await page.locator('#column-search').evaluate(el=>el===document.activeElement));assert.equal(await page.locator('#column-search').inputValue(),'');};
    const search=page.locator('#column-search'),visible=page.locator('#column-options .checkbox-label:visible');
    const checked=()=>page.locator('[data-column]:checked').evaluateAll(nodes=>nodes.map(node=>node.dataset.column).sort());
    const save=async()=>{const response=page.waitForResponse(r=>r.url().endsWith('/api/layouts')&&r.request().method()==='POST');await page.locator('#save-columns').click();assert((await response).ok());await ready();};
    const layouts=async()=>(await(await fetch(url+'api/layouts')).json());
    const close=async()=>{await page.locator('#save-columns').focus();await page.keyboard.press('Escape');await page.locator('#columns-dialog').waitFor({state:'hidden'});};

    await page.goto(url);await ready();await open();
    const all=await visible.count(),sectionCount=await page.locator('.column-section:visible').count();
    assert(all>40);assert(await page.locator('[data-column="name"]').isDisabled());
    await search.fill('  NACIONAL  ');
    assert((await visible.count())>0);assert((await page.locator('.column-section:visible').count())<sectionCount);
    assert((await visible.allTextContents()).every(label=>label.toLocaleLowerCase('pt-BR').includes('nacional')));
    await search.fill('  POSICAO ');assert.equal(await visible.count(),1);assert((await visible.textContent()).includes('Posição'));
    await search.fill('nao-existe-coluna');assert.equal(await visible.count(),0);assert.equal(await page.locator('.column-section:visible').count(),0);
    assert(await page.locator('#column-search-empty').isVisible());
    await search.fill('');assert.equal(await visible.count(),all);assert.equal(await page.locator('.column-section:visible').count(),sectionCount);
    assert(!(await page.locator('#column-search-empty').isVisible()));

    await search.fill('passe');await page.locator('[data-column="attr_passing"]').check();
    await search.fill('idade');await page.locator('[data-column="age"]').focus();await page.keyboard.press('Space');assert(!(await page.locator('[data-column="age"]').isChecked()));
    await search.fill('tecnica');await page.locator('[data-column="attr_technique"]').check();
    const expected=await checked();assert(expected.includes('name')&&expected.includes('attr_passing')&&expected.includes('attr_technique')&&!expected.includes('age'));
    await save();assert.deepEqual((await layouts()).players.slice().sort(),expected);
    await open();assert.deepEqual(await checked(),expected);assert.equal(await visible.count(),all);
    await search.fill('rescisao');await page.locator('#save-columns').focus();
    for(const shortcut of ['Meta+f','Control+f']){await page.keyboard.press(shortcut);assert(await search.evaluate(el=>el===document.activeElement));await page.locator('#save-columns').focus();}
    await close();assert(!(await page.locator('#columns-dialog').isVisible()));
    await page.keyboard.press('Meta+f');await page.waitForFunction(()=>document.activeElement===document.getElementById('search'));

    await open();await search.fill('passe');await page.locator('[data-column-preset="Defesa"]').click();
    assert(!(await page.locator('[data-column="attr_passing"]').isChecked()));assert(await page.locator('[data-column="attr_tackling"]').isChecked());
    assert(await page.locator('[data-column="name"]').isChecked());assert.equal(await search.inputValue(),'passe');
    await search.fill('desarme');assert.equal(await visible.count(),1);assert(await page.locator('[data-column="attr_tackling"]').isVisible());
    await page.locator('[data-column-preset="Limpar"]').click();assert.equal(await page.locator('[data-column^="attr_"]:checked').count(),0);
    await close();

    for(const [kind,term,column]of [['staff','  FUNCAO  ','staff_role'],['clubs','  ESTADIO  ','stadium_name']]){
      await page.locator(`[data-view="${kind}"]`).click();await ready();await open();
      await search.fill(term);assert(await page.locator(`[data-column="${column}"]`).isVisible());
      assert((await visible.count())>0);assert.equal(await page.locator('[data-column-preset]').count(),0);
      await search.fill('nada-corresponde');assert(await page.locator('#column-search-empty').isVisible());
      await search.fill('');const before=await checked();await save();assert.deepEqual((await layouts())[kind].slice().sort(),before);
    }
    assert.deepEqual((await layouts()).players.slice().sort(),expected);
    await page.reload();await ready();await open();assert.deepEqual(await checked(),expected);await close();

    for(const theme of ['light','dark']){
      if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#theme-toggle').click();
      for(const width of [1440,390]){
        await page.setViewportSize({width,height:900});await open();await search.fill('passe');
        assert.equal(await search.getAttribute('aria-label'),'Buscar colunas');
        assert.equal(await search.locator('..').locator('svg').count(),1);
        const box=await search.boundingBox(),dialog=await page.locator('#columns-dialog').boundingBox();
        assert(box.width>120&&box.x>=dialog.x&&box.x+box.width<=dialog.x+dialog.width);
        assert(dialog.x>=0&&dialog.x+dialog.width<=width);assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
        if(process.env.SCOUT_QA_OUT){await fs.mkdir(process.env.SCOUT_QA_OUT,{recursive:true});await page.screenshot({path:path.join(process.env.SCOUT_QA_OUT,`column-search-${theme}-${width}.png`)});}
        await close();
      }
    }
    assert.deepEqual(errors,[]);
    console.log('PASS: column search, accents/case/whitespace, groups, empty state, selection preservation, isolated layout persistence, presets, three lists, keyboard, Escape and light/dark at 390/1440px; no save loaded');
  }finally{
    if(browser)await browser.close();
    child.kill('SIGTERM');if(child.exitCode===null)await new Promise(resolve=>child.once('exit',resolve));
    await fs.rm(temp,{recursive:true,force:true});
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
