(() => {
  'use strict';
  const available = new Set('ad ae af ag ai al am ao aq ar as at au aw ax az ba bb bd be bf bg bh bi bj bl bm bn bo bq br bs bt bv bw by bz ca cc cd cf cg ch ci ck cl cm cn co cr cu cv cw cx cy cz de dj dk dm do dz ec ee eg eh er es et fi fj fk fm fo fr ga gb gb-eng gb-nir gb-sct gb-wls gd ge gf gg gh gi gl gm gn gp gq gr gs gt gu gw gy hk hm hn hr ht hu id ie il im in io iq ir is it je jm jo jp ke kg kh ki km kn kp kr kw ky kz la lb lc li lk lr ls lt lu lv ly ma mc md me mf mg mh mk ml mm mn mo mp mq mr ms mt mu mv mw mx my mz na nc ne nf ng ni nl no np nr nu nz om pa pe pf pg ph pk pl pm pn pr ps pt pw py qa re ro rs ru rw sa sb sc sd se sg sh si sj sk sl sm sn so sr ss st sv sx sy sz tc td tf tg th tj tk tl tm tn to tr tt tv tw tz ua ug um us uy uz va vc ve vg vi vn vu wf ws xk ye yt za zm zw crimea zanzibar'.split(' '));
  const codes = Object.create(null);
  const displayNames = new Intl.DisplayNames(['pt-BR'], {type:'region'});
  for (const code of available) {
    if (code.length === 2) codes[displayNames.of(code.toUpperCase())] = code;
  }
  Object.assign(codes, {
    'Inglaterra':'gb-eng', 'Escócia':'gb-sct', 'País de Gales':'gb-wls', 'Irlanda do Norte':'gb-nir',
    'Taiwan (Taipé Chinês)':'tw', 'República Tcheca':'cz', 'Taiti':'pf', 'Bonaire':'bq',
    'Benim':'bj', 'Burkina Faso':'bf', 'Malawi':'mw', 'Seychelles':'sc', 'Congo':'cg',
    'República Democrática do Congo':'cd', 'Bahrein':'bh', 'Hong Kong':'hk', 'Macau':'mo',
    'Myanmar':'mm', 'Tajiquistão':'tj', 'Belarus':'by', 'Palestina':'ps', 'Anguilla':'ai',
    'Ilhas Turks e Caicos':'tc', 'Kiribati':'ki', 'Saint-Martin':'mf', 'Saint-Pierre e Miquelon':'pm',
    'Crimeia':'crimea', 'Zanzibar':'zanzibar',
  });
  const escape = value => value.replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  function html(name, context = 'table') {
    const label = String(name ?? ''), code = codes[label];
    if (!available.has(code)) return '';
    context = ['table','picker','profile','token'].includes(context) ? context : 'table';
    const [width,height] = context === 'profile' ? [16,12] : context === 'token' ? [14,10] : [18,13];
    const extension = code === 'crimea' || code === 'zanzibar' ? 'svg' : 'png';
    return `<img class="fm-flag fm-flag--${context}" src="flags/${code}.${extension}" width="${width}" height="${height}" alt="${escape(label)}" title="${escape(label)}" draggable="false" decoding="async">`;
  }
  window.fmScoutFlags = {codes:Object.freeze(codes), html};
})();
