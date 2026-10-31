const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const source=fs.readFileSync(path.join(__dirname,'../web/theme.js'),'utf8');
function boot({saved=null,dark=false,platform='MacIntel',nativeTheme,blocked=false}={}) {
  const listeners={},buttonListeners={},writes=[],messages=[];
  const root={dataset:{}},button={setAttribute(key,value){this[key]=value;},addEventListener(key,fn){buttonListeners[key]=fn;}};
  let mounted=false,changed;
  const system={matches:dark,addEventListener(key,fn){changed=fn;}};
  const document={documentElement:root,getElementById(){return mounted?button:null;},addEventListener(key,fn){listeners[key]=fn;}};
  const storage={getItem(){if(blocked)throw Error('Unavailable');return saved;},setItem(key,value){if(blocked)throw Error('Unavailable');saved=value;writes.push([key,value]);}};
  const window={matchMedia(){return system;},fmscoutNativeTheme:nativeTheme,webkit:{messageHandlers:{themePreference:{postMessage:value=>messages.push(value)}}}};
  vm.runInNewContext(source,{document,window,localStorage:storage,navigator:{platform}});
  const initial=root.dataset.theme;
  mounted=true;listeners.DOMContentLoaded();
  return {root,button,initial,writes,messages,click:()=>buttonListeners.click(),os(value){system.matches=value;changed();},key(overrides={}){const e={key:'L',shiftKey:true,metaKey:true,ctrlKey:false,altKey:false,repeat:false,preventDefault(){this.prevented=true;},...overrides};listeners.keydown(e);return e;}};
}
const automatic=boot();assert.equal(automatic.initial,'light');assert(automatic.button.innerHTML.includes('<circle'));
automatic.os(true);assert.equal(automatic.root.dataset.theme,'dark');assert.equal(automatic.writes.length,0);assert.equal(automatic.messages.length,0);
assert.equal(automatic.button.title,'Modo claro (⇧⌘L)');assert(!automatic.button.innerHTML.includes('<circle'));
automatic.click();assert.equal(automatic.root.dataset.theme,'light');assert.equal(automatic.button['aria-pressed'],'false');assert.deepEqual(automatic.writes,[['fmscout.theme','light']]);assert.deepEqual(automatic.messages,['light']);
automatic.os(true);assert.equal(automatic.root.dataset.theme,'light');
for(const saved of ['light','dark']){const env=boot({saved,dark:saved==='light'});assert.equal(env.initial,saved);env.os(saved==='light');assert.equal(env.root.dataset.theme,saved);}
assert.equal(boot({saved:'auto',dark:true}).initial,'dark');
assert.equal(boot({nativeTheme:'dark'}).initial,'dark');assert.equal(boot({saved:'light',nativeTheme:'dark'}).initial,'light');
const blocked=boot({blocked:true,nativeTheme:'dark'});blocked.click();assert.equal(blocked.root.dataset.theme,'light');assert.deepEqual(blocked.messages,['light']);
const mac=boot();assert(mac.key().prevented);assert.equal(mac.root.dataset.theme,'dark');mac.key({repeat:true});assert.equal(mac.root.dataset.theme,'dark');mac.key({metaKey:false,ctrlKey:true});assert.equal(mac.root.dataset.theme,'dark');
const windows=boot({platform:'Win32'});assert(windows.key({metaKey:false,ctrlKey:true}).prevented);assert.equal(windows.root.dataset.theme,'dark');windows.key({ctrlKey:false});assert.equal(windows.root.dataset.theme,'dark');
console.log('PASS: OS live, first choice, localStorage, native seed/bridge, icons, Mac/Windows shortcuts and storage failure');
