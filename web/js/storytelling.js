const stageOrder = ['Anos Iniciais', 'Anos Finais'];

function fmt(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return Number(value).toFixed(digits).replace('.', ',');
}
function formatIdeb(value) { return fmt(value, 1); }
function formatDelta(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  const sign = Number(value) > 0 ? '+' : '';
  return `${sign}${fmt(value, 1)}`;
}
function formatPercent(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  const sign = Number(value) > 0 ? '+' : '';
  return `${sign}${fmt(value, 1)}%`;
}
function formatPosition(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '—';
  return `${Number(value).toFixed(0)}º`;
}
function byStage(data, stage) { return data.find(d => d.etapa === stage); }
function municipalityRows() { return window.IDEB_DATA.municipio; }
function getGap(stage, year) { return window.IDEB_DATA.gaps.find(d => d.etapa === stage && d.ano === year); }
function variationPhrase(row) {
  if (row.variacao_absoluta > 0) return `Rosário avançou ${formatDelta(row.variacao_absoluta)} ponto entre 2023 e 2025.`;
  if (row.variacao_absoluta < 0) return `Rosário recuou ${formatDelta(row.variacao_absoluta)} ponto entre 2023 e 2025.`;
  return 'Rosário manteve estabilidade no período.';
}
function dre4PositionPhrase(row) {
  const change = row.mudanca_posicao_dre4;
  if (change > 0) return `Ganhou ${change} posição${change === 1 ? '' : 'es'} na DRE 4.`;
  if (change < 0) return `Perdeu ${Math.abs(change)} posição${Math.abs(change) === 1 ? '' : 'es'} na DRE 4.`;
  return 'Manteve a posição na DRE 4.';
}
function driverPhrase(row) {
  const perf = Math.abs(row.variacao_desempenho || 0);
  const flow = Math.abs(row.variacao_rendimento || 0);
  if (perf > flow * 2) return 'O crescimento foi impulsionado principalmente pelo desempenho.';
  if (flow > perf * 2) return 'O crescimento foi impulsionado principalmente pelo fluxo.';
  return 'Desempenho e fluxo contribuíram conjuntamente para o resultado.';
}
function gapPhrase(stage) {
  const gap = getGap(stage, 2025);
  const v = gap.gap_sergipe;
  if (v > 0.05) return `Rosário está ${formatDelta(v)} ponto acima da média municipal de Sergipe.`;
  if (v < -0.05) return `Rosário está ${formatDelta(v)} ponto abaixo da média municipal de Sergipe.`;
  return 'Rosário está praticamente em linha com a média municipal de Sergipe.';
}
function positiveHighlights() {
  const rows = municipalityRows();
  const bestStage = [...rows].sort((a,b) => b.variacao_absoluta - a.variacao_absoluta)[0];
  const bestSchool = [...window.IDEB_DATA.escolas].sort((a,b) => b.variacao_absoluta - a.variacao_absoluta)[0];
  return [
    `Maior avanço nos ${bestStage.etapa}: ${formatDelta(bestStage.variacao_absoluta)} ponto.`,
    `Rosário alcançou ${formatPosition(byStage(rows, 'Anos Iniciais').posicao_dre4_2025)} lugar na DRE 4 nos anos iniciais.`,
    `${window.IDEB_DATA.indicadores.escolas_avancaram} de ${window.IDEB_DATA.indicadores.total_escolas_comparaveis} resultados escolares comparáveis avançaram.`,
    `Maior avanço escolar: ${shortSchool(bestSchool.escola)} (${formatDelta(bestSchool.variacao_absoluta)} ponto).`
  ];
}
function attentionPoints() {
  const rows = municipalityRows();
  const points = [];
  rows.forEach(row => {
    if (row.variacao_desempenho < 0) points.push(`${row.etapa}: desempenho recuou no período.`);
    if (row.variacao_rendimento < 0) points.push(`${row.etapa}: fluxo/rendimento recuou no período.`);
    if (row.ideb_2025 < 4.5) points.push(`${row.etapa}: IDEB 2025 ainda exige acompanhamento.`);
  });
  if (window.IDEB_DATA.indicadores.escolas_recuaram > 0) points.push(`${window.IDEB_DATA.indicadores.escolas_recuaram} resultados escolares recuaram.`);
  if (!points.length) points.push('Não há recuo de IDEB nos resultados comparáveis; o foco passa a ser sustentar ganhos e reduzir desigualdades internas.');
  return points.slice(0,3);
}
function priorities() {
  const weak = window.IDEB_DATA.indicadores.menor_ideb_2025_etapa;
  return [
    `Intensificar acompanhamento dos ${weak.etapa}, etapa com menor IDEB 2025.`,
    'Monitorar aprendizagem e fluxo conjuntamente em cada ciclo.',
    'Disseminar práticas das escolas com maior crescimento.',
    'Apoiar escolas com menor IDEB relativo, mesmo quando houve avanço.'
  ];
}
function shortSchool(name) {
  return String(name).replaceAll('ESCOLA-MUNICIPAL-', 'EM ').replaceAll('ESCOLA MUNICIPAL ', 'EM ').replaceAll('ESCOLA-MUL-', 'EM ').replaceAll('-', ' ').replace(/\s+/g, ' ').trim();
}
function animateNumber(el) {
  const target = Number(el.dataset.value);
  if (Number.isNaN(target)) return;
  const digits = Number(el.dataset.digits || 1);
  const prefix = el.dataset.prefix || '';
  const suffix = el.dataset.suffix || '';
  const start = performance.now();
  const duration = 800;
  function step(now) {
    const t = Math.min(1, (now - start) / duration);
    const eased = 1 - Math.pow(1 - t, 3);
    el.textContent = prefix + fmt(target * eased, digits) + suffix;
    if (t < 1) requestAnimationFrame(step);
  }
  requestAnimationFrame(step);
}
