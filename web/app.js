const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num = value => value == null ? '—' : Number(value).toLocaleString('pt-BR');
const fmtDate = value => value ? new Date(`${value}T12:00:00`).toLocaleDateString('pt-BR') : 'Não disponível';
const contractMonths = ['JAN','FEV','MAR','ABR','MAI','JUN','JUL','AGO','SET','OUT','NOV','DEZ'];
function compactContract(value) { return value ? `${contractMonths[Number(value.slice(5,7))-1]} ${value.slice(2,4)}` : '—'; }
const fieldIds = ['search','position','age_min','age_max','ca_min','pa_min','sum_min','club','nation','league','contract_before','rating_min','free','squad_scope','squad','availability'];
const baseColumns = {players:['name','age','positions','nation_id','club_name','ca','pa','attribute_sum','model_value','model_fee','contract_end'],staff:['name','age','nation_id','staff_role','staff_area','club_name','ca','pa','attribute_sum','attr_technical','attr_tactical','attr_judging_player_ability','attr_judging_player_potential','attr_physiotherapy'],clubs:['name','nation_id','league_name','reputation','player_count','ca_mean','pa_mean','age_mean','transfer_budget_remaining','stadium_seated_capacity']};
let columnGroups = {}, visibleColumns = structuredClone(baseColumns), searchTab = 'general';
let columnWidths = {players:{},staff:{},clubs:{}}, widthSaveTimer;
const defaultWidths={name:190,age:54,positions:112,nation_id:64,eu_national:70,club_name:150,team_slot:95,league_name:170,ca:54,pa:54,rating:62,attribute_sum:64,ability_difference:68,height_cm:60,staff_role:175,staff_area:140,reputation:90,player_count:95,ca_mean:74,pa_mean:74,age_mean:68,stadium_name:170};
const rangeLabels = {height_cm:'Altura (cm) †',stadium_seated_capacity:'Estádio: lugares sentados',stadium_expansion_capacity:'Estádio: capacidade de expansão',age:'Idade',ca:'Capacidade atual (CA) †',pa:'Potencial (PA) †',ability_difference:'Diferença PA − CA †',sum:'Soma dos atributos (36)',rating:'Nota atual (estimativa)',rep_home:'Reputação nacional',rep_current:'Reputação atual',rep_world:'Reputação mundial',club_reputation:'Reputação do clube',reputation:'Reputação do clube',model_value:'Valor de mercado · unidade do save',model_fee:'Compra estimada · unidade do save',value:'Valor lido do save · unidade do save',wage:'Salário · unidade do save †',release_fee:'Rescisão geral ou do tipo selecionado · unidade do save',balance:'Saldo · unidade do save',transfer_budget_remaining:'Orçamento de transferências · unidade do save',wage_budget_weekly:'Orçamento salarial · unidade do save'};
const rangeMax = {height_cm:255,stadium_seated_capacity:1000000,stadium_expansion_capacity:1000000,age:100,ca:200,pa:200,ability_difference:200,sum:720,rating:100,rep_home:10000,rep_current:10000,rep_world:10000,club_reputation:10000,reputation:10000,model_value:1e12,model_fee:1e12,value:1e12,wage:1e12,release_fee:1e12,balance:1e12,transfer_budget_remaining:1e12,wage_budget_weekly:1e12};
const titles = {players:'Jogadores',staff:'Staff',clubs:'Clubes',shortlist:'Minha lista',squad:'Meu time'};
let view = 'players', kind = 'players', sort = 'pa', direction = 'desc', total = 0, moreRequest = 0;
let staffScoring = [], meta = null, groups = {}, roles = {}, saves = [], presets = [], conditions = {}, traitLabels = [];
let rows = [], currentProfile = null, profileTab = 'attributes', selection = new Set(), loading = false, shortlistBusy = false;
let requestVersion = 0, profileVersion = 0, debounce, polling;
let optionsKind = null, viewVersion = 0;
const pickers = {};
let activePicker = null;
let salaryPrefs = {currency:'EUR',period:'month',rate:null}, salaryReference = null;
let filterDraft = null, draftVersion = 0, toastTimer, undoList = null, copyTimer;
const icons = {
  copy:'M6 5h7v9H6zM10 5V2H3v9h3',
  check:'M3.5 8.5 6.5 11.5 12.5 4.5',
  person:'M8 8.2a2.7 2.7 0 1 0 0-5.4 2.7 2.7 0 0 0 0 5.4ZM3 13.6c.6-2.4 2.6-3.8 5-3.8s4.4 1.4 5 3.8',
  staff:'M4.5 3.2H4a1 1 0 0 0-1 1v9a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-9a1 1 0 0 0-1-1h-.5M5.5 2h5v2h-5zM5.5 8h5M5.5 10.8h3',
  club:'M8 1.8 13 3.6v4.2c0 3.2-2.1 5.4-5 6.4-2.9-1-5-3.2-5-6.4V3.6Z',star:'M8 2l1.8 3.7 4 .6-2.9 2.8.7 4L8 11.2 4.4 13.1l.7-4L2.2 6.3l4-.6Z',
  home:'M2.5 13.5h11M4 13.5V7l4-3.5L12 7v6.5M6.5 13.5v-3.5h3v3.5',search:'M7 12A5 5 0 1 0 7 2a5 5 0 0 0 0 10ZM10.6 10.6 14 14',filter:'M2.5 4h11M4.5 8h7M6.5 12h3',columns:'M2.5 3h11v10h-11zM6.2 3v10M9.8 3v10',export:'M8 10V2.5M5.2 5.2 8 2.5l2.8 2.7M3 9v4h10V9',import:'M8 2.5V10M5.2 7.3 8 10l2.8-2.7M3 9v4h10V9',close:'M4 4l8 8M12 4l-8 8'
};
function icon(name) { return `<svg class="icon" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="${icons[name]||icons.search}"/></svg>`; }
function profileName(row) { return String((kind==='clubs'?row.short_name:null)||row.name||''); }
async function copyProfileName() {
  const name=currentProfile&&profileName(currentProfile.row);
  if(!name)return;
  const button=$('copy-name');
  if(window.webkit?.messageHandlers?.copyName)window.webkit.messageHandlers.copyName.postMessage(name);
  else await navigator.clipboard.writeText(name);
  if(!button?.isConnected)return;
  clearTimeout(copyTimer);button.innerHTML=icon('check');button.classList.add('copied');button.title='Copiado';button.setAttribute('aria-label','Nome copiado');
  copyTimer=setTimeout(()=>{if(button.isConnected){button.innerHTML=icon('copy');button.classList.remove('copied');button.title='Copiar nome';button.setAttribute('aria-label','Copiar nome');}},1500);
}
const positionXY={STC:[50,11],AML:[17,26],AMR:[83,26],AMC:[50,30],ML:[15,44],MC:[50,45],MR:[85,44],WBL:[12,57],WBR:[88,57],DM:[50,60],DL:[15,72],DR:[85,72],DC:[50,74],SW:[50,82],GK:[50,91]};
function positionGroup(p) { return p==='GK'?'gk':['DC','DL','DR','WBL','WBR','SW'].includes(p)?'def':['DM','MC','ML','MR'].includes(p)?'mid':'att'; }
function positionChips(list=[]) { return `<span class="position-chips">${list.map(p=>`<span class="position-chip ${positionGroup(p)}">${esc(p)}</span>`).join('')}</span>`; }
const clubAbbreviations = {'Inter Miami':'MIA','Real Madrid':'RMA','Man City':'MCI','Al-Nassr':'NSR','Barcelona':'BAR','Bayern München':'FCB','Napoli':'NAP','Arsenal':'ARS','Liverpool':'LIV','Chelsea':'CHE','Man United':'MUN','Corinthians':'COR'};
const clubAliases = {'Manchester City':'Man City','Manchester United':'Man United','Man Utd':'Man United','FC Bayern München':'Bayern München','Bayern Munich':'Bayern München','FC Barcelona':'Barcelona','Inter Miami CF':'Inter Miami'};
function clubPalette(row={}) {
  const bg=row.club_background,fg=row.club_foreground;
  if(!/^#[0-9a-f]{6}$/i.test(bg)||!/^#[0-9a-f]{6}$/i.test(fg))return null;
  const luminance=color=>color.slice(1).match(/../g).map(c=>parseInt(c,16)/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4).reduce((sum,c,i)=>sum+c*[.2126,.7152,.0722][i],0);
  const contrast=(a,b)=>(Math.max(a,b)+.05)/(Math.min(a,b)+.05),light=luminance(bg);
  return [bg,contrast(light,luminance(fg))>=4.5?fg:contrast(light,1)>=contrast(light,0)?'#FFFFFF':'#000000'];
}
function badge(name='', row={}) {
  const club=clubAliases[name]||name,palette=clubPalette(row);
  return `<span class="club-badge" ${palette?`data-club-bg="${palette[0]}" data-club-fg="${palette[1]}"`:''} aria-hidden="true">${esc(clubAbbreviations[club]||String(name||'').trim().slice(0,3).toUpperCase()||'FM')}</span>`;
}
const countryCodes=window.fmScoutFlags.codes;
function countryFlag(name, context='table') { return window.fmScoutFlags.html(name,context); }
function nationalityHeader(row) {
  const nations=row.nationalities?.length?row.nationalities:[{name:row.nation_name}];
  return `<div class="fm-nationalities">${(kind==='players'?nations:nations.slice(0,1)).map(n=>`<span class="fm-nationality ${kind==='clubs'?'fm-nationality--club':''}" title="${esc((n.id===row.nation_id?'Nacionalidade principal':'Nacionalidade adicional')+(n.is_eu?' · UE':''))}">${countryFlag(n.name,'profile')}<span>${esc(n.name||'Nome indisponível')}${kind==='clubs'&&row.league_name?' · '+esc(row.league_name):''}</span></span>`).join('')}</div>`;
}
function heat(value) {
  if(!Number.isFinite(value)||value<1||value>20)return '—';
  return `<span class="heat-cell" data-heat="${value}">${value}</span>`;
}
function applyDataStyles(container) {
  container.querySelectorAll('[data-club-bg][data-club-fg]').forEach(node=>{node.style.background=node.dataset.clubBg;node.style.color=node.dataset.clubFg;});
  container.querySelectorAll('[data-heat]').forEach(node=>{const v=Number(node.dataset.heat);if(v<1||v>20)return;const t=(v-1)/19;node.style.background=`oklch(${(.25+.6*t).toFixed(3)} ${(.03+.16*t).toFixed(3)} 132)`;node.style.color=t>.55?'#101410':'#D9DDD6';});
  container.querySelectorAll('[data-width]').forEach(node=>{const v=Number(node.dataset.width);if(Number.isFinite(v))node.style.width=`${Math.max(0,Math.min(100,v))}%`;});
  container.querySelectorAll('[data-x][data-y]').forEach(node=>{node.style.left=`${Number(node.dataset.x)}%`;node.style.top=`${Number(node.dataset.y)}%`;});
}
function proficiency(value) { return value>=18?'strong':value>=11?'medium':value>0?'weak':'none'; }
function positionMap(row) {
  const familiarity=Object.fromEntries(Object.entries(row.positions||{}).map(([key,v])=>[key.toUpperCase(),v]));
  const label=v=>({strong:'Forte',medium:'Média',weak:'Fraca',none:'Sem familiaridade'})[proficiency(v)];
  const pitch=`<div class="pitch position-map" aria-label="Familiaridade nas posições"><div class="pitch-lines" aria-hidden="true"></div><div class="pitch-circle" aria-hidden="true"></div>${Object.entries(positionXY).map(([p,[x,y]])=>{const v=familiarity[p];return `<span class="pitch-node ${proficiency(v)}" data-x="${x}" data-y="${y}" title="${positionNames[p]} · ${v==null?'Não lido':`${v}/20 · ${label(v)}`}">${v>0?p:''}</span>`;}).join('')}</div>`;
  return pitch+`<div class="position-legend">${['strong','medium','weak'].map((tier,i)=>`<span><i class="${tier}"></i>${['Forte','Média','Fraca'][i]}</span>`).join('')}</div>`+Object.entries(familiarity).filter(([p,v])=>positionXY[p]&&v>0).sort((a,b)=>b[1]-a[1]).map(([p,v])=>`<div class="position-rating ${proficiency(v)}"><span class="proficiency ${proficiency(v)}">${p}</span><span>${positionNames[p]}</span><small>${label(v)}</small><span class="mini-bar" title="${v}/20"><b data-width="${v*5}"></b></span></div>`).join('');
}
function compactMoney(raw,wage=false) {
  if(raw==null)return '—';
  if((wage?salaryPrefs.rate:salaryPrefs.money_rate)==null)return wage?salaryFormat(raw):moneyFormat(raw);
  const value=raw*(wage?salaryFactor():moneyFactor()),abs=Math.abs(value),scale=abs>=1e9?1e9:abs>=1e6?1e6:abs>=1e3?1e3:1;
  const symbol=new Intl.NumberFormat('pt-BR',{style:'currency',currency:salaryPrefs.currency}).formatToParts(0).find(p=>p.type==='currency').value;
  return `${value<0?'−':''}${symbol} ${num(Number((abs/scale).toFixed(scale===1?0:1)))}${scale===1e9?' bi':scale===1e6?' M':scale===1e3?' mil':''}${wage?({week:'/sem',month:'/mês',year:'/ano'})[salaryPrefs.period]:''}`;
}
function abilityBar(row) { return `<span class="mini-bar" aria-hidden="true"><i data-width="${Math.max(0,Math.min(100,(row.pa||0)/2))}"></i><b data-width="${Math.max(0,Math.min(100,(row.ca||0)/2))}"></b></span>`; }
function contractTone(row) {
  if(row.contract_state==='free')return 'free';
  if(!row.contract_end||!meta?.date)return '';
  const months=(new Date(`${row.contract_end}T12:00:00`)-new Date(`${meta.date}T12:00:00`))/86400000/30.4375;
  return months>=0&&months<=6?'urgent':months<=12&&months>=0?'soon':'';
}
function closeProfile() { ++profileVersion;currentProfile=null;document.body.classList.remove('has-profile');$('profile').inert=true;document.querySelectorAll('#table tr.selected').forEach(row=>row.classList.remove('selected')); }
function snapshotFilters() { return {fields:Object.fromEntries(fieldIds.filter(id=>$(id)).map(id=>[id,$(id).type==='checkbox'?$(id).checked:$(id).value])),conditions:{...conditions},sort,direction}; }
function restoreFilters(snapshot) { for(const [id,value] of Object.entries(snapshot.fields))if($(id)){if($(id).type==='checkbox')$(id).checked=value;else $(id).value=value;}conditions={...snapshot.conditions};sort=snapshot.sort;direction=snapshot.direction;renderConditions();syncMirrors();updatePitch();syncPickers(); }
function openFilters() { if(!meta||loading)return;filterDraft=snapshotFilters();$('advanced').showModal();$('advanced-button').setAttribute('aria-expanded','true');refreshRows(true); }
function renderShell() {
  if(!$('toolbar-actions'))return;
  $('toolbar-actions').hidden=!meta||loading;
  $('list-import').hidden=view!=='shortlist';
  document.querySelectorAll('[data-count]').forEach(node=>node.textContent=meta?num(meta.counts[node.dataset.count]):'');
  $('squad-count').textContent=meta?.managed?.[0]?.player_count?num(meta.managed[0].player_count):'';
  $('save-badge').textContent=(meta?.managed?.[0]?.club_short_name||'FM').slice(0,3).toUpperCase();
  const palette=clubPalette(meta?.managed?.[0]);
  $('save-badge').style.background=palette?.[0]||'';$('save-badge').style.color=palette?.[1]||'';
  if(!meta)$('shortlist-count').textContent='';
  $('save-date').textContent=meta?`${fmtDate(meta.date)} · ${salaryPrefs.currency}/${salaryPeriods[salaryPrefs.period].label}`:'Abrir save…';
  const tokens=Object.entries(values()).filter(([key,v])=>v&&!['sort','direction','search','availability'].includes(key)&&!(key==='squad'&&v==='all')&&!(key==='squad_scope'&&v==='first')&&!(view==='squad'&&key==='club'));
  $('active-filters').innerHTML=tokens.map(([key,v])=>{let label=key.startsWith('attr_')||key.startsWith('maxattr_')?`${attributeLabel(key.replace(/^(max)?attr_/,''))} ${key.startsWith('max')?'≤':'≥'} ${v}`:pickers[key]?`${pickerNames[key]}: ${String(v).split(',').map(value=>pickers[key].options.find(o=>o.value===value)?.label||'Não disponível').slice(0,2).join(', ')}${String(v).split(',').length>2?'…':''}`:key==='position'?`Posição: ${v}`:key==='within_shortlist'?'Na minha lista':key==='eu_national'?`UE: ${v==='yes'?'Sim':'Não'}`:`${rangeLabels[key.replace(/_(min|max)$/,'')]||key}: ${v}`;return `<span class="filter-token"><button data-open-filters title="Editar filtro">${esc(label)}</button><button data-remove-filter="${esc(key)}" aria-label="Remover ${esc(label)}">×</button></span>`;}).join('');
  $('filter-count').textContent=tokens.length;$('filter-count').hidden=!tokens.length;
  const areas=pickers.staff_area?.options||[],regions=pickers.based_region?.options||[];
  const segments=kind==='staff'?[{value:'',label:'Todos'},...areas]:kind==='clubs'?[{value:'',label:'Todos'},...regions.filter(o=>['Europa','América do Sul','América do Norte','Ásia'].includes(o.label))]:[];
  $('entity-segments').hidden=kind==='players';
  $('entity-segments').innerHTML=segments.map(o=>`<button data-entity-segment="${esc(o.value)}" aria-pressed="${String(($(kind==='staff'?'staff_area':'based_region')?.value||'')===o.value)}">${esc(o.label)}</button>`).join('');
  renderSaveMenu();
}
function renderSaveMenu() {
  if(!$('currency-segments'))return;
  $('currency-segments').innerHTML=['EUR','BRL','USD','GBP'].map(c=>`<button data-currency="${c}" aria-pressed="${salaryPrefs.currency===c}">${c}</button>`).join('');
  $('period-segments').innerHTML=Object.entries(salaryPeriods).map(([p,s])=>`<button data-period="${p}" aria-pressed="${salaryPrefs.period===p}">${({week:'Semanal',month:'Mensal',year:'Anual'})[p]}</button>`).join('');
}
const salaryPeriods = {week:{factor:1,label:'semana'},month:{factor:52/12,label:'mês'},year:{factor:52,label:'ano'}};
function salaryFactor() { return salaryPrefs.rate == null ? 1 : salaryPrefs.rate * salaryPeriods[salaryPrefs.period].factor; }
function salaryUnit() { return salaryPrefs.rate == null ? 'semanal · unidade do save' : `${salaryPrefs.currency} / ${salaryPeriods[salaryPrefs.period].label}`; }
function salaryFormat(raw) { return raw == null ? 'Não disponível' : salaryPrefs.rate == null ? `${num(raw)} unid./sem. †` : new Intl.NumberFormat('pt-BR',{style:'currency',currency:salaryPrefs.currency,minimumFractionDigits:0,maximumFractionDigits:0}).format(raw*salaryFactor()); }
const releaseColumns = ['release_fee','release_fee_domestic','release_fee_foreign'];
const moneyColumns = [...releaseColumns,'value','balance','transfer_budget_remaining','model_value','model_fee'];
const currencyRanges = ['wage','wage_budget_weekly','release_fee','value','balance','transfer_budget_remaining','model_value','model_fee'];
const currencyFilter = /^(wage|wage_budget_weekly|release_fee|value|balance|transfer_budget_remaining|model_value|model_fee)_(min|max)$/;
function moneyFactor() { return salaryPrefs.money_rate ?? 1; }
function moneyUnit() { return salaryPrefs.money_rate == null ? 'unid. do save' : salaryPrefs.currency + (salaryPrefs.money_source==='salary'?' (aprox.)':''); }
function moneyFormat(raw) { return raw == null ? '—' : salaryPrefs.money_rate == null ? `${num(raw)} unid. do save` : new Intl.NumberFormat('pt-BR',{style:'currency',currency:salaryPrefs.currency,minimumFractionDigits:0,maximumFractionDigits:0}).format(raw*moneyFactor()); }
function filterFactor(key) { return key.startsWith('wage') ? salaryFactor() : moneyFactor(); }
function updateSalaryLabels() {
  rangeLabels.wage=`Salário · ${salaryUnit()} †`;rangeLabels.wage_budget_weekly=`Orçamento salarial · ${salaryUnit()}`;
  rangeLabels.release_fee=`Rescisão geral ou do tipo selecionado · ${moneyUnit()}`;
  Object.assign(rangeLabels,{model_value:`Valor de mercado · ${moneyUnit()}`,model_fee:`Compra estimada · ${moneyUnit()}`,value:`Valor lido do save · ${moneyUnit()}`,balance:`Saldo · ${moneyUnit()}`,transfer_budget_remaining:`Orçamento de transferências · ${moneyUnit()}`});
  for(const key of currencyRanges) {
    const field=document.querySelector(`[data-range="${key}"]`);if(!field)continue;
    field.querySelector('legend').textContent=rangeLabels[key];
    field.querySelectorAll('input').forEach(input=>{input.max=String(rangeMax[key]*filterFactor(key));input.min=key==='balance'?String(-rangeMax[key]*filterFactor(key)):'0';input.step='any';});
  }
}
const pickerNames = {club:'Clubes',nation:'Nacionalidades',league:'Ligas dos clubes',based:'Países onde atua',nation_region:'Regiões da nacionalidade',based_region:'Regiões onde atua',contract_kind:'Tipos de contrato',squad_status:'Status no elenco',release_kind:'Cláusulas de liberação'};
const positionNames = {GK:'Goleiro',SW:'Líbero',DL:'Lateral esquerdo',DC:'Zagueiro',DR:'Lateral direito',DM:'Volante',ML:'Meia esquerdo',MC:'Meio-campista',MR:'Meia direito',AML:'Ponta esquerdo',AMC:'Meia ofensivo',AMR:'Ponta direito',STC:'Atacante',WBL:'Ala esquerdo',WBR:'Ala direito'};
const clauseNames = {minimum_fee_release:'Rescisão geral',minimum_fee_release_foreign:'Rescisão para clubes estrangeiros',minimum_fee_release_domestic:'Rescisão para clubes nacionais',minimum_fee_release_domestic_higher_division:'Rescisão para clubes nacionais de divisão superior',relegation_release:'Rescisão por rebaixamento',non_promotion_release:'Rescisão por não promoção',appearance_fee:'Prêmio por participação',shutout_bonus:'Prêmio por jogo sem sofrer gols',unused_substitute_fee:'Prêmio como reserva não utilizado',top_division_relegation_salary_drop:'Redução salarial por rebaixamento (%)',optional_extension_by_club:'Extensão opcional pelo clube (anos)'};
pickerNames.staff_area='Áreas do staff';pickerNames.staff_role='Cargos do staff';

async function api(path, body) {
  const response = await fetch(`api/${path}`, body ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)} : {});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Erro ${response.status}`);
  return data;
}
function notice(message = '', error = false) {
  clearTimeout(toastTimer);
  $('message').textContent = message;
  $('message').hidden = !message;
  $('message').classList.toggle('error', error);
  if(message&&!error&&!loading)toastTimer=setTimeout(()=>{$('message').hidden=true;undoList=null;},2800);
}
function action(fn) { return (...args) => Promise.resolve(fn(...args)).catch(error => notice(error.message, true)); }
function values() {
  const filters = {};
  for (const id of fieldIds) {
    const control = $(id); if (!control) continue;
    if (control.disabled) continue;
    const value = control.type === 'checkbox' ? (control.checked ? '1' : '') : control.value;
    if (value) filters[id] = currencyFilter.test(id) ? String(Number((Number(value)/filterFactor(id)).toFixed(6))) : value;
  }
  if (view === 'squad' && meta?.managed?.length) filters.club = String(meta.managed[0].club_uid);
  return {...filters,...conditions,sort,direction};
}
function query(offset = 0) {
  const filters = {...values(),kind,offset,limit:$('page-size').value,columns:visibleColumns[kind].join(',')};
  if (view === 'shortlist') filters.shortlist = '1';
  if (view === 'squad') filters.club = meta?.managed?.[0]?.club_uid ?? '-1';
  return new URLSearchParams(filters);
}
function validateControls() {
  for (const id of fieldIds) if ($(id) && !$(id).disabled && !$(id).checkValidity()) {
    $(id).reportValidity(); return false;
  }
  for (const key of Object.keys(rangeMax)) {
    const min = $(key+'_min'), max = $(key+'_max');
    if (min?.value && max?.value && Number(min.value)>Number(max.value)) { notice(`Mínimo maior que o máximo: ${rangeLabels[key]}.`,true); return false; }
  }
  for (const [key,value] of Object.entries(conditions)) {
    if (key.startsWith('attr_') && conditions['max'+key] && Number(value)>Number(conditions['max'+key])) { notice(`Mínimo maior que o máximo: ${attributeLabel(key.slice(5))}.`,true); return false; }
  }
  if ($('age_min').value && $('age_max').value && Number($('age_min').value) > Number($('age_max').value)) {
    notice('A idade mínima precisa ser menor ou igual à máxima.', true); return false;
  }
  return true;
}
function renderListStatus() {
  const noun=kind==='players'?'jogadores':kind==='staff'?'pessoas':'clubes';
  $('list-title').textContent=titles[view];
  $('result-count').textContent=`${view==='squad'&&meta?.managed?.length?(meta.managed[0].club_short_name||meta.managed[0].club_name)+' · ':''}${num(total)} ${noun}`;
  $('filter-result-count').textContent=`${num(total)} resultados · filtros combinados`;
  $('sort-summary').textContent=`${columnLabel(sort)} ${direction==='desc'?'↓':'↑'}${kind==='players'?' · desempate pela soma':''}`;
  $('page-info').textContent=total?`${num(rows.length)} de ${num(total)} carregados`:'Nenhum resultado';
  $('next').disabled=loading||$('workspace').getAttribute('aria-busy')==='true'||rows.length>=total;
  $('next').textContent=moreRequest?'Carregando…':rows.length>=total?'Todos carregados':`Carregar mais ${num(Math.min(Number($('page-size').value),total-rows.length))} ${noun}`;
  renderShell();
}
async function refreshRows(reset = true) {
  if (!meta || loading || !validateControls()) return;
  if(filterDraft&&$('advanced').open) {
    const version=++draftVersion;
    const data=await api(`rows?${query(0)}`);
    if(version===draftVersion&&filterDraft)$('filter-result-count').textContent=`${num(data.total)} resultados`;
    return;
  }
  const append=!reset;
  if (append && ($('workspace').getAttribute('aria-busy')==='true' || rows.length>=total)) return;
  const version = ++requestVersion;
  moreRequest=append?version:0;
  $('workspace').setAttribute('aria-busy','true');
  $('next').disabled=true;
  if(append)$('next').textContent='Carregando…';
  let data;
  try { data = await api(`rows?${query(append?rows.length:0)}`); }
  catch(error) { if(version===requestVersion){moreRequest=0;$('workspace').setAttribute('aria-busy','false');renderListStatus();}throw error; }
  if (version !== requestVersion) return;
  moreRequest=0;
  $('workspace').setAttribute('aria-busy','false');
  const scroll=document.querySelector('.table-scroll'), scrollTop=scroll.scrollTop;
  rows = append?[...rows,...data.rows]:data.rows; total = data.total;
  if(kind==='players')$('shortlist-count').textContent = num(data.shortlist_count);
  renderListStatus();
  $('export').disabled = !data.shortlist_count || kind === 'clubs';
  renderTable();
  scroll.scrollTop=append?scrollTop:0;
}
const labels = {height_cm:'Altura (cm) †',balance:'Saldo · unidade do save',transfer_budget_remaining:'Transferências · unidade do save',wage_budget_weekly:'Orçamento salarial',stadium_seated_capacity:'Estádio: lugares sentados',stadium_expansion_capacity:'Estádio: expansão',name:'Nome',age:'Idade',club_name:'Clube',ca:'CA †',pa:'PA †',attribute_sum:'Soma (36)',goalkeeping_sum:'Goleiro (11)',rating:'Nota est. %',nation_id:'País',reputation:'Reputação',positions:'Posição',ability_difference:'PA − CA †',rep_home:'Rep. nacional',rep_current:'Rep. atual',rep_world:'Rep. mundial',wage:'Salário †',value:'Valor',release_fee:'Rescisão geral · unid. save',release_fee_domestic:'Rescisão nacional · unid. save',release_fee_foreign:'Rescisão internacional · unid. save',ca_mean:'CA médio †',pa_mean:'PA médio †',age_mean:'Idade média',player_count:'Jogadores',ca_count:'CA lidos',pa_count:'PA lidos',age_count:'Idades lidas',team_slot:'Equipe †'};
function columnLabel(key) { if(moneyColumns.includes(key))return `${({release_fee:'Rescisão geral',release_fee_domestic:'Rescisão nacional',release_fee_foreign:'Rescisão internacional',model_value:'Valor de mercado',model_fee:'Compra estimada',value:'Valor lido do save',balance:'Saldo',transfer_budget_remaining:'Transferências'})[key]} · ${moneyUnit()}`; return key==='attribute_sum'&&kind==='staff'?`Soma de habilidades (${staffScoring.length}) †`:key === 'wage_budget_weekly' ? `Orçamento salarial · ${salaryUnit()}` : key === 'wage' ? `Salário · ${salaryUnit()} †` : key === 'eu_national' ? 'EU' : key === 'nation_id' ? kind==='clubs'?'País':'Nacionalidades' : key.startsWith('attr_') ? attributeLabel(key.slice(5)) : labels[key] || key; }
labels.stadium_name='Estádio';labels.staff_role='Função †';labels.league_name='Liga do clube †';labels.staff_area='Área do staff';
labels.contract_end='Contrato';
function euLabel(value) { return value===true?'Sim':value===false?'Não':'Indisponível'; }
function nationalityLabel(row) { return row.nationalities?.map(n=>`${n.name||'Nome indisponível'}${n.id===row.nation_id?' (principal)':''}${n.is_eu?' · UE':''}`).join('; ') || 'Nome indisponível'; }
function orderedColumns(columns, forKind = kind) {
  const order = Object.values(columnGroups[forKind] || {}).flat();
  const rank = key => { const index = order.indexOf(key); return index < 0 ? order.length : index; };
  return [...columns].sort((a,b) => rank(a)-rank(b));
}
function renderColumnOptions() {
  $('column-search').value='';
  $('column-search-empty').hidden=true;
  const sections = {...columnGroups[kind]};
  const known = Object.values(sections).flat();
  const other = visibleColumns[kind].filter(key => !known.includes(key));
  if(other.length)sections['Outras colunas salvas']=other;
  $('column-options').innerHTML=`<div class="column-sections">${Object.entries(sections).map(([group,keys])=>`<section class="column-section"><h3>${esc(group)}</h3>${keys.map(key=>`<label class="checkbox-label"><input data-column="${key}" type="checkbox" ${visibleColumns[kind].includes(key)?'checked':''} ${key==='name'?'disabled':''}>${esc(columnLabel(key))}</label>`).join('')}</section>`).join('')}</div>${kind==='players'?'<div class="column-presets"><span>Atributos</span>'+['Ataque','Criação','Defesa','Físico','Limpar'].map(label=>`<button data-column-preset="${label}">${label}</button>`).join('')+'</div>':''}`;
}
function filterColumnOptions() {
  const normalize = value => value.normalize('NFD').replace(/\p{Diacritic}/gu,'').toLocaleLowerCase('pt-BR');
  const search = normalize($('column-search').value.trim());
  let matches = 0;
  for(const section of $('column-options').querySelectorAll('.column-section')) {
    let count = 0;
    for(const label of section.querySelectorAll('.checkbox-label')) {
      label.hidden = !normalize(label.textContent).includes(search);
      if(!label.hidden)count++;
    }
    section.hidden = count === 0;
    matches += count;
  }
  $('column-search-empty').hidden = matches > 0;
}
function columnWidth(key, pairedAbility=false) {
  return columnWidths[kind][key] ?? (key==='ca'&&pairedAbility?128:key==='nation_id'&&kind==='clubs'?140:key.startsWith('attr_')?46:defaultWidths[key]||(moneyColumns.includes(key)?110:90));
}
function sizeTable() {
  $('table').style.width=`${[...$('table').querySelectorAll('thead th')].reduce((total,th)=>total+parseFloat(th.style.width),0)}px`;
}
function resizeColumn(handle, width) {
  const th=handle.closest('th');
  width=Math.max(40,Math.min(1000,Math.round(width)));
  columnWidths[kind][th.dataset.columnKey]=width;
  th.style.width=`${width}px`;handle.setAttribute('aria-valuenow',width);sizeTable();
}
function saveColumnWidths() {
  clearTimeout(widthSaveTimer);
  widthSaveTimer=setTimeout(action(()=>api('layouts',{...visibleColumns,_widths:columnWidths})),200);
}
function renderTable() {
  let columns = [...visibleColumns[kind]];
  if (kind === 'players' && $('position').value.split(',').includes('GK') && !columns.includes('goalkeeping_sum')) columns.push('goalkeeping_sum');
  columns = orderedColumns(columns);
  const pairedAbility=columns.includes('ca')&&columns.includes('pa');
  if(pairedAbility)columns=columns.filter(key=>key!=='pa');
  const person = kind !== 'clubs';
  const header=key=>{
    const textKeys=['name','club_name','positions','stadium_name','league_name','nation_id','eu_national','staff_role','staff_area','team_slot'];
    const sorted=key===sort||(key==='ca'&&pairedAbility&&sort==='pa');
    const button=k=>`<button data-sort="${k}" title="Ordenar por ${esc(columnLabel(k))}">${pairedAbility&&key==='ca'?k.toUpperCase():k==='nation_id'&&kind!=='clubs'?'Nac':esc(columnLabel(k))}${k===sort?(direction==='desc'?' ↓':' ↑'):''}</button>`;
    const resize=`<span class="column-resize" role="separator" tabindex="0" aria-label="Largura de ${esc(columnLabel(key))}" aria-orientation="vertical" aria-valuemin="40" aria-valuemax="1000" aria-valuenow="${columnWidth(key,pairedAbility)}" title="Arraste para ajustar a largura. Use ← e → no teclado; dois cliques para restaurar."></span>`;
    return `<th scope="col" data-column-key="${key}" class="${key==='attribute_sum'?'sum':textKeys.includes(key)?'':'numeric'}" ${sorted?`aria-sort="${direction==='desc'?'descending':'ascending'}"`:''}>${key==='positions'?'Posição':key==='ca'&&pairedAbility?`<span class="ability-heading">${button('ca')}<span>/</span>${button('pa')}</span>`:button(key)}${resize}</th>`;
  };
  $('table').querySelector('thead').innerHTML=`<tr>${person?`<th scope="col" class="check"><input id="select-all" type="checkbox" aria-label="${kind==='staff'?'Selecionar todos os profissionais carregados':'Selecionar todos os jogadores carregados'}"></th>`:''}${columns.map(header).join('')}</tr>`;
  if(kind==='staff')$('table').querySelector('[data-sort="attribute_sum"]')?.setAttribute('title',`Soma dos ${staffScoring.length} atributos profissionais ativos, peso igual, máximo ${staffScoring.length*20}. Campos legados, personalidade e estilo não entram.`);
  $('table').querySelector('tbody').innerHTML = rows.length ? rows.map(row => `<tr data-uid="${row.uid}" class="${currentProfile?.row.uid === row.uid ? 'selected' : ''}">${person ? `<td class="check"><input type="checkbox" data-select="${row.uid}" aria-label="Selecionar ${esc(row.name)}" ${selection.has(row.uid) ? 'checked' : ''}></td>` : ''}${columns.map(key => {
    if (key === 'name') return `<td class="name"><button data-profile="${row.uid}" ${kind==='clubs'?`title="${esc(row.name)}"`:''}>${kind==='clubs'?badge(row.short_name||row.name,row)+' ':''}${esc((kind==='clubs'?row.short_name:null) || row.name || `Registro ${row.uid}`)}</button>${person&&row.shortlisted?'<span class="fine" title="Na lista" aria-label="Na lista"> ★</span>':''}</td>`;
    if(key==='contract_end')return `<td class="numeric tone-${contractTone(row)}" title="${esc(row.contract_state==='free'?'Sem contrato':fmtDate(row.contract_end))}">${row.contract_state==='free'?'Livre':compactContract(row.contract_end)}</td>`;
    if (key === 'league_name') return `<td>${esc(row.league_name||'Liga não lida')}</td>`;
    if (key === 'stadium_name') return `<td>${esc(row.stadium_name||'Nome não lido')}</td>`;
    if (key === 'staff_area' || key === 'staff_role') return `<td>${esc(row[key])}</td>`;
    if (key==='attribute_sum'&&kind==='staff')return `<td class="numeric" title="Soma de ${staffScoring.length} atributos profissionais ativos; leitura experimental. Ausente quando algum deles não foi lido.">${row.attribute_sum==null?'Não disponível':num(row.attribute_sum)}</td>`;
    if (key === 'positions') return `<td>${positionChips(row.natural_positions||[])}</td>`;
    if(key.startsWith('attr_'))return `<td class="numeric" title="${esc(attributeLabel(key.slice(5)))}">${heat(row[key])}</td>`;
    if (key === 'team_slot') return `<td title="Vínculo de equipe decodificado; categoria exata ainda sem nome confirmado">${row.team_slot==null?'—':row.team_slot===0?'Principal':`Secundária ${row.team_slot}`}</td>`;
    if (key === 'club_name') return `<td title="${esc(row.club_name)}"><span class="cell-club">${badge(row.club_short_name||row.club_name,row)}<span>${esc(row.club_short_name || row.club_name || 'Sem vínculo decodificado')}</span></span></td>`;
    if (key === 'nation_id') {const names=(row.nationalities||[]).map(n=>n.name).filter(Boolean);if(!names.length&&row.nation_name)names.push(row.nation_name);const flags=names.slice(0,kind==='players'?3:1).map(name=>countryFlag(name)).join('');return `<td class="nationality-cell" title="${esc(names.join('; '))}"><span class="fm-flags">${flags}</span>${kind==='clubs'||!flags?esc(names[0]||'Nome indisponível'):''}</td>`;}
    if(key==='ca'&&pairedAbility)return `<td class="numeric"><span class="ability-pair"><b>${num(row.ca)}</b>${abilityBar(row)}<span class="ability-pa">${num(row.pa)}</span></span></td>`;
    if (key === 'eu_national') return `<td>${euLabel(row.eu_national)}</td>`;
    if (key === 'player_count' && row.player_count === 0) return '<td class="empty-squad">Nenhum jogador lido</td>';
    if (moneyColumns.includes(key)) return `<td class="numeric" title="${esc(moneyFormat(row[key]))}">${key.startsWith('model_')&&row[key]!=null&&(key!=='model_value'||row.model_value_basis==='model')?'≈ ':''}${compactMoney(row[key])}</td>`;
    if (key === 'wage' || key === 'wage_budget_weekly') return `<td class="numeric" title="${esc(salaryFormat(row[key]))}">${compactMoney(row[key],true)}</td>`;
    return `<td class="numeric ${key === 'attribute_sum' ? 'sum' : key === 'ca' || key === 'pa' ? 'ability' : ''}" ${key.endsWith('_mean')?`title="${row[key.replace('_mean','_count')]} de ${row.player_count} jogadores com valor disponível"`:''}>${key === 'rating' || key.endsWith('_mean') ? row[key] == null ? '—' : row[key].toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1}) : num(row[key])}</td>`;
  }).join('')}</tr>`).join('') : `<tr><td class="empty-row" colspan="${columns.length+(person?1:0)}">${view === 'shortlist' ? 'Sua lista está vazia. Marque jogadores na busca e clique em Adicionar à lista.' : view === 'squad' && !meta.managed.length ? 'O clube do treinador não foi identificado neste save. Use o filtro de clube na aba Jogadores.' : 'Nenhum registro atende aos filtros. Reduza os critérios ou clique em Limpar.'}</td></tr>`;
  $('table').querySelector('thead tr').insertAdjacentHTML('afterbegin','<th scope="col" class="row-number" title="Número da linha nos filtros e na ordenação atuais">Nº</th>');
  $('table').querySelectorAll('tbody tr[data-uid]').forEach((row,index)=>row.insertAdjacentHTML('afterbegin',`<td class="row-number">${num(index+1)}</td>`));
  $('table').querySelectorAll('thead th').forEach(th=>{const width=th.classList.contains('row-number')?36:th.classList.contains('check')?32:columnWidth(th.dataset.columnKey,pairedAbility);th.style.width=`${width}px`;});
  sizeTable();
  $('table').querySelectorAll('thead [data-sort^="attr_"]').forEach(button=>{button.title=attributeLabel(button.dataset.sort.slice(5));button.textContent=button.title.slice(0,3)+(button.dataset.sort===sort?(direction==='desc'?' ↓':' ↑'):'');});
  const empty=$('table').querySelector('.empty-row');if(empty)empty.colSpan++;
  applyDataStyles($('table'));
  updateSelection();
}
function updateSelection() {
  const unavailable=loading||shortlistBusy||!meta, count=selection.size;
  $('selection-actions').hidden=kind==='clubs'||!meta||count===0;
  $('selection-count').textContent=`${num(count)} ${count===1?'selecionado':'selecionados'}`;
  $('compare').disabled=unavailable||count!==2;
  $('selection-hint').textContent=count>2?'Marque apenas dois para comparar.':'';
  $('list-add').disabled=unavailable||count===0;
  $('list-add').hidden=view==='shortlist';
  $('list-remove').disabled=unavailable||count===0;
  $('list-remove').hidden=view!=='shortlist'&&!$('within_shortlist').checked;
  $('clear-selection').disabled=unavailable||count===0;
  const all=$('select-all');
  if(all&&kind!=='clubs') {
    const marked=rows.filter(row=>selection.has(row.uid)).length;
    all.checked=rows.length>0&&marked===rows.length;
    all.indeterminate=marked>0&&marked<rows.length;
    all.disabled=unavailable||rows.length===0;
    all.title=`Selecionar ou desmarcar as ${num(rows.length)} linhas já carregadas desta pesquisa.`;
  }
  document.querySelectorAll('[data-select],#profile-watch,#profile-select').forEach(control=>{
    control.disabled=unavailable;
    if(control.dataset.select)control.checked=selection.has(Number(control.dataset.select));
  });
  if(currentProfile&&$('profile-select'))$('profile-select').textContent=selection.has(currentProfile.row.uid)?'Desmarcar':'Selecionar';
}
async function changeShortlist(uids, add, allowUndo=true) {
  if(shortlistBusy||loading||kind==='clubs'||!uids.length)return;
  const requestedKind=kind, requestedView=viewVersion, ids=new Set(uids);
  shortlistBusy=true;updateSelection();
  try {
    const previous=new Set();
    if(allowUndo)for(let offset=0;;offset+=200){const data=await api(`rows?kind=${kind}&shortlist=1&offset=${offset}&limit=200&columns=name`);data.rows.forEach(row=>previous.add(row.uid));if(offset+data.rows.length>=data.total)break;}
    if(kind!==requestedKind||viewVersion!==requestedView||loading)return;
    const result=await api('shortlist/batch',{kind,uids:[...ids],action:add?'add':'remove'});
    if(kind!==requestedKind||viewVersion!==requestedView||loading)return;
    rows.forEach(row=>{if(ids.has(row.uid))row.shortlisted=add;});
    if(currentProfile&&ids.has(currentProfile.row.uid)){currentProfile.shortlisted=add;renderProfile();}
    if(kind==='players')$('shortlist-count').textContent=num(result.shortlist_count);
    $('export').disabled=!result.shortlist_count;
    const verb=add?'adicionado':'removido';
    notice(`${num(result.changed)} ${verb}${result.changed===1?'':'s'} à lista.`);
    const changedIds=[...ids].filter(uid=>previous.has(uid)!==add);
    if(allowUndo&&changedIds.length){undoList={kind:requestedKind,career:meta.path,uids:changedIds,add:!add};$('message').insertAdjacentHTML('beforeend','<button id="undo-list">Desfazer</button>');}
    if(view==='shortlist'||$('within_shortlist').checked){
      if(!add)ids.forEach(uid=>selection.delete(uid));
      return await refreshRows(true);
    }
    renderListStatus();renderTable();
  } finally { shortlistBusy=false;updateSelection(); }
}
async function showProfile(uid) {
  if(currentProfile?.row.uid===uid){closeProfile();renderTable();return;}
  const version = ++profileVersion;
  const data = await api(`profile?kind=${kind}&uid=${uid}`);
  if (version !== profileVersion) return;
  currentProfile = data; renderProfile(); renderTable();
}
function definition(items) {
  return `<dl>${items.map(([key,value]) => `<div><dt>${esc(key)}</dt><dd>${esc(value ?? 'Não disponível')}</dd></div>`).join('')}</dl>`;
}
function attributeValue(value,inverse=false) { const effective=inverse&&value!=null?21-value:value;return `<span class="attribute-value ${effective >= 16 ? 'high' : effective>=13?'normal':effective>=9?'medium':'low'}">${value == null ? '—' : esc(value)}</span>`; }
function attributeGroup(row, title) {
  const source = title === 'Personalidade' ? row.personality : title === 'Profissionais' ? row.professional_attributes : row.attributes;
  if (!source) return '';
  const fields = groups[title];
  const sum = {'Técnicos':row.technical_sum,'Mentais':row.mental_sum,'Físicos':row.physical_sum,'Goleiro':row.goalkeeping_sum,'Profissionais':row.attribute_sum}[title];
  return `<section class="attribute-group"><h3>${esc(title)}${sum == null ? '' : `<span>${sum}</span>`}</h3><div class="attribute-items">${Object.entries(fields).map(([key,label]) => `<div class="attribute-row"><span title="${esc(label)}">${esc(label)}</span>${attributeValue(source[key],['injury_proneness','dirtiness','controversy'].includes(key))}</div>`).join('')}</div></section>`;
}
function professionalGroups(row) {
  return ['Gestão e liderança','Treinamento','Recrutamento','Saúde','Goleiros (legado)'].map(title=>{
    const keys=(columnGroups.staff?.[title]||[]).map(key=>key.slice(5));
    if(!keys.length)return '';
    return `<section class="attribute-group"><h3>${title}</h3><div class="attribute-items">${keys.map(key=>`<div class="attribute-row"><span title="${esc(attributeLabel(key))}">${esc(attributeLabel(key))}</span>${attributeValue(row.professional_attributes?.[key])}</div>`).join('')}</div></section>`;
  }).join('');
}
function renderProfile() {
  if (!currentProfile) return;
  const {row:r,history,shortlisted} = currentProfile;
  const player = kind === 'players', staff = kind === 'staff';
  const tabs = kind === 'clubs' ? {attributes:'Clube',squad:'Elenco',finance:'Finanças',loans:'Empréstimos'} : {attributes:'Atributos',...(player?{roles:'Posições'}:{}),transfer:'Contrato',hidden:'Ocultos',...(player ? {report:'Relatório',history:'Evolução'} : {preferences:'Estilo'})};
  if(!(profileTab in tabs))profileTab='attributes';
  let content = '';
  if (profileTab === 'attributes') {
    const identity=definition([['Idade',r.age == null ? null : `${r.age} anos`],['Nascimento',fmtDate(r.birth_date)],['Nacionalidades',nationalityLabel(r)],['Possui nacionalidade UE',euLabel(r.eu_national)],['ID do FM',r.unique_id],['Liga do clube †',r.league_name||'Liga não lida'],...(player ? [['Altura',r.height_cm == null ? null : `${r.height_cm} cm`],['Pé esquerdo / direito',`${r.left_foot ?? '—'} / ${r.right_foot ?? '—'}`],['Diferença PA − CA †',r.ability_difference],['Reputação nacional',r.rep_home],['Reputação atual',r.rep_current],['Reputação mundial',r.rep_world],['Condição (valor bruto)',r.raw_condition],['Ritmo (valor bruto)',r.raw_match_sharpness]] : [])]);
    if (player) content = `${['Técnicos','Mentais','Físicos',...(r.positions?.gk >= 15 ? ['Goleiro'] : [])].map(g => attributeGroup(r,g)).join('')}<details class="role-row"><summary>Identificação e leitura</summary>${identity}<p class="fine">Soma = técnicos + mentais + físicos: 36 atributos, peso igual, máximo 720. Goleiro tem soma própria de 11 atributos.</p></details>`;
    if (staff) content = professionalGroups(r)+`<h3>Contrato</h3>`+definition([[`Salário · ${salaryUnit()} †`,salaryFormat(r.wage)],['Contrato até',fmtDate(r.contract_end)],['Nascimento',fmtDate(r.birth_date)],['ID do FM',r.unique_id],['Nacionalidades',nationalityLabel(r)],['Alguma cidadania da União Europeia',euLabel(r.eu_national)],['Função',r.staff_role],['Área do staff',r.staff_area],[`Soma de habilidades (${staffScoring.length}) †`,r.attribute_sum]])+`<details class="role-row"><summary>Sobre a leitura profissional</summary><p class="fine">Cargos pelo contrato atual ou vínculo médico e assentos do clube. Vínculos incompletos continuam sem cargo identificado. Soma dos ${staffScoring.length} atributos profissionais ativos, peso igual, máximo ${staffScoring.length*20}. Campos legados, estilo e personalidade ficam fora da soma e do placar.</p></details>`;
    if (kind === 'clubs') content = definition([['Nome',r.short_name || r.name],['Nome completo',r.name],['ID do FM',r.unique_id],['País',r.nation_name || 'Nome indisponível'],['Reputação',r.reputation],['Liga do clube †',r.league_name||'Liga não lida'],['Última posição na liga',r.last_league_position || null],['Equipes no save',r.teams?.length],[`Saldo · ${moneyUnit()}`,moneyFormat(r.balance)],[`Transferências restantes · ${moneyUnit()}`,moneyFormat(r.transfer_budget_remaining)],[`Orçamento salarial · ${salaryUnit()}`,salaryFormat(r.wage_budget_weekly)],['Data dos valores financeiros',fmtDate(r.finance_date)],['Origem das finanças',r.finance_source==='current'?'Posição atual no save':r.finance_source==='monthly'?'Histórico mensal':'Não disponível'],['Estádio',r.stadium_name||(r.stadium_seated_capacity==null?null:'Nome não lido')],['Lugares sentados',r.stadium_seated_capacity],['Capacidade de expansão',r.stadium_expansion_capacity]]) + '<p class="fine">Finanças atuais quando identificadas; nos demais clubes, o histórico mensal mantém sua data original. Valores experimentais disponíveis apenas nos clubes cobertos pelo leitor. Estádio e liga pelo vínculo atual do clube; jogos em casa como alternativa quando o vínculo direto não é lido. Nomes usam a instalação local do FM, quando disponíveis. Lugares sentados não equivalem necessariamente à capacidade total. Instalações de treino, formação, uniformes e melhores formações ainda pendentes.</p>';
    if(kind==='clubs')content+=definition([['Categoria',r.gender==='male'?'Masculino (base de referência)':r.gender==='female'?'Feminino (base de referência)':'Categoria não identificada']]);
  } else if (profileTab === 'finance' && kind === 'clubs') {
    content=definition([[`Saldo · ${moneyUnit()}`,moneyFormat(r.balance)],[`Transferências restantes · ${moneyUnit()}`,moneyFormat(r.transfer_budget_remaining)],[`Orçamento salarial · ${salaryUnit()}`,salaryFormat(r.wage_budget_weekly)],['Data dos valores',fmtDate(r.finance_date)],['Origem',r.finance_source==='current'?'Posição atual no save':r.finance_source==='monthly'?'Histórico mensal':'Não disponível']]);
  } else if (profileTab === 'loans' && kind === 'clubs') {
    content = '<h3>Empréstimos financeiros</h3><p class="fine">Dívida líquida atual: não disponível. Os valores originais abaixo não são o saldo devedor restante. Dívidas e créditos de transferências ainda não foram lidos.</p>';
    if (!Array.isArray(r.loans)) content += '<p>Empréstimos não identificados neste clube.</p>';
    else if (!r.loans.length) content += '<p>Nenhum empréstimo financeiro registrado na lista lida. Isso não significa dívida líquida zero.</p>';
    else content += r.loans.map((loan,index) => `<section class="attribute-group"><h3>Empréstimo ${index+1}</h3>${definition([
      ['Tipo',({1:'Banco',5:'Município'})[loan.kind_raw]||'Tipo não identificado'],
      [`Valor original · ${moneyUnit()}`,moneyFormat(loan.original_amount)],
      [`Parcela por mês · ${moneyUnit()}`,moneyFormat(loan.monthly_payment)],
      [`Juros por mês · ${moneyUnit()}`,moneyFormat(loan.monthly_interest)],
      [`Pagamento condicional · ${moneyUnit()}`,moneyFormat(loan.conditional_amount)],
      ['Início',fmtDate(loan.start_date)],['Término',fmtDate(loan.end_date)]])}</section>`).join('');
  } else if (profileTab === 'hidden') content = `${player ? attributeGroup(r,'Ocultos') : ''}${attributeGroup(r,'Personalidade')}<p class="fine">Propensão a lesões, jogo sujo e controvérsia: valores menores podem ser desejáveis. Use o filtro “No máximo”.</p>`;
  else if (profileTab === 'transfer') {
    const c = {...(r.contract || {}),wage:r.wage,start:r.contract_start,end:r.contract_end};
    content = `<div class="contract-card tone-${contractTone(r)}"><h3>Contrato</h3><strong>${r.contract_state==='free'?'Sem contrato':r.contract_end?'Até '+fmtDate(r.contract_end):'Não identificado'}</strong></div>`+definition([['Clube',r.club_short_name || r.club_name],['Vínculo',({free:'Sem contrato',contracted:'Com contrato',unknown:'Não identificado'})[r.contract_state]||'Não identificado'],['Contrato desde',fmtDate(c.start)],['Contrato até',fmtDate(c.end)],['Tipo',c.kind==='unknown'?'Nome indisponível':c.kind?.replaceAll('_',' ')],['Status no elenco',c.squad_status?.replaceAll('_',' ')],[`Salário · ${salaryUnit()} †`,salaryFormat(c.wage)],...(player ? [[`Valor lido do save · ${moneyUnit()}`,moneyFormat(r.value)],['Na lista de transferências †',r.transfer_listed==null?'Não disponível':r.transfer_listed?'Sim':'Não'],['Na lista de empréstimos †',r.loan_listed==null?'Não disponível':r.loan_listed?'Sim':'Não'],['Emprestado',r.on_loan==null?'Não disponível':r.on_loan ? 'Sim' : 'Não'],['Clube de origem',r.loan_parent_club_name],['Fim do empréstimo',fmtDate(r.loan_end)]] : [])]);
    if(player && r.value_note)content+=`<p class="fine">${esc(r.value_note)}</p>`;
    if(player)content+='<h3>Estimativas de negociação</h3>'+definition([
      [`Valor de mercado · ${moneyUnit()}`,r.model_value==null?'Não disponível':`${r.model_value_basis==='model'?'≈ ':''}${moneyFormat(r.model_value)}`],
      ['Faixa de valor do modelo',r.model_value_low==null?'Não disponível':`${moneyFormat(r.model_value_low)} – ${moneyFormat(r.model_value_high)}`],
      [`Compra estimada · ${moneyUnit()}`,r.model_fee==null?'Não disponível':`≈ ${moneyFormat(r.model_fee)}`],
      ['Faixa de compra do modelo',r.model_fee_low==null?'Não disponível':`${moneyFormat(r.model_fee_low)} – ${moneyFormat(r.model_fee_high)}`],
      ['Origem do valor de mercado',({save:'Lido do save',model:'Estimado pelo modelo',free:'Sem contrato'})[r.model_value_basis]],
      ['Base da compra',({save:'Valor lido do save',model:'Valor estimado pelo modelo',free:'Sem contrato: sem taxa de transferência'})[r.model_fee_basis]],
    ])+`<p class="fine">Modelo FMSuperScout: usa o valor positivo do save quando disponível; nas lacunas, estima por reputação, idade e prazo contratual; compra considera listagem, salário relativo e reputação do seu clube quando lidos. Estimativas experimentais: a regressão apresentou desvios grandes nos controles de Corinthians e Real Madrid. As faixas são do modelo, não as exibidas pelo FM ou garantias de proposta aceita. Não inclui disputa entre compradores, orçamento, comissões ou status “não está à venda” ainda sem leitura confirmada. Campos do save e cláusulas são preservados. ${esc((r.model_assumptions||[]).join(' '))}</p>`;
    if(c.clauses?.length)content+='<h3>Cláusulas do contrato</h3>'+definition(c.clauses.map(clause=>[clauseNames[clause.kind]||(clause.kind==='unknown'?`Código ${clause.kind_code}`:clause.kind.replaceAll('_',' ')),clause.value==null?'Parâmetro: '+(clause.parameter??'—'):moneyFormat(clause.value)]));
    content += `<p class="fine">Salários usam as preferências de exibição. ${salaryPrefs.money_rate==null?'Valores sem conversão conferida continuam identificados como unidades do save.':salaryPrefs.money_source==='salary'?'Valores monetários usam a taxa salarial aproximada; confira uma rescisão em Moeda / salários para melhorar a precisão.':'Valores monetários usam a conversão conferida por uma rescisão nesta carreira.'} Referências abreviadas e arredondamentos do FM podem gerar pequenas diferenças. Valor de mercado usa a mesma conversão monetária; preço efetivamente aceito depende da negociação no FM. Cláusulas podem ter condições específicas.</p>`;
  } else if (profileTab === 'roles') {
    content = positionMap(r)+'<details class="role-row"><summary>Avaliações por posição</summary><p class="fine">Nota Matt Scout: média ponderada dos atributos × 5 × (0,75 + 0,25 × familiaridade/20). Estimativa própria por posição; não replica os percentuais do Genie.</p>';
    content += Object.entries(r.roles).sort((a,b)=>(b[1]??-1)-(a[1]??-1)).map(([key,score]) => `<details class="role-row"><summary><span>${esc(roles[key].name)} · posição ${r.positions?.[roles[key].position] ?? '—'}/20</span><strong>${score == null ? '—' : `${num(score)}%`}</strong></summary><p>${Object.entries(roles[key].weights).map(([attr,weight]) => `${esc(attributeLabel(attr))} × ${weight}`).join(' · ')}</p></details>`).join('');
    content += '<h3>Familiaridade nas posições</h3>' + definition(Object.entries(r.positions || {}).map(([position,value]) => [position.toUpperCase(),`${value}/20`]));
    if (r.traits_code?.length) content += `<p class="fine">${r.traits_code.length} movimentos ainda sem nome identificado pelo leitor.</p>`;
    content+='</details>';
  } else if (profileTab === 'report') {
    const all = {...(r.attributes||{})};
    const visible = Object.entries(all).filter(([key,v]) => ['Técnicos','Mentais','Físicos'].some(g => key in groups[g]) && v != null);
    const strengths = [...visible].sort((a,b)=>b[1]-a[1]).slice(0,5);
    const weaknesses = [...visible].sort((a,b)=>a[1]-b[1]).slice(0,5);
    content = `<div class="report"><h3>Melhor nota entre posições familiares</h3><p>${esc(roles[r.best_role]?.name || 'Não disponível')} · ${r.rating == null ? '—' : `${num(r.rating)}% (estimativa)`}</p><h3>Maiores atributos</h3><ul>${strengths.map(([key,value]) => `<li>${esc(attributeLabel(key))}: ${value}</li>`).join('')}</ul><h3>Menores atributos</h3><ul>${weaknesses.map(([key,value]) => `<li>${esc(attributeLabel(key))}: ${value}</li>`).join('')}</ul><p class="fine">Menores atributos não são necessariamente fraquezas para a função escolhida. Este relatório descreve os dados; não prevê desempenho.</p></div>`;
  } else if(profileTab==='preferences') {
    content='<p class="fine">Preferências de estilo do profissional. Não representam habilidade de treinamento ou avaliação.</p>'+definition(Object.entries(r.preferences||{}).map(([key,value])=>[key.replaceAll('_',' '),value]));
  } else if(profileTab==='squad') {
    content=Object.entries(r.squad_metrics||{}).map(([scope,m])=>`<h3>${scope==='first'?'Equipe principal':'Todos os vinculados'}</h3>${definition([['Jogadores',m.player_count===0?'Nenhum jogador lido':m.player_count],['CA médio †',m.ca_mean==null?'—':num(Math.round(m.ca_mean*10)/10)],['CA lidos',m.player_count?`${m.ca_count}/${m.player_count}`:'Não disponível'],['PA médio †',m.pa_mean==null?'—':num(Math.round(m.pa_mean*10)/10)],['PA lidos',m.player_count?`${m.pa_count}/${m.player_count}`:'Não disponível'],['Idade média',m.age_mean==null?'—':num(Math.round(m.age_mean*10)/10)]])}`).join('')+`<button id="show-club-players">Ver jogadores deste clube</button><p class="fine">Equipe principal usa o vínculo de equipe decodificado (slot 0). Jogadores sem vínculo ou valor disponível não entram nas médias.</p>`;
  } else if (profileTab === 'history') {
    content = '<p class="fine">Histórico registrado a partir dos saves que você abrir neste mesmo caminho. Não reconstrói o passado anterior à primeira leitura.</p>';
    content += `<table class="history-table"><thead><tr><th>Data no jogo</th><th>CA †</th><th>PA †</th><th>Soma (36)</th></tr></thead><tbody>${history.map(h => `<tr><td>${fmtDate(h.date)}</td><td>${num(h.ca)}</td><td>${num(h.pa)}</td><td>${num(h.attribute_sum)}</td></tr>`).join('')}</tbody></table>`;
  }
  const metricItems=kind==='clubs'?[['Reputação',r.reputation],['CA médio',r.ca_mean],['PA médio',r.pa_mean],['Idade',r.age_mean]]:[['CA',r.ca],['PA',r.pa],['Soma',r.attribute_sum],...(player?[['Nota',r.rating]]:[])];
  const primaryKeys=kind==='players'?['attributes','roles','transfer','hidden']:kind==='clubs'?['attributes','squad','finance']:['attributes','transfer','hidden'];
  const tabButtons=keys=>keys.map(key=>`<button data-profile-tab="${key}" class="${key===profileTab?'active':''}" aria-pressed="${key===profileTab}">${tabs[key]}</button>`).join('');
  const clubName=kind==='clubs'?r.short_name||r.name:r.club_short_name||r.club_name||'Sem vínculo decodificado';
  const watchButton=kind!=='clubs'?`<button id="profile-watch" class="${shortlisted?'listed':''}" title="${shortlisted?'Remover da lista':'Adicionar à lista'}" aria-label="${shortlisted?'Remover da lista':'Adicionar à lista'}">${icon('star')}</button>`:'';
  $('profile').innerHTML = `<div class="profile-heading"><div class="profile-topline">${badge(clubName,r)}<span title="${esc(clubName)}">${esc(clubName)}${kind!=='clubs'&&r.league_name?' · '+esc(r.league_name):''}</span>${watchButton}<button id="close-profile" title="Fechar (Esc)" aria-label="Fechar perfil">${icon('close')}</button></div><div class="profile-name"><h2>${esc(profileName(r)||`Registro ${r.uid}`)}</h2><button id="copy-name" title="Copiar nome" aria-label="Copiar nome" ${profileName(r)?'':'disabled'}>${icon('copy')}</button></div><div>${player?positionChips(r.natural_positions||[]):staff?`<span class="position-chip">${esc(r.staff_role)}</span>`:''}</div>${kind!=='clubs'?`<p>${num(r.age)} anos${staff?' · '+esc(r.staff_area):''}</p>`:''}${nationalityHeader(r)}${kind!=='clubs'?`<div class="profile-actions"><button id="profile-select">${selection.has(r.uid)?'Desmarcar':'Selecionar'}</button></div>`:''}</div>
  <div class="profile-metrics"><div class="metric-grid">${metricItems.map(([label,value])=>`<div class="metric ${label.startsWith('PA')?'pa':''}"><label>${label}</label><strong>${value==null?'—':num(Number(Number(value).toFixed(1)))}</strong></div>`).join('')}</div>${kind!=='clubs'?abilityBar(r):''}${player?`<div class="metrics-caption"><span>${compactMoney(r.model_value)} · ${compactMoney(r.wage,true)}</span><span>${r.ability_difference>0?'+'+r.ability_difference+' até o potencial':''}</span></div>`:''}</div>
  <div class="profile-tabs">${tabButtons(primaryKeys)}</div><div class="profile-content">${content}</div><details class="profile-extras" ${!primaryKeys.includes(profileTab)?'open':''}><summary>Mais informações</summary><div class="profile-tabs">${tabButtons(Object.keys(tabs).filter(key=>!primaryKeys.includes(key)))}</div><p class="fine">† CA/PA, altura, salário, habilidades profissionais, cargos e liga: leitura experimental. Conferências pontuais documentadas; nem todos os registros foram validados.</p></details>`;
  applyDataStyles($('profile'));
  document.body.classList.add('has-profile');$('profile').inert=false;
  updateSelection();
}
function attributeLabel(key) {
  return Object.values(groups).map(group=>group[key]).find(Boolean) || key;
}
function selectLoaded(checked) {
  if(loading||shortlistBusy||!meta||kind==='clubs')return;
  rows.forEach(row=>{if(checked)selection.add(row.uid);else selection.delete(row.uid);});
  updateSelection();
}
function toggleSelection(uid) {
  if(loading||shortlistBusy||kind==='clubs')return;
  if(selection.has(uid))selection.delete(uid);else selection.add(uid);
  updateSelection();
}
async function comparePlayers() {
  if(selection.size!==2||loading||shortlistBusy||kind==='clubs')return;
  const data = await Promise.all([...selection].map(uid=>api(`profile?kind=${kind}&uid=${uid}`)));
  const [a,b] = data.map(d=>d.row);
  const line = (label,av,bv,inverse=false,highlight=true) => {
    const comparable = highlight && typeof av === 'number' && typeof bv === 'number';
    const aw=comparable&&(inverse?av<bv:av>bv),bw=comparable&&(inverse?bv<av:bv>av),max=label.startsWith('Soma')?(kind==='players'?720:staffScoring.length*20):label.startsWith('CA')||label.startsWith('PA')?200:label==='Idade'?100:20;
    return `<tr><td>${esc(label)}</td><td class="comparison-numbers ${aw?'better':''}">${esc(av ?? '—')}</td><td><div class="comparison-bars" aria-hidden="true"><span><i class="${aw?'winner':''}" data-width="${typeof av==='number'?av/max*100:0}"></i></span><span><i class="${bw?'winner':''}" data-width="${typeof bv==='number'?bv/max*100:0}"></i></span></div></td><td class="comparison-numbers ${bw?'better':''}">${esc(bv ?? '—')}</td></tr>`;
  };
  const bothKeepers = kind === 'players' && a.positions?.gk >= 15 && b.positions?.gk >= 15;
  const scoreGroups = kind === 'players' ? ['Técnicos','Mentais','Físicos',...(bothKeepers?['Goleiro']:[])] : ['Profissionais'];
  const sumGroups = kind === 'players' ? [...scoreGroups,'Ocultos','Personalidade'] : ['Profissionais','Personalidade'];
  const wins=[0,0];let ties=0,missing=0;
  for(const group of scoreGroups)for(const key of Object.keys(groups[group])) {
    if(group==='Profissionais'&&!staffScoring.includes(key))continue;
    const av=(group==='Personalidade'?a.personality:group==='Profissionais'?a.professional_attributes:a.attributes)?.[key],bv=(group==='Personalidade'?b.personality:group==='Profissionais'?b.professional_attributes:b.attributes)?.[key];
    if(typeof av!=='number'||typeof bv!=='number'){missing++;continue;}
    if(av===bv)ties++;else wins[(key==='controversy'?av<bv:av>bv)?0:1]++;
  }
  const score = [a,b].map((player,i)=>`<div class="${wins[i]>wins[1-i]?'better':''}"><strong>${esc(player.name)}</strong><span>${num(wins[i])} atributos vencidos</span>${wins[i]>wins[1-i]?'<b>Venceu por atributos</b>':''}</div>`).join('');
  const summary=`<div class="comparison-score">${score}</div><p class="fine comparison-score-note">${wins[0]===wins[1]?'Empate no placar · ':''}${num(ties)} atributos empatados${missing?` · ${num(missing)} sem dados comparáveis`:''}. ${kind==='players'?`Contagem dos ${bothKeepers?47:36} atributos técnicos, mentais e físicos${bothKeepers?', incluindo goleiro':''}, com o mesmo peso.`:`Contagem dos ${staffScoring.length} atributos profissionais ativos, com o mesmo peso. Campos legados ficam fora do placar e sem destaque. Leitura experimental.`}</p>`;
  $('compare-title').textContent = kind === 'staff' ? 'Comparar staff' : 'Comparar jogadores';
  $('comparison').innerHTML = `${summary}<table><colgroup><col><col style-placeholder="value"><col><col style-placeholder="value"></colgroup><thead><tr><th>Critério</th><th>${esc(a.name)}</th><th aria-label="Barras de comparação"></th><th>${esc(b.name)}</th></tr></thead><tbody>${line('Idade',a.age,b.age,false,false)}${line('CA †',a.ca,b.ca)}${line('PA †',a.pa,b.pa)}${line(kind==='players'?'Soma (36)':`Soma profissional (${staffScoring.length}) †`,a.attribute_sum,b.attribute_sum)}${sumGroups.map(group => `<tr class="group-row"><td colspan="4">${esc(group)}</td></tr>${Object.entries(groups[group]).map(([key,label])=>line(label,(group==='Personalidade'?a.personality:group==='Profissionais'?a.professional_attributes:a.attributes)?.[key],(group==='Personalidade'?b.personality:group==='Profissionais'?b.professional_attributes:b.attributes)?.[key],['injury_proneness','dirtiness','controversy'].includes(key),group!=='Profissionais'||staffScoring.includes(key))).join('')}`).join('')}</tbody></table><p class="fine">Verde destaca o maior valor; em propensão a lesões, jogo sujo e controvérsia, destaca o menor. Isso não determina sozinho o melhor jogador.</p>`;
  applyDataStyles($('comparison'));
  $('compare-dialog').showModal();
}
function renderConditions() {
  $('conditions').innerHTML = Object.entries(conditions).map(([key,value])=>`<button data-remove-condition="${key}" aria-label="Remover condição ${esc(attributeLabel(key.split('_').slice(1).join('_')))}">${esc(attributeLabel(key.split('_').slice(1).join('_')))} ${key.startsWith('maxattr_')?'≤':'≥'} ${esc(value)} ×</button>`).join('');
  document.querySelectorAll('[data-condition]').forEach(input=>input.value=conditions[input.dataset.condition]||'');
}
function resetFilters() {
  for (const id of fieldIds) { if (!$(id)) continue; if ($(id).type === 'checkbox') $(id).checked = false; else $(id).value = id==='squad_scope'?'first':id==='squad'?'all':''; }
  conditions = {}; renderConditions();
  document.querySelectorAll('[data-trait]').forEach(c=>c.checked=false);
  syncMirrors(); updatePitch();
  syncPickers();
}
function renderAvailability() {
  $('opportunities').hidden = kind !== 'players';
  const selected = $('availability').value;
  for (const button of document.querySelectorAll('[data-availability]')) {
    button.setAttribute('aria-pressed', String(button.dataset.availability === selected));
    const missing = ['transfer_listed','loan_listed'].includes(button.dataset.availability) && !meta?.listing_status_count;
    button.disabled = missing;
    button.title = missing ? 'Esta lista ainda não está disponível para o save.' : '';
  }
  $('availability-note').textContent = selected.startsWith('expiring_')
    ? `Prazo contado a partir de ${fmtDate(meta?.date)}, data da carreira. Contratos já expirados ficam fora.`
    : selected === 'free' ? 'Somente jogadores cuja leitura indica ausência de vínculo. Registros incompletos ficam fora.'
    : ['transfer_listed','loan_listed'].includes(selected) ? 'Listagem experimental: somente estados conferidos no FM. Estados não identificados ficam fora.'
    : !meta?.listing_status_count ? 'Listas de transferências e empréstimos ainda indisponíveis nesta leitura.' : '';
}
async function options() {
  const requestedKind=kind;
  const data = await api(`options?kind=${kind}`);
  if(kind!==requestedKind)return;
  setupPicker('club',data.clubs.filter(c=>c.name).map(c=>({value:String(c.uid),label:c.name})));
  setupPicker('nation',data.nations.map(n=>({value:String(n.id),label:n.name})));
  setupPicker('league',data.competitions.map(c=>({value:c.key,label:c.name})));
  setupPicker('staff_role',Object.entries(data.staff_roles||{}).map(([value,label])=>({value,label})));
  $('league-note').textContent=`Cobertura parcial: ${num(meta?.league_clubs_count||0)} clubes com liga nacional nomeada pela tabela do save. Liga não lida não significa clube sem divisão.`;
  setupPicker('staff_area',Object.entries(data.staff_areas||{}).map(([value,label])=>({value,label})));
  setupPicker('based',data.based.map(n=>({value:String(n.id),label:n.name})));
  for(const id of ['nation_region','based_region'])setupPicker(id,Object.entries(data.regions).map(([value,label])=>({value,label})));
  buildSearchTabs();
  optionsKind=kind;
}
async function changeView(next) {
  const version=++viewVersion;++requestVersion;
  const oldKind = kind;
  view = next; kind = next === 'staff' ? 'staff' : next === 'clubs' ? 'clubs' : 'players';
  closeProfile();
  selection.clear();resetFilters();updateSelection();
  if (oldKind !== kind) { sort = kind === 'clubs' ? 'reputation' : 'pa';profileTab='attributes'; }
  document.querySelectorAll('[data-view]').forEach(button=>button.toggleAttribute('aria-current',button.dataset.view===view));
  document.querySelector('[data-view="'+view+'"]').setAttribute('aria-current','page');
  $('list-title').textContent = view === 'squad' && meta?.managed?.length ? meta.managed[0].club_short_name || meta.managed[0].club_name : titles[view];
  $('search').placeholder = kind === 'players' ? 'Buscar jogador, clube ou país' : kind === 'staff' ? 'Buscar staff ou clube' : 'Buscar clube ou liga';
  for (const id of ['position','sum_min','rating_min']) $(id).disabled = kind !== 'players';
  for (const id of ['age_min','age_max','ca_min','pa_min','contract_before','free']) $(id).disabled = kind === 'clubs';
  $('club').disabled = view === 'squad';
  $('availability').disabled = kind !== 'players';
  $('nation_region').disabled=kind==='clubs';
  $('eu_national').disabled=kind==='clubs';
  $('staff-area-filter').hidden=kind!=='staff';$('staff_area').disabled=kind!=='staff';$('staff_role').disabled=kind!=='staff';
  $('squad-scope-label').hidden=kind!=='clubs';$('squad_scope').disabled=kind!=='clubs';
  $('player-squad-label').hidden=kind!=='players';$('squad').disabled=kind!=='players';
  for (const id of fieldIds) {
    if (!$(id)) continue;
    if (id.startsWith('rep_') || id.startsWith('ability_difference') || id.startsWith('ca_') || id.startsWith('pa_')) $(id).disabled = kind === 'clubs';
    if (id.startsWith('rep_')) $(id).disabled = kind !== 'players';
    if (id.startsWith('sum_')) $(id).disabled=kind==='clubs';
    if (id.startsWith('rating_') || id.startsWith('height_cm_')) $(id).disabled=kind!=='players';
    if (id.startsWith('model_') || id.startsWith('value_') || id.startsWith('release_fee_') || ['traits','squad_status','contract_kind','release_kind','has_release'].includes(id)) $(id).disabled = kind !== 'players';
    if(['based','no_contract'].includes(id))$(id).disabled=kind==='clubs';
    if (['balance_','transfer_budget_remaining_','wage_budget_weekly_','reputation_','stadium_seated_capacity_','stadium_expansion_capacity_'].some(prefix=>id.startsWith(prefix))) $(id).disabled = kind !== 'clubs';
    if(['wage_min','wage_max','free','contract_after','contract_before','within_shortlist'].includes(id)) $(id).disabled=kind==='clubs';
  }
  $('pitch-panel').hidden = kind !== 'players'; $('search-title').textContent = kind==='players'?'Pesquisa de jogadores':kind==='staff'?'Pesquisa de staff':'Pesquisa de clubes';
  rangeMax.sum=kind==='staff'?staffScoring.length*20:720;
  $('sum_min').placeholder=kind==='staff'?`${staffScoring.length}–${staffScoring.length*20}`:'36–720';
  $('general-fields').querySelector('[data-range="sum"] legend').textContent=kind==='staff'?`Soma profissional (${staffScoring.length}) †`:'Soma dos atributos (36)';
  for(const input of document.querySelectorAll('#sum_min,#sum_max,[data-mirror="sum_min"],[data-mirror="sum_max"]'))input.max=rangeMax.sum;
  syncMirrors(); updatePitch();syncPickers();
  document.querySelectorAll('[data-range]').forEach(field=>field.hidden=[...field.querySelectorAll('input')].every(input=>input.disabled));
  $('table-note').textContent = kind === 'players' ? 'Soma: 36 atributos de linha. † CA/PA: sem confirmação independente. Nota: estimativa Matt Scout.' : kind === 'staff' ? `Soma: ${staffScoring.length} atributos profissionais ativos; campos legados ficam fora. Cargos pelo contrato atual; treinador principal/diretor também por assento. Vínculos incompletos permanecem sem cargo identificado.` : `${num(meta?.hidden_female_clubs||0)} clubes femininos identificados ocultos. Categoria desconhecida permanece visível. Médias usam jogadores lidos; † CA/PA e vínculos experimentais.`;
  renderShell();
  if (meta) {
    $('result-count').textContent='Atualizando…';
    $('table').querySelector('tbody').innerHTML='<tr><td class="empty-row" colspan="20">Atualizando resultados…</td></tr>';
    if(optionsKind!==kind)await options();
    if(version!==viewVersion)return;
    await refreshRows(true);
  }
}
function saveButtons(container) {
  container.innerHTML = saves.length ? saves.map((save,i)=>`<button class="save-option" data-save="${i}"><span><strong>${esc(save.name)}</strong><small>${(save.size/1048576).toFixed(1)} MB · .fm</small></span><span>Abrir</span></button>`).join('') : '<p>Nenhum save encontrado na pasta padrão. Clique em Abrir save para selecionar outro arquivo.</p>';
}
function lockLoading(value) {
  loading = value;
  if(value)closeProfile();
  $('loading-view').hidden=!value;
  if(value){$('welcome').hidden=true;$('workspace').hidden=true;}
  renderShell();
  document.querySelectorAll('[data-view],#filters input,#filters select,#filters button,#advanced input,#advanced select,#advanced button,#next,#page-size,#table button,#table input').forEach(control=>control.disabled=control.closest('.unavailable')?true:value);
  $('open').disabled = value; $('reload').disabled = value || !meta;
  $('salary-settings').disabled=value||!meta;
  $('workspace').setAttribute('aria-busy',String(value));
  if (value) { $('compare').disabled = true; $('export').disabled = true; }
  else $('remove-preset').disabled=!$('preset').value;
  updateSelection();
}
window.loadSave = action(async path => {
  if (loading) return;
  for (const dialog of document.querySelectorAll('dialog[open]')) dialog.close();
  await api('load',{path}); lockLoading(true);$('loading-file').textContent=String(path).split('/').pop(); notice('Preparando leitura do save…');
  poll();
});
async function poll() {
  clearTimeout(polling);
  try {
    const data = await api('status');
    if (data.loading) { $('loading-step').textContent=data.progress;$('message').hidden=true; $('footer-state').textContent = 'Lendo cópia do save…'; polling = setTimeout(poll,600); return; }
    lockLoading(false);
    if (data.error) { notice(data.error,true);$('welcome').hidden=!!meta;$('workspace').hidden=!meta;if (meta) await changeView(view); return; }
    meta = data.meta; $('shortlist-count').textContent=meta?num(data.shortlist_count):''; $('reload').disabled=!meta;optionsKind=null;currentProfile = null; selection.clear(); updateSelection();
    if (meta) {
      const managed=meta.managed?.[0];if(managed?.club_uid!=null)managed.player_count=(await api(`rows?kind=players&club=${managed.club_uid}&limit=1&columns=name`)).total;
      salaryPrefs=await api('salaries');updateSalaryLabels();$('salary-settings').disabled=false;
      $('save-name').textContent = meta.file;
      $('save-date').textContent = `${fmtDate(meta.date)} · FM ${meta.build}`;
      $('welcome').hidden = true; $('workspace').hidden = false; $('filters').hidden = false;
      $('footer-state').textContent = `${num(meta.counts.players)} jogadores · ${num(meta.counts.staff)} staff · Somente leitura`;
      notice(meta.warnings.length ? meta.warnings.join(' · ') : '');
      resetFilters(); await changeView('players');
    }
  } catch (error) { lockLoading(false); notice(error.message,true); }
}
async function refreshPresets() {
  const old = $('preset').value;
  const data = await api('presets'); presets = data.presets;
  $('preset').innerHTML = '<option value="">Selecione um filtro salvo</option>' + presets.map(p=>`<option value="${esc(p.id)}">${esc(p.name)} · ${titles[p.kind]}</option>`).join('');
  $('preset').value = old; $('remove-preset').disabled = !$('preset').value;
  $('saved-searches').innerHTML=presets.map(p=>`<button data-saved-search="${esc(p.id)}">${icon('search')}<span>${esc(p.name)}</span></button>`).join('')+[['young','Promessas ≤ 21'],['contract','Contrato ≤ 12 meses'],['defender','Zagueiros com UE']].map(([id,label])=>`<button data-builtin-search="${id}">${icon('search')}<span>${label}</span></button>`).join('');
}
function syncMirrors() { renderAvailability(); document.querySelectorAll('[data-mirror]').forEach(input=>{input.value=$(input.dataset.mirror).value;input.disabled=$(input.dataset.mirror).disabled;}); }
function updatePitch() {
  const selected=new Set($('position').value.split(',').filter(Boolean));
  document.querySelectorAll('[data-pitch]').forEach(button=>button.setAttribute('aria-pressed',String(selected.has(button.dataset.pitch))));
  $('pitch-selection').textContent = selected.size ? `Posições: ${[...selected].map(p=>positionNames[p]).join(', ')} · qualquer uma` : 'Todas as posições';
  $('quick-position').textContent=selected.size===0?'Todas as posições':selected.size===1?positionNames[[...selected][0]]:`${selected.size} posições`;
}
function setupPicker(id, options) {
  let input=$(id);
  if(input.tagName==='SELECT') {
    const replacement=document.createElement('input');replacement.type='hidden';replacement.id=id;replacement.value=input.value;replacement.disabled=input.disabled;input.replaceWith(replacement);input=replacement;
  }
  let button=input.parentElement.querySelector('[data-picker-open]');
  if(!button){button=document.createElement('button');button.type='button';button.dataset.pickerOpen=id;button.className='picker-button';button.setAttribute('aria-haspopup','dialog');button.setAttribute('aria-label',`Selecionar ${pickerNames[id]}`);input.after(button);}
  pickers[id]={input,button,options:options.sort((a,b)=>a.label.localeCompare(b.label,'pt-BR',{numeric:true}))};syncPickers();
}
function syncPickers() {
  for(const [id,picker]of Object.entries(pickers)) {
    const selected=picker.input.value.split(',').filter(Boolean);
    picker.button.textContent=selected.length===0?picker.options.length?`Todos · ${pickerNames[id]}`:id==='league'?'Liga do clube ainda não identificada':'Nomes ainda indisponíveis':selected.length===1?picker.options.find(o=>o.value===selected[0])?.label||'Opção salva indisponível':`${selected.length} opções selecionadas`;
    if(['nation','based'].includes(id)&&selected.length)picker.button.innerHTML=`<span class="fm-country-chips">${selected.map(value=>{const label=picker.options.find(o=>o.value===value)?.label||'Opção salva indisponível';return `<span class="fm-country-chip">${countryFlag(label,'token')}${esc(label)}</span>`;}).join('')}</span>`;
    picker.button.title=selected.map(v=>picker.options.find(o=>o.value===v)?.label||'Opção salva indisponível').join(' · ');
    picker.button.disabled=picker.input.disabled||!picker.options.length;
  }
}
function renderPickerOptions() {
  if(!activePicker)return;
  const picker=pickers[activePicker],search=$('picker-search').value.normalize('NFD').replace(/\p{Diacritic}/gu,'').toLocaleLowerCase('pt-BR');
  const selected=new Set(picker.input.value.split(',').filter(Boolean));
  const choices=picker.options.filter(o=>o.label.normalize('NFD').replace(/\p{Diacritic}/gu,'').toLocaleLowerCase('pt-BR').includes(search));
  const visible=choices.slice(0,120);
  $('picker-options').innerHTML=visible.length?visible.map(o=>`<label class="picker-option"><input type="checkbox" data-picker-value="${esc(o.value)}" ${selected.has(o.value)?'checked':''}>${['nation','based'].includes(activePicker)?countryFlag(o.label,'picker'):''}<span>${esc(o.label)}</span></label>`).join(''):'<p class="fine">Nenhuma opção corresponde à busca.</p>';
  $('picker-count').textContent=`${visible.length} de ${choices.length} opções${choices.length>120?' · refine a busca':''}`;
  updatePickerSummary();
}
function updatePickerSummary() {
  const picker=pickers[activePicker],selected=picker.input.value.split(',').filter(Boolean);
  $('picker-selected').textContent=selected.length?`${selected.length} selecionadas: ${selected.slice(0,5).map(v=>picker.options.find(o=>o.value===v)?.label||'Opção salva indisponível').join(' · ')}${selected.length>5?'…':''}`:'Nenhuma restrição. Selecione uma ou mais opções.';
}
function rangeFields(key) {
  const inputs = ['min','max'].map(bound=> {
    const id = `${key}_${bound}`, exists = !!$(id), actualId = exists ? `mirror-${id}` : id;
    if (!exists && !fieldIds.includes(id)) fieldIds.push(id);
    return `<label>${bound==='min'?'Mín.':'Máx.'}<input type="number" id="${actualId}" ${exists?`data-mirror="${id}"`:''} min="${['balance','ability_difference'].includes(key)?-rangeMax[key]:0}" max="${rangeMax[key]}" placeholder="${bound==='min'?'0':num(rangeMax[key])}"></label>`;
  }).join('');
  return `<fieldset class="range-field" data-range="${key}"><legend>${esc(rangeLabels[key])}</legend>${inputs}</fieldset>`;
}
function unavailable(label, reason) { return `<label class="unavailable">${esc(label)}<input disabled placeholder="${esc(reason)}"><small>${esc(reason)}</small></label>`; }
function buildSearch() {
  for(const id of ['staff_area','staff_role'])if(!fieldIds.includes(id))fieldIds.push(id);
  $('general-fields').innerHTML = `<label>Nome / clube<input data-mirror="search" type="search"></label><div class="range-grid">${['age','height_cm','ca','pa','ability_difference','sum','rating'].map(rangeFields).join('')}</div><div class="location-grid"><label>Clube<select id="club"><option value="">Todos os clubes</option></select></label><label>Nacionalidade · qualquer cidadania<select id="nation"><option value="">Todas</option></select></label><label>Liga do clube<select id="league"><option value="">Todas</option></select></label><label>País onde atua<select id="based"><option value="">Qualquer país</option></select></label><label>Região da nacionalidade<input id="nation_region" type="hidden"></label><label>Região onde atua<input id="based_region" type="hidden"></label><label>Possui nacionalidade da União Europeia<select id="eu_national"><option value="">Qualquer</option><option value="yes">Sim · alguma cidadania é da UE</option><option value="no">Não · nenhuma cidadania lida é da UE</option></select></label></div><p id="league-note" class="fine"></p><p class="fine">Nacionalidade, região da nacionalidade e UE consideram todas as cidadanias lidas. O filtro UE usa os 27 países membros atuais; não calcula regras específicas de inscrição de cada liga.</p><label class="checkbox-label"><input id="within_shortlist" type="checkbox">Somente na minha lista</label><div class="range-grid">${['rep_home','rep_current','rep_world','club_reputation','reputation','balance','transfer_budget_remaining','wage_budget_weekly','stadium_seated_capacity','stadium_expansion_capacity'].map(rangeFields).join('')}</div><details class="pending-fields"><summary>Filtros ainda sem dados confiáveis</summary><div class="location-grid">${[['Jogador gerado (regen)','Identificação não decodificada'],['Partidas pela seleção','Não decodificadas'],['Gols pela seleção','Não decodificados'],['Avaliação potencial','Projeção ainda não implementada'],['Reputação do elenco','Sem campo confirmado'],['Gênero','Não decodificado']].map(([l,r])=>unavailable(l,r)).join('')}</div></details>`;
  $('contract-fields').innerHTML = `<div class="location-grid"><label>Oportunidade<select data-mirror="availability"><option value="">Qualquer</option><option value="free">Sem contrato</option><option value="expiring_6">Expira em até 6 meses</option><option value="expiring_12">Expira em até 12 meses</option><option value="transfer_listed">Lista de transferências</option><option value="loan_listed">Lista de empréstimos</option></select></label><label>Contrato expira a partir de<input id="contract_after" type="date"></label><label>Contrato expira até<input id="contract_before" type="date"></label><label>Tipo de contrato<select id="contract_kind"><option value="">Qualquer</option><option value="1">Tempo integral</option><option value="3">Jovem</option><option value="2">Código 2 · sem nome confirmado</option></select></label><label>Status no elenco<select id="squad_status"><option value="">Qualquer</option>${[[1,'Estrela'],[2,'Jogador importante'],[3,'Titular habitual'],[4,'Jogador de elenco'],[5,'Reserva de impacto'],[7,'Pouco utilizado'],[9,'Reserva de emergência'],[10,'Promessa em ascensão'],[11,'Promessa futura'],[13,'Jovem'],[14,'Titular da equipe B'],[15,'Goleiro titular'],[16,'Goleiro de copas'],[17,'Goleiro de copas nacionais'],[18,'Goleiro de copas continentais'],[20,'Reserva'],[21,'Goleiro reserva de emergência'],[22,'Excedente']].map(([id,label])=>`<option value="${id}">${label}</option>`).join('')}</select></label><label>Cláusula de liberação<select id="release_kind"><option value="">Qualquer</option>${[['minimum_fee_release','Mínima geral'],['minimum_fee_release_foreign','Clubes estrangeiros'],['minimum_fee_release_domestic','Clubes nacionais'],['minimum_fee_release_domestic_higher_division','Divisão nacional superior'],['relegation_release','Por rebaixamento'],['non_promotion_release','Por não promoção']].map(([id,label])=>`<option value="${id}">${label}</option>`).join('')}</select></label></div><div class="check-grid"><input id="free" type="checkbox" hidden><label class="checkbox-label"><input id="no_contract" type="checkbox">Sem contrato (jogador livre)</label><label class="checkbox-label"><input id="has_release" type="checkbox">Com cláusula de rescisão (inclui condicionais)</label></div><div class="range-grid">${['value','model_value','model_fee','wage','release_fee'].map(rangeFields).join('')}</div><p class="fine">Cláusulas e valor de mercado usam a moeda selecionada em Moeda / salários; os limites são convertidos para a busca no save. Ausência de contrato lido pode ser falta de cobertura do leitor. As colunas Rescisão geral, nacional e internacional mostram condições separadas. Nacional significa clubes do mesmo país do clube atual; internacional, clubes estrangeiros. Cláusulas por rebaixamento e outras condições ficam separadas no perfil. Selecione um tipo de cláusula para filtrar o valor correspondente. Sem uma conversão conferida, os valores ficam identificados como unidades do save.</p><details class="pending-fields"><summary>Filtros ainda sem dados confiáveis</summary><div class="location-grid">${[['Disponível pela regra Bosman','Elegibilidade não calculada'],['Disponibilidade para transferência','Não decodificada'],['Preço efetivamente aceito','Depende da negociação no FM']].map(([l,r])=>unavailable(l,r)).join('')}</div></details>`;
  for(const id of ['based','nation_region','based_region','eu_national','within_shortlist','contract_after','no_contract','contract_kind','squad_status','release_kind','has_release','traits']) if(!fieldIds.includes(id)) fieldIds.push(id);
  const coords=positionXY;
  for(const [position,[x,y]] of Object.entries(coords)) {
    const button=document.createElement('button'); button.textContent=position;button.dataset.pitch=position;button.setAttribute('aria-label',`Filtrar posição ${position}`);button.setAttribute('aria-pressed','false');
    button.style.left=`${x}%`;button.style.top=`${y}%`; $('pitch').append(button);
  }
  buildSearchTabs(); syncMirrors();
  $('pitch').insertAdjacentHTML('afterbegin','<div class="pitch-circle" aria-hidden="true"></div>');
  for(const id of ['squad_scope','squad'])$(id).closest('label').parentElement===$('filters')&&$('general-fields').append($(id).closest('label'));
  $('general-fields').insertAdjacentHTML('beforeend','<div id="staff-area-filter" hidden><div class="location-grid"><label>Cargo do staff †<input id="staff_role" type="hidden" disabled></label><label>Área do staff<input id="staff_area" type="hidden" disabled></label></div><p class="fine">Cargos por assento e contrato: treinador principal e diretor de futebol. Os demais ficam não identificados; área continua separada do cargo.</p></div>');
  for(const id of ['contract_kind','squad_status','release_kind'])setupPicker(id,[...$(id).options].filter(o=>o.value && (id!=='contract_kind'||['1','3'].includes(o.value))).map(o=>({value:o.value,label:o.textContent})));
}
function buildSearchTabs() {
  const tabs = {general:'Geral',...(kind!=='clubs'?{contract:'Contrato'}:{}),...(kind==='players'?{'Técnicos':'Técnicos','Mentais':'Mentais','Físicos':'Físicos','Goleiro':'Goleiro','Ocultos':'Ocultos','traits':'Movimentos'}:{}),...(kind==='staff'?{'Profissionais':'Profissionais'}:{}),...(kind!=='clubs'?{'Personalidade':'Personalidade'}:{})};
  $('search-tabs').innerHTML=Object.entries(tabs).map(([key,label])=>`<button role="tab" data-filter-tab="${key}" aria-selected="${key===searchTab}">${label}</button>`).join('');
  if(!(searchTab in tabs))searchTab='general'; showSearchTab(searchTab);
}
function showSearchTab(tab) {
  searchTab=tab;
  for(const id of ['general','contract','attributes','traits'])$(`filter-${id}`).hidden = id !== (tab==='general'||tab==='contract'||tab==='traits'?tab:'attributes');
  document.querySelectorAll('[data-filter-tab]').forEach(button=>button.setAttribute('aria-selected',String(button.dataset.filterTab===tab)));
  if(groups[tab]) $('attribute-grid').innerHTML = Object.entries(groups[tab]).sort((a,b)=>a[1].localeCompare(b[1],'pt-BR')).map(([key,label])=>`<div class="attribute-filter-row"><span title="${esc(label)}">${esc(label)}</span><div class="attribute-segments" role="group" aria-label="${esc(label)} mínimo">${Array.from({length:20},(_,i)=>`<button data-attribute-min="${key}" data-min-value="${i+1}" title="${esc(label)} ≥ ${i+1}" aria-label="${esc(label)} mínimo ${i+1}" aria-pressed="${Number(conditions['attr_'+key])===i+1}" ${i<Number(conditions['attr_'+key])?`data-heat="${i+1}"`:''}></button>`).join('')}</div><input type="number" min="1" max="20" placeholder="Mín." data-condition="attr_${key}" aria-label="${esc(label)} mínimo" value="${esc(conditions[`attr_${key}`]||'')}"><input type="number" min="1" max="20" placeholder="Máx." data-condition="maxattr_${key}" aria-label="${esc(label)} máximo" value="${esc(conditions[`maxattr_${key}`]||'')}"></div>`).join('');
  applyDataStyles($('attribute-grid'));
}
function downloadFile(filename,contents,mime) {
  if (window.webkit?.messageHandlers?.saveFile) {
    window.webkit.messageHandlers.saveFile.postMessage({filename,contents}); return;
  }
  const url = URL.createObjectURL(new Blob([contents],{type:mime}));
  const link = document.createElement('a'); link.href = url; link.download = filename; link.click();
  setTimeout(()=>URL.revokeObjectURL(url),1000);
}
document.addEventListener('click',action(async event => {
  const button = event.target.closest('button');
  if(!button){const row=event.target.closest('#table tbody tr[data-uid]');if(row&&!event.target.closest('input'))return showProfile(Number(row.dataset.uid));return;}
  if(button.hasAttribute('data-open-filters'))return openFilters();
  if(button.dataset.removeFilter){const key=button.dataset.removeFilter;if(key.startsWith('attr_')||key.startsWith('maxattr_'))delete conditions[key];else if($(key)){if($(key).type==='checkbox')$(key).checked=false;else $(key).value=key==='squad'?'all':key==='squad_scope'?'first':'';}renderConditions();syncMirrors();updatePitch();syncPickers();return refreshRows(true);}
  if(button.hasAttribute('data-entity-segment')){$(kind==='staff'?'staff_area':'based_region').value=button.dataset.entitySegment;syncPickers();return refreshRows();}
  if(button.dataset.savedSearch){$('preset').value=button.dataset.savedSearch;$('apply-preset').click();return;}
  if(button.dataset.builtinSearch){await changeView('players');resetFilters();const key=button.dataset.builtinSearch;if(key==='young'){$('age_max').value='21';$('pa_min').value='170';}else if(key==='contract')$('availability').value='expiring_12';else{$('position').value='DC';$('eu_national').value='yes';}syncMirrors();updatePitch();return refreshRows();}
  if(button.dataset.attributeMin){const key='attr_'+button.dataset.attributeMin;if(conditions[key]===button.dataset.minValue)delete conditions[key];else conditions[key]=button.dataset.minValue;renderConditions();showSearchTab(searchTab);return refreshRows();}
  if(button.dataset.columnPreset){const sets={Ataque:['finishing','dribbling','first_touch','technique','off_the_ball','acceleration','pace'],Criação:['passing','vision','technique','decisions','first_touch','flair','teamwork'],Defesa:['tackling','marking','heading','positioning','anticipation','bravery','strength'],Físico:['acceleration','pace','agility','balance','jumping_reach','stamina','strength'],Limpar:[]};const chosen=sets[button.dataset.columnPreset];document.querySelectorAll('[data-column^="attr_"]').forEach(control=>control.checked=chosen.includes(control.dataset.column.slice(5)));return;}
  if(button.dataset.currency||button.dataset.period){const oldFactors=Object.fromEntries(currencyRanges.map(key=>[key,filterFactor(key)]));salaryPrefs=await api('salaries',{currency:button.dataset.currency||salaryPrefs.currency,period:button.dataset.period||salaryPrefs.period});for(const key of currencyRanges)for(const bound of ['min','max']){const input=$(key+'_'+bound);if(input?.value)input.value=String(Number(input.value)/oldFactors[key]*filterFactor(key));}updateSalaryLabels();syncMirrors();renderTable();renderListStatus();if(currentProfile)renderProfile();return;}
  if (button.dataset.view) return changeView(button.dataset.view);
  if(button.dataset.pickerOpen) {
    const id=button.dataset.pickerOpen;if(pickers[id].input.disabled)return;
    activePicker=id;$('picker-title').textContent=`Selecionar ${pickerNames[id]}`;$('picker-search').value='';renderPickerOptions();$('picker-dialog').showModal();$('picker-search').focus();return;
  }
  if (button.dataset.filterTab) { showSearchTab(button.dataset.filterTab); return; }
  if (button.hasAttribute('data-availability')) {
    $('availability').value = button.dataset.availability;
    $('free').checked = false; $('no_contract').checked = false;
    $('contract_after').value = ''; $('contract_before').value = '';
    syncMirrors(); return refreshRows(true);
  }
  if (button.dataset.pitch) { const chosen=new Set($('position').value.split(',').filter(Boolean));if(chosen.has(button.dataset.pitch))chosen.delete(button.dataset.pitch);else chosen.add(button.dataset.pitch);$('position').value=[...chosen].join(',');updatePitch();syncMirrors();return refreshRows(true); }
  if (button.dataset.sort) { direction = sort === button.dataset.sort && direction === 'desc' ? 'asc' : 'desc'; sort = button.dataset.sort; return refreshRows(true); }
  if (button.dataset.profile) return showProfile(Number(button.dataset.profile));
  if (button.dataset.profileTab) { profileTab = button.dataset.profileTab; renderProfile(); return; }
  if (button.dataset.save) return window.loadSave(saves[Number(button.dataset.save)].path);
  if (button.dataset.close) { $(button.dataset.close).close(); return; }
  if (button.dataset.removeCondition) { delete conditions[button.dataset.removeCondition]; renderConditions(); return refreshRows(true); }
  switch (button.id) {
    case 'sidebar-toggle': {const collapsed=document.body.classList.toggle('sidebar-collapsed');$('sidebar').inert=collapsed;button.setAttribute('aria-expanded',String(!collapsed));button.title=`${collapsed?'Mostrar':'Ocultar'} barra lateral (⌃⌘S)`;button.setAttribute('aria-label',`${collapsed?'Mostrar':'Ocultar'} barra lateral`);return;}
    case 'save-card':renderSaveMenu();$('save-menu').showModal();button.setAttribute('aria-expanded','true');return;
    case 'open-other':$('save-menu').close();$('open').click();return;
    case 'close-save':$('save-menu').close();closeProfile();meta=null;rows=[];selection.clear();$('welcome').hidden=false;$('workspace').hidden=true;$('toolbar-actions').hidden=true;$('save-name').textContent='Nenhum save aberto';$('list-title').textContent='FM Matt Scout 26';$('result-count').textContent='Nenhum save aberto';$('reload').disabled=true;$('salary-settings').disabled=true;renderShell();return;
    case 'close-profile':closeProfile();return;
    case 'copy-name':return copyProfileName();
    case 'undo-list':{const undo=undoList;undoList=null;if(undo&&kind===undo.kind&&meta?.path===undo.career)return changeShortlist(undo.uids,undo.add,false);return;}
    case 'add-filter':return openFilters();
    case 'apply-filters':if(!validateControls())return;filterDraft=null;++draftVersion;$('advanced').close();closeProfile();return refreshRows(true);
    case 'open':
      if (window.webkit?.messageHandlers?.openSave) window.webkit.messageHandlers.openSave.postMessage(null);
      else { saveButtons($('dialog-saves')); $('open-dialog').showModal(); }
      break;
    case 'load-path': return window.loadSave($('save-path').value);
    case 'reload': return window.loadSave(meta.path);
    case 'salary-settings':
      if($('save-menu').open)$('save-menu').close();
      salaryReference=kind!=='clubs'&&currentProfile?{kind,uid:currentProfile.row.uid,name:currentProfile.row.name}:null;
      $('salary-currency').value=salaryPrefs.currency;$('salary-period').value=salaryPrefs.period;$('salary-amount').value='';$('money-amount').value='';
      const clauses=(currentProfile?.row.contract?.clauses||[]).filter(c=>['minimum_fee_release','minimum_fee_release_foreign','minimum_fee_release_domestic','minimum_fee_release_domestic_higher_division','relegation_release','non_promotion_release'].includes(c.kind)&&c.parameter==null&&c.value>0);
      $('money-kind').innerHTML=[...new Set(clauses.map(c=>c.kind))].map(k=>`<option value="${k}">${esc(clauseNames[k])}</option>`).join('')||'<option value="">Nenhuma rescisão lida neste perfil</option>';
      $('money-kind').disabled=$('money-amount').disabled=!salaryReference||!clauses.length;
      $('salary-amount').disabled=!salaryReference;
      $('salary-reference').textContent=salaryReference?`Profissional selecionado: ${salaryReference.name}`:'Abra o perfil de um jogador ou staff para conferir a conversão.';
      $('salary-status').textContent=salaryPrefs.rate==null?'Conversão ainda não conferida. Os salários continuam identificados como unidades do save por semana.':`Salários em ${salaryUnit()}. Conversão conferida nesta carreira.`;
      $('money-status').textContent=salaryPrefs.money_rate==null?'Conversão de valores monetários ainda não conferida.':salaryPrefs.money_source==='clause'?`Valores em ${moneyUnit()}, conferidos por uma rescisão nesta carreira.`:`Valores em ${moneyUnit()}, usando a referência salarial. Confira uma rescisão para melhorar a precisão.`;
      $('salary-dialog').showModal();break;
    case 'save-salary': {
      const body={currency:$('salary-currency').value,period:$('salary-period').value};
      if($('salary-amount').value){if(!$('salary-amount').reportValidity())return;Object.assign(body,salaryReference,{amount:Number($('salary-amount').value)});}
      if($('money-amount').value){if(!$('money-amount').reportValidity())return;Object.assign(body,salaryReference,{money_amount:Number($('money-amount').value),release_kind:$('money-kind').value});}
      const oldFactors=Object.fromEntries(currencyRanges.map(key=>[key,filterFactor(key)]));salaryPrefs=await api('salaries',body);
      for(const key of currencyRanges)for(const bound of ['min','max']){const input=$(key+'_'+bound);if(input?.value)input.value=String(Number(input.value)/oldFactors[key]*filterFactor(key));}
      updateSalaryLabels();$('salary-dialog').close();if(currentProfile)renderProfile();
      notice(`Preferências salvas. Salários: ${salaryUnit()}. Valores: ${moneyUnit()}. Filtros mantêm os mesmos limites.`);
      renderListStatus();renderTable();return;
    }
    case 'advanced-button':return openFilters();
    case 'quick-position':showSearchTab('general');return openFilters();
    case 'picker-clear':if(activePicker){pickers[activePicker].input.value='';syncPickers();renderPickerOptions();return refreshRows(true);}break;
    case 'clear-search':
    case 'clear': resetFilters(); return refreshRows(true);
    case 'next': return refreshRows(false);
    case 'compare': return comparePlayers();
    case 'list-add': return changeShortlist([...selection],true);
    case 'list-remove': return changeShortlist([...selection],false);
    case 'clear-selection': selection.clear();updateSelection();return;
    case 'columns': {
      renderColumnOptions();
      $('columns-dialog').showModal();$('column-search').focus(); break;
    }
    case 'save-columns': {
      visibleColumns[kind]=[...document.querySelectorAll('[data-column]:checked')].map(c=>c.dataset.column);
      await api('layouts',{...visibleColumns,_widths:columnWidths});$('columns-dialog').close();return refreshRows();
    }
    case 'reset-columns': visibleColumns[kind]=[...baseColumns[kind]];columnWidths[kind]={};await api('layouts',{...visibleColumns,_widths:columnWidths});$('columns-dialog').close();return refreshRows();
    case 'profile-select': toggleSelection(currentProfile.row.uid); break;
    case 'profile-watch': return changeShortlist([currentProfile.row.uid],!currentProfile.shortlisted);
    case 'export': $('list-dialog').showModal();break;
    case 'export-csv': {
      const response = await fetch(`api/export?kind=${kind}`);
      if (!response.ok) throw new Error('Não foi possível exportar a lista.');
      downloadFile('matt-scout-lista.csv',await response.text(),'text/csv'); break;
    }
    case 'export-list-json': downloadFile('matt-scout-lista.json',JSON.stringify(await api(`list-file?kind=${kind}`),null,2),'application/json');break;
    case 'list-import': if(!meta){notice('Abra um save antes de importar uma lista.');return;}$('list-file').click();break;
    case 'show-club-players': {const club=currentProfile.row.uid;await changeView('players');$('club').value=String(club);syncPickers();return refreshRows(true);}
    case 'save-preset': $('preset-dialog').showModal(); $('preset-name').focus(); break;
    case 'confirm-preset': {
      if (!validateControls()) return;
      const saved = await api('presets',{name:$('preset-name').value,kind,filters:values()});
      $('preset-dialog').close(); $('preset-name').value = ''; await refreshPresets(); $('preset').value = saved.id; $('remove-preset').disabled = false;
      notice(`Filtro “${saved.name}” salvo neste Mac. Use Exportar filtros para guardar um arquivo portátil.`); break;
    }
    case 'apply-preset': {
      const preset = presets.find(p=>p.id===$('preset').value);
      if (!preset) { notice('Selecione um filtro salvo.'); return; }
      await changeView(preset.kind); resetFilters();
      for (const [key,value] of Object.entries(preset.filters)) {
        if (key.startsWith('attr_') || key.startsWith('maxattr_')) conditions[key]=value;
        else if (fieldIds.includes(key)) {
          if ($(key).type==='checkbox') $(key).checked=value==='1';
          else {
            if ($(key).tagName==='SELECT' && ![...$(key).options].some(o=>o.value===value)) $(key).add(new Option('Opção salva indisponível',value));
            $(key).value=currencyFilter.test(key)?String(Number(value)*filterFactor(key)):value;
          }
        }
      }
      sort=preset.filters.sort||'pa'; direction=preset.filters.direction||'desc'; renderConditions();syncMirrors();updatePitch();syncPickers(); return refreshRows(true);
    }
    case 'remove-preset': if ($('preset').value) { await api('presets/remove',{id:$('preset').value}); await refreshPresets(); notice('Filtro excluído. Os filtros aplicados continuam na tela.'); } break;
    case 'export-presets': downloadFile('matt-scout-filtros.json',JSON.stringify({version:1,presets},null,2),'application/json'); break;
    case 'import-presets': $('preset-file').click(); break;
  }
}));
document.addEventListener('change',action(async event => {
  if(event.target.dataset.pickerValue&&activePicker){const picker=pickers[activePicker],selected=new Set(picker.input.value.split(',').filter(Boolean));if(event.target.checked)selected.add(event.target.dataset.pickerValue);else selected.delete(event.target.dataset.pickerValue);picker.input.value=[...selected].join(',');syncPickers();updatePickerSummary();return refreshRows(true);}
  if(event.target.id==='list-file') {
    const file=event.target.files[0];if(!file)return;
    try{if(file.size>2097152)throw new Error('A lista deve ter no máximo 2 MB.');const result=await api('list-import',JSON.parse(await file.text()));notice(`${result.matched} registros encontrados; ${result.missing} sem correspondência por ID, nome e nascimento.`);await refreshRows();}finally{event.target.value='';}return;
  }
  if(event.target.dataset.trait){
    const ids=new Set($('traits').value.split(',').filter(Boolean));
    if(event.target.checked)ids.add(event.target.dataset.trait);else ids.delete(event.target.dataset.trait);
    $('traits').value=[...ids].join(',');return refreshRows(true);
  }
  if(event.target.dataset.mirror) { $(event.target.dataset.mirror).value=event.target.value;syncMirrors();return refreshRows(true); }
  if(event.target.dataset.condition) {
    if(!event.target.checkValidity()){event.target.reportValidity();return;}
    if(event.target.value)conditions[event.target.dataset.condition]=event.target.value;else delete conditions[event.target.dataset.condition];
    renderConditions();return refreshRows(true);
  }
  if(event.target.id==='select-all'){selectLoaded(event.target.checked);return;}
  if (event.target.dataset.select) { toggleSelection(Number(event.target.dataset.select)); return; }
  if (event.target.id==='preset') { $('remove-preset').disabled=!event.target.value; return; }
  if (event.target.id==='preset-file') {
    const file=event.target.files[0]; if (!file) return;
    try {
      if (file.size>262144) throw new Error('O arquivo deve ter no máximo 256 KB.');
      const result=await api('presets/import',JSON.parse(await file.text())); await refreshPresets(); notice(`${result.added} filtros importados.`);
    } finally { event.target.value=''; }
    return;
  }
  if(event.target.id==='page-size'){renderListStatus();return;}
  if (fieldIds.includes(event.target.id)){syncMirrors();updatePitch();await refreshRows(true);}
}));
$('table').querySelector('thead').addEventListener('contextmenu',event=>{
  if(!event.target.closest('th')||!meta||loading)return;
  event.preventDefault();$('columns').click();
});
$('search').addEventListener('input',()=>{clearTimeout(debounce);debounce=setTimeout(action(()=>refreshRows(true)),200);});
$('table').addEventListener('pointerdown',event=>{
  const handle=event.target.closest('.column-resize');
  if(!handle||event.button!==0||loading)return;
  event.preventDefault();handle.focus();
  const startX=event.clientX,startWidth=parseFloat(handle.closest('th').style.width);
  handle.setPointerCapture(event.pointerId);handle.classList.add('resizing');
  const move=e=>resizeColumn(handle,startWidth+e.clientX-startX);
  const finish=()=>{handle.removeEventListener('pointermove',move);handle.removeEventListener('pointerup',finish);handle.removeEventListener('pointercancel',finish);handle.classList.remove('resizing');saveColumnWidths();};
  handle.addEventListener('pointermove',move);handle.addEventListener('pointerup',finish);handle.addEventListener('pointercancel',finish);
});
$('table').addEventListener('keydown',event=>{
  const handle=event.target.closest('.column-resize');
  if(!handle)return;
  if(['ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(event.key))event.stopPropagation();
  if(!['ArrowLeft','ArrowRight'].includes(event.key)||loading)return;
  event.preventDefault();resizeColumn(handle,parseFloat(handle.closest('th').style.width)+(event.key==='ArrowRight'?1:-1)*(event.shiftKey?50:10));saveColumnWidths();
});
$('table').addEventListener('dblclick',event=>{
  const handle=event.target.closest('.column-resize');
  if(!handle||loading)return;
  delete columnWidths[kind][handle.closest('th').dataset.columnKey];renderTable();saveColumnWidths();
});
$('picker-search').addEventListener('input',renderPickerOptions);
$('column-search').addEventListener('input',filterColumnOptions);
document.addEventListener('keydown',action(async event=>{
  const key=event.key.toLowerCase();
  if((event.metaKey||event.ctrlKey)&&key==='f'){event.preventDefault();if($('columns-dialog').open)$('column-search').focus();else if(meta)$('search').focus();return;}
  if(event.metaKey&&event.ctrlKey&&key==='s'){event.preventDefault();$('sidebar-toggle').click();return;}
  if(event.metaKey&&key==='r'&&meta){event.preventDefault();if(!loading)window.loadSave(meta.path);return;}
  if(event.key==='Escape'){
    if(document.querySelector('dialog[open]'))return;
    if(currentProfile)closeProfile();else{++profileVersion;selection.clear();updateSelection();}return;
  }
  if(['ArrowUp','ArrowDown'].includes(event.key)&&meta&&!loading&&!document.querySelector('dialog[open]')&&!event.target.closest('input,select,textarea,[contenteditable=true]')){
    const index=rows.findIndex(row=>row.uid===currentProfile?.row.uid),next=Math.max(0,Math.min(rows.length-1,index<0?0:index+(event.key==='ArrowDown'?1:-1)));
    if(rows[next]&&next!==index){event.preventDefault();await showProfile(rows[next].uid);$('table').querySelector(`tr[data-uid="${rows[next].uid}"]`)?.scrollIntoView({block:'nearest'});}
  }
}));
async function init() {
  const data=await api('status'); groups=data.groups;columnGroups=data.column_groups;staffScoring=data.staff_scoring_attributes; roles=data.roles; saves=data.saves;traitLabels=data.traits;buildSearch();saveButtons($('save-list')); await refreshPresets();
  const {_widths={},...layout}=await api('layouts');visibleColumns={...visibleColumns,...layout};columnWidths={...columnWidths,..._widths};
  $('trait-grid').innerHTML=traitLabels.map(t=>`<label class="checkbox-label"><input type="checkbox" data-trait="${t.id}">${esc(t.name)}</label>`).join('');
  document.querySelectorAll('[data-icon]').forEach(node=>node.innerHTML=icon(node.dataset.icon));
  $('filter-bar').prepend($('opportunities'));
  $('advanced').addEventListener('close',()=>{if(filterDraft){restoreFilters(filterDraft);filterDraft=null;++draftVersion;renderShell();}$('advanced-button').setAttribute('aria-expanded','false');});
  $('save-menu').addEventListener('close',()=>{$('save-card').setAttribute('aria-expanded','false');});
  document.querySelectorAll('dialog').forEach(dialog=>dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}}));
  if(window.innerWidth<700)$('sidebar-toggle').click();
  renderShell();
  if(data.loading){lockLoading(true);poll();}else if(data.meta){await poll();}
}
action(init)();
