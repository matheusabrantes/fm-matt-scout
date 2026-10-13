const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const num = value => value == null ? '—' : Number(value).toLocaleString('pt-BR');
const fmtDate = value => value ? new Date(`${value}T12:00:00`).toLocaleDateString('pt-BR') : 'Não disponível';
const fieldIds = ['search','position','age_min','age_max','ca_min','pa_min','sum_min','club','nation','league','contract_before','rating_min','free','squad_scope','squad'];
const baseColumns = {players:['name','age','positions','club_name','team_slot','nation_id','eu_national','ca','pa','attribute_sum','rating'],staff:['name','staff_role','staff_area','age','club_name','ca','pa','attribute_sum','nation_id'],clubs:['name','nation_id','reputation','player_count','ca_mean','pa_mean','age_mean']};
let visibleColumns = structuredClone(baseColumns), searchTab = 'general';
const rangeLabels = {height_cm:'Altura (cm) †',stadium_seated_capacity:'Estádio: lugares sentados',stadium_expansion_capacity:'Estádio: capacidade de expansão',age:'Idade',ca:'Capacidade atual (CA) †',pa:'Potencial (PA) †',ability_difference:'Diferença PA − CA †',sum:'Soma dos atributos (36)',rating:'Nota atual (estimativa)',rep_home:'Reputação nacional',rep_current:'Reputação atual',rep_world:'Reputação mundial',club_reputation:'Reputação do clube',reputation:'Reputação do clube',value:'Valor de mercado · unidade do save',wage:'Salário · unidade do save †',release_fee:'Menor cláusula de liberação · unidade do save',balance:'Saldo · unidade do save',transfer_budget_remaining:'Orçamento de transferências · unidade do save',wage_budget_weekly:'Orçamento salarial · unidade do save'};
const rangeMax = {height_cm:255,stadium_seated_capacity:1000000,stadium_expansion_capacity:1000000,age:100,ca:200,pa:200,ability_difference:200,sum:720,rating:100,rep_home:10000,rep_current:10000,rep_world:10000,club_reputation:10000,reputation:10000,value:1e12,wage:1e12,release_fee:1e12,balance:1e12,transfer_budget_remaining:1e12,wage_budget_weekly:1e12};
const titles = {players:'Jogadores',staff:'Staff',clubs:'Clubes',shortlist:'Minha lista',squad:'Meu time'};
let view = 'players', kind = 'players', sort = 'pa', direction = 'desc', total = 0, moreRequest = 0;
let meta = null, groups = {}, roles = {}, saves = [], presets = [], conditions = {}, traitLabels = [];
let rows = [], currentProfile = null, profileTab = 'attributes', comparison = new Set(), loading = false;
let requestVersion = 0, profileVersion = 0, debounce, polling;
let optionsKind = null, viewVersion = 0;
const pickers = {};
let activePicker = null;
let salaryPrefs = {currency:'EUR',period:'month',rate:null}, salaryReference = null;
const salaryPeriods = {week:{factor:1,label:'semana'},month:{factor:52/12,label:'mês'},year:{factor:52,label:'ano'}};
function salaryFactor() { return salaryPrefs.rate == null ? 1 : salaryPrefs.rate * salaryPeriods[salaryPrefs.period].factor; }
function salaryUnit() { return salaryPrefs.rate == null ? 'semanal · unidade do save' : `${salaryPrefs.currency} / ${salaryPeriods[salaryPrefs.period].label}`; }
function salaryFormat(raw) { return raw == null ? 'Não disponível' : salaryPrefs.rate == null ? `${num(raw)} unid./sem. †` : new Intl.NumberFormat('pt-BR',{style:'currency',currency:salaryPrefs.currency,minimumFractionDigits:0,maximumFractionDigits:0}).format(raw*salaryFactor()); }
function updateSalaryLabels() {
  rangeLabels.wage=`Salário · ${salaryUnit()} †`;rangeLabels.wage_budget_weekly=`Orçamento salarial · ${salaryUnit()}`;
  for(const key of ['wage','wage_budget_weekly']) {
    const field=document.querySelector(`[data-range="${key}"]`);if(!field)continue;
    field.querySelector('legend').textContent=rangeLabels[key];
    field.querySelectorAll('input').forEach(input=>{input.max=String(rangeMax[key]*salaryFactor());input.step='any';});
  }
}
const pickerNames = {club:'Clubes',nation:'Nacionalidades',league:'Ligas dos clubes',based:'Países onde atua',nation_region:'Regiões da nacionalidade',based_region:'Regiões onde atua',contract_kind:'Tipos de contrato',squad_status:'Status no elenco',release_kind:'Cláusulas de liberação'};
const positionNames = {GK:'Goleiro',SW:'Líbero',DL:'Lateral esquerdo',DC:'Zagueiro',DR:'Lateral direito',DM:'Volante',ML:'Meia esquerdo',MC:'Meio-campista',MR:'Meia direito',AML:'Ponta esquerdo',AMC:'Meia ofensivo',AMR:'Ponta direito',STC:'Atacante',WBL:'Ala esquerdo',WBR:'Ala direito'};
pickerNames.staff_area='Áreas do staff';pickerNames.staff_role='Cargos do staff';

async function api(path, body) {
  const response = await fetch(`api/${path}`, body ? {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)} : {});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Erro ${response.status}`);
  return data;
}
function notice(message = '', error = false) {
  $('message').textContent = message;
  $('message').hidden = !message;
  $('message').classList.toggle('error', error);
}
function action(fn) { return (...args) => Promise.resolve(fn(...args)).catch(error => notice(error.message, true)); }
function values() {
  const filters = {};
  for (const id of fieldIds) {
    const control = $(id); if (!control) continue;
    if (control.disabled) continue;
    const value = control.type === 'checkbox' ? (control.checked ? '1' : '') : control.value;
    if (value) filters[id] = /^(wage|wage_budget_weekly)_(min|max)$/.test(id) ? String(Number((Number(value)/salaryFactor()).toFixed(6))) : value;
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
  $('result-count').textContent=`${num(total)} ${noun}`;
  $('filter-result-count').textContent=`${num(total)} resultados · filtros combinados`;
  $('sort-summary').textContent=`${columnLabel(sort)} ${direction==='desc'?'↓':'↑'}${kind==='players'?' · desempate pela soma':''}`;
  $('page-info').textContent=total?`${num(rows.length)} de ${num(total)} carregados`:'Nenhum resultado';
  $('next').disabled=loading||$('workspace').getAttribute('aria-busy')==='true'||rows.length>=total;
  $('next').textContent=moreRequest?'Carregando…':rows.length>=total?'Todos carregados':`Carregar mais ${num(Math.min(Number($('page-size').value),total-rows.length))} ${noun}`;
}
async function refreshRows(reset = true) {
  if (!meta || loading || !validateControls()) return;
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
  $('shortlist-count').textContent = data.shortlist_count;
  renderListStatus();
  $('export').disabled = !data.shortlist_count || kind === 'clubs';
  renderTable();
  scroll.scrollTop=append?scrollTop:0;
}
const labels = {height_cm:'Altura (cm) †',balance:'Saldo · unidade do save',transfer_budget_remaining:'Transferências · unidade do save',wage_budget_weekly:'Orçamento salarial',stadium_seated_capacity:'Estádio: lugares sentados',stadium_expansion_capacity:'Estádio: expansão',name:'Nome',age:'Idade',club_name:'Clube',ca:'CA †',pa:'PA †',attribute_sum:'Soma (36)',goalkeeping_sum:'Goleiro (11)',rating:'Nota est. %',nation_id:'País',reputation:'Reputação',positions:'Posição',ability_difference:'PA − CA †',rep_home:'Rep. nacional',rep_current:'Rep. atual',rep_world:'Rep. mundial',wage:'Salário †',value:'Valor',release_fee:'Cláusula',ca_mean:'CA médio †',pa_mean:'PA médio †',age_mean:'Idade média',player_count:'Jogadores',ca_count:'CA lidos',pa_count:'PA lidos',age_count:'Idades lidas',team_slot:'Equipe †'};
function columnLabel(key) { return key==='attribute_sum'&&kind==='staff'?'Soma de habilidades (19) †':key === 'wage_budget_weekly' ? `Orçamento salarial · ${salaryUnit()}` : key === 'wage' ? `Salário · ${salaryUnit()} †` : key === 'eu_national' ? 'Nacionalidade UE' : key === 'nation_id' ? kind==='clubs'?'País':'Nacionalidades' : key.startsWith('attr_') ? attributeLabel(key.slice(5)) : labels[key] || key; }
labels.staff_role='Função †';labels.league_name='Liga do clube †';labels.staff_area='Área do staff';
function euLabel(value) { return value===true?'Sim':value===false?'Não':'Indisponível'; }
function nationalityLabel(row) { return row.nationalities?.map(n=>`${n.name||'Nome indisponível'}${n.id===row.nation_id?' (principal)':''}${n.is_eu?' · UE':''}`).join('; ') || 'Nome indisponível'; }
function renderTable() {
  const columns = [...visibleColumns[kind]];
  if (kind === 'players' && $('position').value.split(',').includes('GK') && !columns.includes('goalkeeping_sum')) columns.push('goalkeeping_sum');
  const person = kind !== 'clubs';
  $('table').querySelector('thead').innerHTML = `<tr>${person ? '<th scope="col" aria-label="Lista de observação"></th><th scope="col" aria-label="Comparar"></th>' : ''}${columns.map(key => `<th scope="col" class="${key === 'attribute_sum' ? 'sum' : key !== 'name' && key !== 'club_name' && key !== 'positions' ? 'numeric' : ''}" ${key === sort ? `aria-sort="${direction === 'desc' ? 'descending' : 'ascending'}"` : ''}>${key === 'positions' ? 'Posição' : `<button data-sort="${key}" title="${key === 'attribute_sum' ? 'Soma dos 36 atributos técnicos, mentais e físicos. Não inclui CA, PA, goleiro ou ocultos.' : key === 'rating' ? 'Estimativa por posição com fórmula própria visível no perfil.' : `Ordenar por ${columnLabel(key)}`}">${columnLabel(key)}${key === sort ? direction === 'desc' ? ' ↓' : ' ↑' : ''}</button>`}</th>`).join('')}</tr>`;
  if(kind==='staff')$('table').querySelector('[data-sort="attribute_sum"]')?.setAttribute('title','Soma dos 19 atributos profissionais decodificados, peso igual, máximo 380. Leitura experimental. Personalidade e estilo não entram.');
  $('table').querySelector('tbody').innerHTML = rows.length ? rows.map(row => `<tr data-uid="${row.uid}" class="${currentProfile?.row.uid === row.uid ? 'selected' : ''}">${person ? `<td class="watch"><button data-watch="${row.uid}" class="${row.shortlisted ? 'active' : ''}" aria-label="${row.shortlisted ? 'Remover' : 'Adicionar'} ${esc(row.name)} ${row.shortlisted ? 'da' : 'à'} lista" aria-pressed="${row.shortlisted}">${row.shortlisted ? '●' : '○'}</button></td><td class="check"><input type="checkbox" data-compare="${row.uid}" aria-label="Comparar ${esc(row.name)}" ${comparison.has(row.uid) ? 'checked' : ''}></td>` : ''}${columns.map(key => {
    if (key === 'name') return `<td class="name"><button data-profile="${row.uid}">${esc(row.name || `Registro ${row.uid}`)}</button></td>`;
    if (key === 'league_name') return `<td>${esc(row.league_name||'Liga não lida')}</td>`;
    if (key === 'staff_area' || key === 'staff_role') return `<td>${esc(row[key])}</td>`;
    if (key==='attribute_sum'&&kind==='staff')return `<td class="numeric" title="Soma de 19 atributos profissionais; leitura experimental. Ausente quando algum deles não foi lido.">${row.attribute_sum==null?'Não disponível':num(row.attribute_sum)}</td>`;
    if (key === 'positions') return `<td>${esc(row.natural_positions?.join(', ') || '—')}</td>`;
    if (key === 'team_slot') return `<td title="Vínculo de equipe decodificado; categoria exata ainda sem nome confirmado">${row.team_slot==null?'—':row.team_slot===0?'Principal':`Secundária ${row.team_slot}`}</td>`;
    if (key === 'club_name') return `<td title="${esc(row.club_name)}">${esc(row.club_short_name || row.club_name || 'Sem vínculo decodificado')}</td>`;
    if (key === 'nation_id') return `<td>${esc(row.nation_name || 'Nome indisponível')}</td>`;
    if (key === 'eu_national') return `<td>${euLabel(row.eu_national)}</td>`;
    if (key === 'player_count' && row.player_count === 0) return '<td class="empty-squad">Nenhum jogador lido</td>';
    if (key === 'wage' || key === 'wage_budget_weekly') return `<td class="numeric">${salaryFormat(row[key])}</td>`;
    return `<td class="numeric ${key === 'attribute_sum' ? 'sum' : key === 'ca' || key === 'pa' ? 'ability' : ''}" ${key.endsWith('_mean')?`title="${row[key.replace('_mean','_count')]} de ${row.player_count} jogadores com valor disponível"`:''}>${key === 'rating' || key.endsWith('_mean') ? row[key] == null ? '—' : row[key].toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1}) : num(row[key])}</td>`;
  }).join('')}</tr>`).join('') : `<tr><td class="empty-row" colspan="${columns.length+(person?2:0)}">${view === 'shortlist' ? 'Sua lista está vazia. Use o círculo ao lado de um nome para adicionar.' : view === 'squad' && !meta.managed.length ? 'O clube do treinador não foi identificado neste save. Use o filtro de clube na aba Jogadores.' : 'Nenhum registro atende aos filtros. Reduza os critérios ou clique em Limpar.'}</td></tr>`;
  $('table').querySelector('thead tr').insertAdjacentHTML('afterbegin','<th scope="col" class="row-number" title="Número da linha nos filtros e na ordenação atuais">Nº</th>');
  $('table').querySelectorAll('tbody tr[data-uid]').forEach((row,index)=>row.insertAdjacentHTML('afterbegin',`<td class="row-number">${num(index+1)}</td>`));
  const empty=$('table').querySelector('.empty-row');if(empty)empty.colSpan++;
}
function updateComparison() {
  $('compare-count').textContent = `${comparison.size}/2`;
  $('compare').disabled = comparison.size !== 2 || loading;
}
async function toggleWatch(uid) {
  const requestedKind=kind, requestedView=viewVersion;
  const result = await api('shortlist',{kind,uid});
  if(kind!==requestedKind||viewVersion!==requestedView)return;
  if (currentProfile?.row.uid === uid) { currentProfile.shortlisted = result.shortlisted; renderProfile(); }
  const row=rows.find(r=>r.uid===uid);
  if(row)row.shortlisted=result.shortlisted;
  if(row&&!result.shortlisted&&(view==='shortlist'||$('within_shortlist').checked)){
    ++requestVersion;moreRequest=0;$('workspace').setAttribute('aria-busy','false');
    rows=rows.filter(r=>r.uid!==uid);total--;
  }
  $('shortlist-count').textContent=num(result.shortlist_count);
  $('export').disabled=!result.shortlist_count||kind==='clubs';
  if(rows.length===0&&total>0)return refreshRows(true);
  renderListStatus();renderTable();
}
async function showProfile(uid) {
  const version = ++profileVersion;
  const data = await api(`profile?kind=${kind}&uid=${uid}`);
  if (version !== profileVersion) return;
  currentProfile = data; profileTab = 'attributes'; renderProfile(); renderTable();
}
function definition(items) {
  return `<dl>${items.map(([key,value]) => `<div><dt>${esc(key)}</dt><dd>${esc(value ?? 'Não disponível')}</dd></div>`).join('')}</dl>`;
}
function attributeValue(value) { return `<span class="attribute-value ${value >= 15 ? 'high' : value >= 10 ? 'medium' : ''}">${value == null ? '—' : esc(value)}</span>`; }
function attributeGroup(row, title) {
  const source = title === 'Personalidade' ? row.personality : title === 'Profissionais' ? row.professional_attributes : row.attributes;
  if (!source) return '';
  const fields = groups[title];
  const sum = {'Técnicos':row.technical_sum,'Mentais':row.mental_sum,'Físicos':row.physical_sum,'Goleiro':row.goalkeeping_sum,'Profissionais':row.attribute_sum}[title];
  return `<section class="attribute-group"><h3>${esc(title)}${sum == null ? '' : `<span>Σ ${sum}</span>`}</h3>${Object.entries(fields).map(([key,label]) => `<div class="attribute-row"><span>${esc(label)}</span>${attributeValue(source[key])}</div>`).join('')}</section>`;
}
function renderProfile() {
  if (!currentProfile) return;
  const {row:r,history,shortlisted} = currentProfile;
  const player = kind === 'players', staff = kind === 'staff';
  const tabs = kind === 'clubs' ? {attributes:'Clube',squad:'Elenco'} : {attributes:'Atributos',hidden:'Ocultos',transfer:'Contrato',...(player ? {roles:'Posições',report:'Relatório',history:'Evolução'} : {preferences:'Estilo'})};
  let content = '';
  if (profileTab === 'attributes') {
    if (player || staff) content += `<div class="ability-strip"><div><span>CA †</span><strong>${num(r.ca)}</strong></div><div><span>PA †</span><strong>${num(r.pa)}</strong></div>${player ? `<div class="total"><span>Soma (36)</span><strong>${num(r.attribute_sum)}</strong></div>` : ''}</div>`;
    content += definition([['Idade',r.age == null ? null : `${r.age} anos`],['Nascimento',fmtDate(r.birth_date)],['Nacionalidades',nationalityLabel(r)],['Possui nacionalidade UE',euLabel(r.eu_national)],['ID do FM',r.unique_id],['Liga do clube †',r.league_name||'Liga não lida'],...(player ? [['Altura',r.height_cm == null ? null : `${r.height_cm} cm`],['Pé esquerdo / direito',`${r.left_foot ?? '—'} / ${r.right_foot ?? '—'}`],['Diferença PA − CA †',r.ability_difference],['Reputação nacional',r.rep_home],['Reputação atual',r.rep_current],['Reputação mundial',r.rep_world],['Condição (valor bruto)',r.raw_condition],['Ritmo (valor bruto)',r.raw_match_sharpness]] : [])]);
    if (player) content += `<p class="fine">Soma = técnicos + mentais + físicos: 36 atributos, peso igual, máximo 720. Goleiro tem soma própria de 11 atributos.</p>${['Técnicos','Mentais','Físicos',...(r.positions?.gk >= 15 ? ['Goleiro'] : [])].map(g => attributeGroup(r,g)).join('')}`;
    if (staff) content += definition([['Função',r.staff_role],['Área do staff',r.staff_area],['Soma de habilidades (19) †',r.attribute_sum]])+`<p class="fine">A área vem das listas do clube. Treinador principal e diretor de futebol são identificados por assentos do clube e contrato no mesmo clube, quando lidos. Os demais cargos ainda não são identificados. Soma dos 19 atributos profissionais disponíveis, peso igual, máximo 380. Leitura experimental: ainda sem conferência no jogo para este save. Preferências e personalidade não entram nessa soma.</p>${attributeGroup(r,'Profissionais')}${attributeGroup(r,'Personalidade')}`;
    if (kind === 'clubs') content = definition([['Nome',r.name],['Nome curto',r.short_name],['ID do FM',r.unique_id],['País',r.nation_name || 'Nome indisponível'],['Reputação',r.reputation],['Liga do clube †',r.league_name||'Liga não lida'],['Última posição na liga',r.last_league_position || null],['Equipes no save',r.teams?.length],['Saldo (unidade do save)',r.balance],['Transferências restantes',r.transfer_budget_remaining],[`Orçamento salarial · ${salaryUnit()}`,salaryFormat(r.wage_budget_weekly)],['Data dos valores financeiros',fmtDate(r.finance_date)],['Estádio',r.stadium_seated_capacity==null?null:r.stadium_name||'Nome não lido'],['Lugares sentados',r.stadium_seated_capacity],['Capacidade de expansão',r.stadium_expansion_capacity]]) + '<p class="fine">Finanças disponíveis apenas nos clubes cobertos pelo leitor. Estádio vinculado pelos jogos em casa, quando há um único vínculo. Lugares sentados não equivalem necessariamente à capacidade total. Instalações de treino, formação, uniformes e melhores formações ainda pendentes.</p>';
    if(kind==='clubs')content+=definition([['Categoria',r.gender==='male'?'Masculino (base de referência)':r.gender==='female'?'Feminino (base de referência)':'Categoria não identificada']]);
  } else if (profileTab === 'hidden') content = `${player ? attributeGroup(r,'Ocultos') : ''}${attributeGroup(r,'Personalidade')}<p class="fine">Propensão a lesões, jogo sujo e controvérsia: valores menores podem ser desejáveis. Use o filtro “No máximo”.</p>`;
  else if (profileTab === 'transfer') {
    const c = r.contract || (staff ? {wage:r.wage,start:r.contract_start,end:r.contract_end} : {});
    content = definition([['Clube',r.club_name],['Contrato desde',fmtDate(c.start)],['Contrato até',fmtDate(c.end)],['Tipo',c.kind==='unknown'?'Nome indisponível':c.kind?.replaceAll('_',' ')],['Status no elenco',c.squad_status?.replaceAll('_',' ')],[`Salário · ${salaryUnit()} †`,salaryFormat(c.wage)],...(player ? [['Valor (unidade do save)',num(r.transfer_value)],['Emprestado',r.on_loan==null?'Não disponível':r.on_loan ? 'Sim' : 'Não'],['Clube de origem',r.loan_parent_club_name],['Fim do empréstimo',fmtDate(r.loan_end)]] : [])]);
    if(c.clauses?.length)content+='<h3>Cláusulas do contrato</h3>'+definition(c.clauses.map(clause=>[clause.kind==='unknown'?`Código ${clause.kind_code}`:clause.kind.replaceAll('_',' '),clause.value==null?'Parâmetro: '+(clause.parameter??'—'):num(clause.value)]));
    content += '<p class="fine">Salários usam as preferências de exibição após conferir a conversão com o FM. Outros valores monetários continuam nas unidades do arquivo. Salário ainda sem confirmação independente; preço estimado de venda indisponível. Cláusulas podem ter condições específicas.</p>';
  } else if (profileTab === 'roles') {
    content = '<p class="fine">Nota Matt Scout: média ponderada dos atributos × 5 × (0,75 + 0,25 × familiaridade/20). Estimativa própria por posição; não replica os percentuais do Genie. A avaliação por IA será decidida depois.</p>';
    content += Object.entries(r.roles).sort((a,b)=>(b[1]??-1)-(a[1]??-1)).map(([key,score]) => `<details class="role-row"><summary><span>${esc(roles[key].name)} · posição ${r.positions?.[roles[key].position] ?? '—'}/20</span><strong>${score == null ? '—' : `${num(score)}%`}</strong></summary><p>${Object.entries(roles[key].weights).map(([attr,weight]) => `${esc(attributeLabel(attr))} × ${weight}`).join(' · ')}</p></details>`).join('');
    content += '<h3>Familiaridade nas posições</h3>' + definition(Object.entries(r.positions || {}).map(([position,value]) => [position.toUpperCase(),`${value}/20`]));
    if (r.traits_code?.length) content += `<p class="fine">${r.traits_code.length} movimentos ainda sem nome identificado pelo leitor.</p>`;
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
  $('profile').innerHTML = `<div class="profile-heading"><h2>${esc(r.name || `Registro ${r.uid}`)}</h2><p>${esc(r.club_name || r.short_name || 'Sem vínculo decodificado')}${player ? ` · ${esc(r.natural_positions?.join(', ') || '')}` : ''}</p>${kind !== 'clubs' ? `<div class="profile-actions"><button id="profile-watch">${shortlisted ? 'Remover da lista' : 'Adicionar à lista'}</button><button id="profile-compare">${comparison.has(r.uid) ? 'Tirar da comparação' : 'Comparar jogador'}</button></div>` : ''}</div><div class="profile-tabs">${Object.entries(tabs).map(([key,label])=>`<button data-profile-tab="${key}" class="${key===profileTab?'active':''}" aria-pressed="${key===profileTab}">${label}</button>`).join('')}</div><div class="profile-content">${content}<p class="fine">† CA/PA, altura, salário, habilidades profissionais, cargos por assento e liga por tabela: leitura experimental, sem conferência independente no jogo para este save.</p></div>`;
}
function attributeLabel(key) {
  return Object.values(groups).map(group=>group[key]).find(Boolean) || key;
}
function toggleCompare(uid) {
  if (comparison.has(uid)) comparison.delete(uid);
  else if (comparison.size < 2) comparison.add(uid);
  else { notice('Escolha até dois registros. Desmarque um para trocar.'); renderTable(); return; }
  updateComparison(); renderTable(); if (currentProfile) renderProfile();
}
async function comparePlayers() {
  const data = await Promise.all([...comparison].map(uid=>api(`profile?kind=${kind}&uid=${uid}`)));
  const [a,b] = data.map(d=>d.row);
  const line = (label,av,bv,inverse=false) => {
    const comparable = typeof av === 'number' && typeof bv === 'number';
    return `<tr><td>${esc(label)}</td><td class="${comparable && (inverse?av<bv:av>bv) ? 'better' : ''}">${esc(av ?? '—')}</td><td class="${comparable && (inverse?bv<av:bv>av) ? 'better' : ''}">${esc(bv ?? '—')}</td></tr>`;
  };
  const bothKeepers = kind === 'players' && a.positions?.gk >= 15 && b.positions?.gk >= 15;
  const scoreGroups = kind === 'players' ? ['Técnicos','Mentais','Físicos',...(bothKeepers?['Goleiro']:[])] : ['Profissionais'];
  const sumGroups = kind === 'players' ? [...scoreGroups,'Ocultos','Personalidade'] : ['Profissionais','Personalidade'];
  const wins=[0,0];let ties=0,missing=0;
  for(const group of scoreGroups)for(const key of Object.keys(groups[group])) {
    const av=(group==='Personalidade'?a.personality:group==='Profissionais'?a.professional_attributes:a.attributes)?.[key],bv=(group==='Personalidade'?b.personality:group==='Profissionais'?b.professional_attributes:b.attributes)?.[key];
    if(typeof av!=='number'||typeof bv!=='number'){missing++;continue;}
    if(av===bv)ties++;else wins[(key==='controversy'?av<bv:av>bv)?0:1]++;
  }
  const score = [a,b].map((player,i)=>`<div class="${wins[i]>wins[1-i]?'better':''}"><strong>${esc(player.name)}</strong><span>${num(wins[i])} atributos vencidos</span>${wins[i]>wins[1-i]?'<b>Venceu por atributos</b>':''}</div>`).join('');
  const summary=`<div class="comparison-score">${score}</div><p class="fine comparison-score-note">${wins[0]===wins[1]?'Empate no placar · ':''}${num(ties)} atributos empatados${missing?` · ${num(missing)} sem dados comparáveis`:''}. ${kind==='players'?`Contagem dos ${bothKeepers?47:36} atributos técnicos, mentais e físicos${bothKeepers?', incluindo goleiro':''}, com o mesmo peso.`:'Contagem dos 19 atributos profissionais decodificados, com o mesmo peso. Leitura experimental.'}</p>`;
  $('compare-title').textContent = kind === 'staff' ? 'Comparar staff' : 'Comparar jogadores';
  $('comparison').innerHTML = `${summary}<table><thead><tr><th>Critério</th><th>${esc(a.name)}</th><th>${esc(b.name)}</th></tr></thead><tbody><tr><td>Idade</td><td>${esc(a.age??'—')}</td><td>${esc(b.age??'—')}</td></tr>${line('CA †',a.ca,b.ca)}${line('PA †',a.pa,b.pa)}${line(kind==='players'?'Soma (36)':'Soma profissional (19) †',a.attribute_sum,b.attribute_sum)}${sumGroups.map(group => `<tr class="group-row"><td colspan="3">${esc(group)}</td></tr>${Object.entries(groups[group]).map(([key,label])=>line(label,(group==='Personalidade'?a.personality:group==='Profissionais'?a.professional_attributes:a.attributes)?.[key],(group==='Personalidade'?b.personality:group==='Profissionais'?b.professional_attributes:b.attributes)?.[key],['injury_proneness','dirtiness','controversy'].includes(key))).join('')}`).join('')}</tbody></table><p class="fine">Verde destaca o maior valor; em propensão a lesões, jogo sujo e controvérsia, destaca o menor. Isso não determina sozinho o melhor jogador.</p>`;
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
  if (oldKind !== kind) { comparison.clear(); updateComparison(); sort = kind === 'clubs' ? 'reputation' : 'pa'; resetFilters(); currentProfile = null; ++profileVersion; }
  document.querySelectorAll('[data-view]').forEach(button=>button.toggleAttribute('aria-current',button.dataset.view===view));
  document.querySelector('[data-view="'+view+'"]').setAttribute('aria-current','page');
  $('list-title').textContent = view === 'squad' && meta?.managed?.length ? meta.managed[0].club_short_name || meta.managed[0].club_name : titles[view];
  $('search').placeholder = kind === 'players' ? 'Nome do jogador ou clube' : kind === 'staff' ? 'Nome do staff ou clube' : 'Nome do clube';
  for (const id of ['position','sum_min','rating_min']) $(id).disabled = kind !== 'players';
  for (const id of ['age_min','age_max','ca_min','pa_min','contract_before','free']) $(id).disabled = kind === 'clubs';
  $('club').disabled = view === 'squad';
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
    if (id.startsWith('value_') || id.startsWith('release_fee_') || ['traits','squad_status','contract_kind','release_kind','has_release'].includes(id)) $(id).disabled = kind !== 'players';
    if(['based','no_contract'].includes(id))$(id).disabled=kind==='clubs';
    if (['balance_','transfer_budget_remaining_','wage_budget_weekly_','reputation_','stadium_seated_capacity_','stadium_expansion_capacity_'].some(prefix=>id.startsWith(prefix))) $(id).disabled = kind !== 'clubs';
    if(['wage_min','wage_max','free','contract_after','contract_before','within_shortlist'].includes(id)) $(id).disabled=kind==='clubs';
  }
  $('pitch-panel').hidden = kind !== 'players'; $('search-title').textContent = kind==='players'?'Pesquisa de jogadores':kind==='staff'?'Pesquisa de staff':'Pesquisa de clubes';
  rangeMax.sum=kind==='staff'?380:720;
  $('sum_min').placeholder=kind==='staff'?'19–380':'36–720';
  $('general-fields').querySelector('[data-range="sum"] legend').textContent=kind==='staff'?'Soma profissional (19) †':'Soma dos atributos (36)';
  for(const input of document.querySelectorAll('#sum_min,#sum_max,[data-mirror="sum_min"],[data-mirror="sum_max"]'))input.max=rangeMax.sum;
  syncMirrors(); updatePitch();syncPickers();
  document.querySelectorAll('[data-range]').forEach(field=>field.hidden=[...field.querySelectorAll('input')].every(input=>input.disabled));
  $('table-note').textContent = kind === 'players' ? 'Soma: 36 atributos de linha. † CA/PA: sem confirmação independente. Nota: estimativa Matt Scout.' : kind === 'staff' ? 'Soma: 19 atributos profissionais, leitura experimental. Área: listas médica, comissão técnica e recrutamento; treinador principal/diretor por assento e contrato; demais cargos não lidos.' : `${num(meta?.hidden_female_clubs||0)} clubes femininos identificados ocultos. Categoria desconhecida permanece visível. Médias usam jogadores lidos; † CA/PA e vínculos experimentais.`;
  if (!currentProfile) $('profile').innerHTML = '<div class="profile-empty"><h2>Abra um perfil</h2><p>Clique no nome para consultar os dados.</p></div>';
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
  document.querySelectorAll('[data-view],#filters input,#filters select,#filters button,#advanced input,#advanced select,#advanced button,#next,#page-size,#table button,#table input').forEach(control=>control.disabled=control.closest('.unavailable')?true:value);
  $('open').disabled = value; $('reload').disabled = value || !meta;
  $('salary-settings').disabled=value||!meta;
  $('workspace').setAttribute('aria-busy',String(value));
  if (value) { $('compare').disabled = true; $('export').disabled = true; }
  else $('remove-preset').disabled=!$('preset').value;
}
window.loadSave = action(async path => {
  if (loading) return;
  for (const dialog of document.querySelectorAll('dialog[open]')) dialog.close();
  await api('load',{path}); lockLoading(true); notice('Preparando leitura do save…');
  poll();
});
async function poll() {
  clearTimeout(polling);
  try {
    const data = await api('status');
    if (data.loading) { notice(data.progress); $('footer-state').textContent = 'Lendo cópia do save…'; polling = setTimeout(poll,600); return; }
    lockLoading(false);
    if (data.error) { notice(data.error,true); if (meta) await changeView(view); return; }
    meta = data.meta; $('reload').disabled=!meta;optionsKind=null;currentProfile = null; comparison.clear(); updateComparison();
    if (meta) {
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
}
function syncMirrors() { document.querySelectorAll('[data-mirror]').forEach(input=>{input.value=$(input.dataset.mirror).value;input.disabled=$(input.dataset.mirror).disabled;}); }
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
  $('picker-options').innerHTML=visible.length?visible.map(o=>`<label class="picker-option"><input type="checkbox" data-picker-value="${esc(o.value)}" ${selected.has(o.value)?'checked':''}><span>${esc(o.label)}</span></label>`).join(''):'<p class="fine">Nenhuma opção corresponde à busca.</p>';
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
  $('contract-fields').innerHTML = `<div class="location-grid"><label>Contrato expira a partir de<input id="contract_after" type="date"></label><label>Contrato expira até<input id="contract_before" type="date"></label><label>Tipo de contrato<select id="contract_kind"><option value="">Qualquer</option><option value="1">Tempo integral</option><option value="3">Jovem</option><option value="2">Código 2 · sem nome confirmado</option></select></label><label>Status no elenco<select id="squad_status"><option value="">Qualquer</option>${[[1,'Estrela'],[2,'Jogador importante'],[3,'Titular habitual'],[4,'Jogador de elenco'],[5,'Reserva de impacto'],[7,'Pouco utilizado'],[9,'Reserva de emergência'],[10,'Promessa em ascensão'],[11,'Promessa futura'],[13,'Jovem'],[14,'Titular da equipe B'],[15,'Goleiro titular'],[16,'Goleiro de copas'],[17,'Goleiro de copas nacionais'],[18,'Goleiro de copas continentais'],[20,'Reserva'],[21,'Goleiro reserva de emergência'],[22,'Excedente']].map(([id,label])=>`<option value="${id}">${label}</option>`).join('')}</select></label><label>Cláusula de liberação<select id="release_kind"><option value="">Qualquer</option>${[['minimum_fee_release','Mínima geral'],['minimum_fee_release_foreign','Clubes estrangeiros'],['minimum_fee_release_domestic','Clubes nacionais'],['minimum_fee_release_domestic_higher_division','Divisão nacional superior'],['relegation_release','Por rebaixamento'],['non_promotion_release','Por não promoção']].map(([id,label])=>`<option value="${id}">${label}</option>`).join('')}</select></label></div><div class="check-grid"><label class="checkbox-label"><input id="free" type="checkbox">Sem clube decodificado</label><label class="checkbox-label"><input id="no_contract" type="checkbox">Sem contrato decodificado</label><label class="checkbox-label"><input id="has_release" type="checkbox">Com cláusula de liberação decodificada</label></div><div class="range-grid">${['value','wage','release_fee'].map(rangeFields).join('')}</div><p class="fine">Valores financeiros usam as unidades do save, sem conversão de moeda. Ausência de contrato lido pode ser falta de cobertura do leitor. A menor cláusula pode ser condicional; confira no perfil.</p><details class="pending-fields"><summary>Filtros ainda sem dados confiáveis</summary><div class="location-grid">${[['Disponível pela regra Bosman','Elegibilidade não calculada'],['Disponibilidade para transferência','Não decodificada'],['Listado para transferência','Não decodificado'],['Listado para empréstimo','Não decodificado'],['Valor estimado de venda','Sem estimativa validada']].map(([l,r])=>unavailable(l,r)).join('')}</div></details>`;
  for(const id of ['based','nation_region','based_region','eu_national','within_shortlist','contract_after','no_contract','contract_kind','squad_status','release_kind','has_release','traits']) if(!fieldIds.includes(id)) fieldIds.push(id);
  const coords={STC:[50,10],AML:[18,23],AMC:[50,27],AMR:[82,23],ML:[18,42],MC:[50,43],MR:[82,42],DM:[50,58],WBL:[12,62],WBR:[88,62],DL:[18,76],DC:[50,75],DR:[82,76],SW:[50,85],GK:[50,95]};
  for(const [position,[x,y]] of Object.entries(coords)) {
    const button=document.createElement('button'); button.textContent=position;button.dataset.pitch=position;button.setAttribute('aria-label',`Filtrar posição ${position}`);button.setAttribute('aria-pressed','false');
    button.style.left=`${x}%`;button.style.top=`${y}%`; $('pitch').append(button);
  }
  buildSearchTabs(); syncMirrors();
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
  if(groups[tab]) $('attribute-grid').innerHTML = `<table><thead><tr><th>Atributo</th><th>Mínimo</th><th>Máximo</th></tr></thead><tbody>${Object.entries(groups[tab]).sort((a,b)=>a[1].localeCompare(b[1],'pt-BR')).map(([key,label])=>`<tr><td>${esc(label)}</td><td><input type="number" min="1" max="20" placeholder="1" data-condition="attr_${key}" aria-label="${esc(label)} mínimo" value="${esc(conditions[`attr_${key}`]||'')}"></td><td><input type="number" min="1" max="20" placeholder="20" data-condition="maxattr_${key}" aria-label="${esc(label)} máximo" value="${esc(conditions[`maxattr_${key}`]||'')}"></td></tr>`).join('')}</tbody></table>`;
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
  const button = event.target.closest('button'); if (!button) return;
  if (button.dataset.view) return changeView(button.dataset.view);
  if(button.dataset.pickerOpen) {
    const id=button.dataset.pickerOpen;if(pickers[id].input.disabled)return;
    activePicker=id;$('picker-title').textContent=`Selecionar ${pickerNames[id]}`;$('picker-search').value='';renderPickerOptions();$('picker-dialog').showModal();$('picker-search').focus();return;
  }
  if (button.dataset.filterTab) { showSearchTab(button.dataset.filterTab); return; }
  if (button.dataset.pitch) { const chosen=new Set($('position').value.split(',').filter(Boolean));if(chosen.has(button.dataset.pitch))chosen.delete(button.dataset.pitch);else chosen.add(button.dataset.pitch);$('position').value=[...chosen].join(',');updatePitch();syncMirrors();return refreshRows(true); }
  if (button.dataset.sort) { direction = sort === button.dataset.sort && direction === 'desc' ? 'asc' : 'desc'; sort = button.dataset.sort; return refreshRows(true); }
  if (button.dataset.profile) return showProfile(Number(button.dataset.profile));
  if (button.dataset.watch) return toggleWatch(Number(button.dataset.watch));
  if (button.dataset.profileTab) { profileTab = button.dataset.profileTab; renderProfile(); return; }
  if (button.dataset.save) return window.loadSave(saves[Number(button.dataset.save)].path);
  if (button.dataset.close) { $(button.dataset.close).close(); return; }
  if (button.dataset.removeCondition) { delete conditions[button.dataset.removeCondition]; renderConditions(); return refreshRows(true); }
  switch (button.id) {
    case 'open':
      if (window.webkit?.messageHandlers?.openSave) window.webkit.messageHandlers.openSave.postMessage(null);
      else { saveButtons($('dialog-saves')); $('open-dialog').showModal(); }
      break;
    case 'load-path': return window.loadSave($('save-path').value);
    case 'reload': return window.loadSave(meta.path);
    case 'salary-settings':
      salaryReference=kind!=='clubs'&&currentProfile?{kind,uid:currentProfile.row.uid,name:currentProfile.row.name}:null;
      $('salary-currency').value=salaryPrefs.currency;$('salary-period').value=salaryPrefs.period;$('salary-amount').value='';
      $('salary-amount').disabled=!salaryReference;
      $('salary-reference').textContent=salaryReference?`Profissional selecionado: ${salaryReference.name}`:'Abra o perfil de um jogador ou staff para conferir a conversão.';
      $('salary-status').textContent=salaryPrefs.rate==null?'Conversão ainda não conferida. Os salários continuam identificados como unidades do save por semana.':`Salários em ${salaryUnit()}. Conversão conferida nesta carreira.`;
      $('salary-dialog').showModal();break;
    case 'save-salary': {
      const body={currency:$('salary-currency').value,period:$('salary-period').value};
      if($('salary-amount').value){if(!$('salary-amount').reportValidity())return;Object.assign(body,salaryReference,{amount:Number($('salary-amount').value)});}
      const oldFactor=salaryFactor();salaryPrefs=await api('salaries',body);
      for(const key of ['wage','wage_budget_weekly'])for(const bound of ['min','max']){const input=$(key+'_'+bound);if(input?.value)input.value=String(Number(input.value)/oldFactor*salaryFactor());}
      updateSalaryLabels();$('salary-dialog').close();if(currentProfile)renderProfile();
      notice(salaryPrefs.rate==null?'Preferências salvas. A conversão dessa moeda ainda precisa ser conferida com o FM.':`Salários em ${salaryUnit()}; filtros mantêm os mesmos limites.`);
      renderListStatus();renderTable();return;
    }
    case 'advanced-button': $('advanced').showModal(); button.setAttribute('aria-expanded','true'); break;
    case 'quick-position':showSearchTab('general');$('advanced').showModal();break;
    case 'picker-clear':if(activePicker){pickers[activePicker].input.value='';syncPickers();renderPickerOptions();return refreshRows(true);}break;
    case 'clear-search':
    case 'clear': resetFilters(); return refreshRows(true);
    case 'next': return refreshRows(false);
    case 'compare': return comparePlayers();
    case 'columns': {
      const extras=kind==='players'?['height_cm','ability_difference','nation_id','eu_national','goalkeeping_sum','rep_home','rep_current','rep_world','wage','value','release_fee']:kind==='staff'?['ability_difference','wage','eu_national','staff_area','staff_role','attribute_sum']:['ca_count','pa_count','age_count','balance','transfer_budget_remaining','wage_budget_weekly','stadium_seated_capacity','stadium_expansion_capacity'];
      const options=[...new Set([...baseColumns[kind],'league_name',...extras])];
      const attributeGroups=kind==='players'?Object.entries(groups).filter(([g])=>g!=='Profissionais'):kind==='staff'?[['Profissionais',groups.Profissionais],['Personalidade',groups.Personalidade]]:[];
      $('column-options').innerHTML = `<div class="column-grid">${options.map(key=>`<label class="checkbox-label"><input data-column="${key}" type="checkbox" ${visibleColumns[kind].includes(key)?'checked':''} ${key==='name'?'disabled':''}>${esc(columnLabel(key))}</label>`).join('')}</div>${attributeGroups.map(([group,fields])=>`<h3>${esc(group)}</h3><div class="column-grid">${Object.entries(fields).map(([key,label])=>`<label class="checkbox-label"><input data-column="attr_${key}" type="checkbox" ${visibleColumns[kind].includes('attr_'+key)?'checked':''}>${esc(label)}</label>`).join('')}</div>`).join('')}`;
      $('columns-dialog').showModal(); break;
    }
    case 'save-columns': {
      visibleColumns[kind]=[...document.querySelectorAll('[data-column]:checked')].map(c=>c.dataset.column);
      await api('layouts',visibleColumns);$('columns-dialog').close();return refreshRows();
    }
    case 'reset-columns': visibleColumns[kind]=[...baseColumns[kind]];await api('layouts',visibleColumns);$('columns-dialog').close();return refreshRows();
    case 'profile-compare': toggleCompare(currentProfile.row.uid); break;
    case 'profile-watch': return toggleWatch(currentProfile.row.uid);
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
            $(key).value=/^(wage|wage_budget_weekly)_(min|max)$/.test(key)?String(Number(value)*salaryFactor()):value;
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
  if (event.target.dataset.compare) { toggleCompare(Number(event.target.dataset.compare)); return; }
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
$('picker-search').addEventListener('input',renderPickerOptions);
document.addEventListener('keydown',event=>{if((event.metaKey||event.ctrlKey)&&event.key==='f'){event.preventDefault();$('search').focus();}});
async function init() {
  const data=await api('status'); groups=data.groups; roles=data.roles; saves=data.saves;traitLabels=data.traits;buildSearch();saveButtons($('save-list')); await refreshPresets();
  const layout=await api('layouts');visibleColumns={...visibleColumns,...layout};
  $('trait-grid').innerHTML=traitLabels.map(t=>`<label class="checkbox-label"><input type="checkbox" data-trait="${t.id}">${esc(t.name)}</label>`).join('');
  $('advanced').addEventListener('close',()=>{$('advanced-button').setAttribute('aria-expanded','false');});
  if(data.loading){lockLoading(true);poll();}else if(data.meta){await poll();}
}
action(init)();
