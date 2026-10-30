/* XTC · ядро открытого жребия. Один и тот же файл считает итоги в пульте (node) и на странице проверки (браузер).
   Вход — замороженный список «номер билеты» и случайность сети drand, которой на момент заморозки ещё не существовало.
   Выход — порядок номеров: первые десять берут места, дальше запас на случай замены. Без сервера, без Math.random, повторяется у любого. */

const hex = buf => [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
export const sha256 = async text => hex(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text)));

/* список: по строке на участника «0059 11», по возрастанию номера, с переводом строки в конце — этот текст и хешируется */
export const listText = rows => [...rows].sort((a, b) => a.n - b.n).map(r => String(r.n).padStart(4, '0') + ' ' + r.t + '\n').join('');
export const parseList = text => text.split('\n').filter(Boolean).map(l => { const [n, t] = l.split(' '); return { n: Number(n), t: Number(t) }; });

/* раунды drand: основная сеть League of Entropy, новый раунд каждые 30 секунд */
export const DRAND = { chain: '8990e7a9aaed2ffed73dbd7092123d6f289930540d7651336225dc172e51b2ce', genesis: 1595431050, period: 30 };
export const roundAt = round => (DRAND.genesis + (round - 1) * DRAND.period) * 1000;
export const roundAfter = ms => Math.floor((ms / 1000 - DRAND.genesis) / DRAND.period) + 2;   /* первый раунд, который выйдет строго позже ms */

/* один шаг: sha256(«случайность:номер шага») как большое число, остаток от деления на все оставшиеся билеты — выпавший билет */
export async function step(seed, i, pool) {
  const total = pool.reduce((s, r) => s + r.t, 0), h = await sha256(seed + ':' + i);
  let x = BigInt('0x' + h) % BigInt(total), at = 0;
  const ticket = Number(x);
  for (; at < pool.length; at++) { if (x < BigInt(pool[at].t)) break; x -= BigInt(pool[at].t); }
  return { i, hash: h, total, ticket, n: pool[at].n, t: pool[at].t, at };
}

/* порядок из count номеров: выпавший выходит из списка, один человек — одно место */
export async function order(rows, seed, count) {
  const pool = [...rows].sort((a, b) => a.n - b.n), out = [];
  for (let i = 1; i <= count && pool.length; i++) { const s = await step(seed, i, pool); out.push(s); pool.splice(s.at, 1); }
  return out;
}
