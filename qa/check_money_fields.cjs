const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const elements = new Map();
function element(key) {
  if (!elements.has(key)) elements.set(key, {
    value:'', disabled:false, type:'number', textContent:'', innerHTML:'',
    addEventListener(){}, setAttribute(){}, insertAdjacentHTML(){},
    querySelector(selector){return element(key+' '+selector);}, querySelectorAll(selector){return selector==='input'?[element(key+' min'),element(key+' max')]:[];},
  });
  return elements.get(key);
}
const document = {
  getElementById:element, addEventListener(){}, querySelectorAll(){return [];},
  querySelector(selector){return element(selector);},
};
const source = fs.readFileSync(path.join(__dirname,'../web/app.js'),'utf8').replace('action(init)();','');
vm.runInNewContext(source + `
  salaryPrefs={currency:'EUR',period:'month',rate:1.25,money_rate:2,money_source:'clause'};
  for(const period of ['week','month','year']) {
    salaryPrefs.period=period;
    for(const key of ['value','balance','transfer_budget_remaining','release_fee']) {
      assert.equal(filterFactor(key),2);
      assert.equal(filterFactor(key+'_min'),2);
      assert(columnLabel(key).includes('EUR'));
    }
    assert.equal(filterFactor('wage'),salaryFactor());
  }
  salaryPrefs.period='month';
  assert.equal(moneyFormat(-125).replace(/[^0-9-]/g,''),'-250');
  assert.equal(moneyFormat(null),'—');
  fieldIds.push('value_min','value_max','balance_min','balance_max','transfer_budget_remaining_min','transfer_budget_remaining_max');
  for(const [key,amount] of [['value_min',200],['value_max',400],['balance_min',-200],['balance_max',100],['transfer_budget_remaining_min',50],['transfer_budget_remaining_max',300]]) {
    $(key).value=String(amount);
    assert.equal(Number(values()[key]),amount/2);
  }
  updateSalaryLabels();
  assert.equal(document.querySelector('[data-range="balance"]').querySelectorAll('input')[0].min,String(-2e12));
  kind='clubs';visibleColumns.clubs=['name','balance','transfer_budget_remaining'];
  rows=[{uid:1,name:'QA',balance:-125,transfer_budget_remaining:500}];
  renderTable();
  assert($('table').querySelector('tbody').innerHTML.includes(moneyFormat(-125)));
  assert($('table').querySelector('tbody').innerHTML.includes('1.000'));
  currentProfile={row:rows[0],history:[],shortlisted:false};profileTab='attributes';renderProfile();
  assert($('profile').innerHTML.includes('Saldo · EUR'));
  assert($('profile').innerHTML.includes(moneyFormat(-125)));
  kind='clubs';profileTab='loans';currentProfile.row.loans=[{kind_raw:1,original_amount:500,monthly_payment:30,monthly_interest:10,conditional_amount:0,start_date:'2020-03-01',end_date:'2055-03-30'}];renderProfile();
  assert($('profile').innerHTML.includes('Banco'));
  assert($('profile').innerHTML.includes('Dívida líquida atual: não disponível'));
  assert($('profile').innerHTML.includes('1.000'));
  assert($('profile').innerHTML.includes('Parcela por mês · EUR'));
  salaryPrefs.period='year';renderProfile();assert($('profile').innerHTML.includes(moneyFormat(30)));
  delete currentProfile.row.loans;renderProfile();assert($('profile').innerHTML.includes('Empréstimos não identificados'));
  currentProfile.row.loans=[];renderProfile();assert($('profile').innerHTML.includes('não significa dívida líquida zero'));
  salaryPrefs.period='month';
  kind='players';profileTab='transfer';currentProfile={row:{uid:2,name:'QA player',transfer_value:500},history:[],shortlisted:false};renderProfile();
  assert($('profile').innerHTML.includes('Valor de mercado · EUR'));
  assert($('profile').innerHTML.includes('1.000'));
  salaryPrefs={currency:'USD',period:'month',rate:null,money_rate:null,money_source:null};
  assert(moneyFormat(500).includes('unid. do save'));
  assert(!moneyFormat(500).includes('$'));
  assert.equal(filterFactor('value'),1);
  assert(columnLabel('value').includes('unid. do save'));
  salaryPrefs={currency:'EUR',period:'month',rate:1.2,money_rate:1.2,money_source:'salary'};
  assert(columnLabel('balance').includes('(aprox.)'));
`, {assert,document,window:{},structuredClone,Intl,console});
console.log('PASS: monetary tables/profiles, signed balances, canonical filter units and period independence');
