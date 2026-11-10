"""Assembles the redesigned page: new markup + the app script (patched) + logo A."""
import json, re, sys, pathlib, urllib.parse
root = pathlib.Path(sys.argv[1])
old = (root / "build/index.src.html").read_text()
script = old[old.index("<script>") + len("<script>"): old.rindex("</script>")]

def rep(a, b, count=1):
    global script
    assert a in script, "missing: " + a[:70]
    script = script.replace(a, b) if count == 0 else script.replace(a, b, count)

rep('t: `En retard · ${d} j`', 't: `En retard (${d} j)`')
rep('${hideB ? "Lot" : "Immeuble · lot"}', '${hideB ? "Lot" : "Immeuble et lot"}')
rep('${hideB ? "" : esc(short(x.b)) + " · "}', '${hideB ? "Lot " : esc(short(x.b)) + ", lot "}')
rep('>Rappel</button>', '>Relancer</button>')
rep('<span>En retard · ${late.length} paiement${late.length > 1 ? "s" : ""}</span>', '<span>En retard (${late.length} paiement${late.length > 1 ? "s" : ""})</span>')
rep('<span>Solde · ${esc(short(b))}</span>', '<span>Solde, ${esc(short(b))}</span>')
rep('Répartition · ${esc(sel.fournisseur)} · ${fdate(sel.date)}', 'Répartition : ${esc(sel.fournisseur)}, ${fdate(sel.date)}')
rep('<h3>Factures · ${esc(short(b))}</h3>', '<h3>Factures enregistrées</h3>')
rep('<h3>${esc(sel.periode)} · ${esc(short(b))}</h3>', '<h3>${esc(sel.periode)}</h3>')
rep('<h3>Nouvel appel de fonds · ${esc(short(b))}</h3>', '<h3>Nouvel appel de fonds</h3>')
rep('Échéance ${fdate(a.echeance)} · ${paid.length}/${a.lines.length} payés', 'Échéance le ${fdate(a.echeance)}, ${paid.length} sur ${a.lines.length} payés')
rep('${lab[k]} · ${g[k].length}', '${lab[k]} (${g[k].length})')
rep('${b.lots.length} lots · ${m} ‰', '${b.lots.length} lots, ${m} ‰')
rep('Total des quotes-parts : ${m} / 1000 ‰ · ', 'Total des quotes-parts : ${m} / 1000 ‰, ')
rep('immeuble${acc.buildings.length > 1 ? "s" : ""} · ${lotsOf(acc)} lots', 'immeuble${acc.buildings.length > 1 ? "s" : ""}, ${lotsOf(acc)} lots')
rep('<a href="#apercu">Aperçu</a>', '')

# graduated reminders (rappel amiable, second rappel, mise en demeure)
start = script.index("function openReminder(")
end = script.index("const closeModal")
script = script[:start] + r'''let remCtx = null;
function levelFor(d) { return d > 60 ? "demeure" : d > 30 ? "second" : "amiable"; }
function reminderText(level) {
  const { acc, b, a, line, lot } = remCtx, br = acc.brand || {};
  const who = lot ? lot.proprietaire : "", num = lot ? lot.numero : "";
  const ref = `${b.nom}, lot ${num}, ${a.periode}`;
  const late = Math.max(0, days(a.echeance, TODAY));
  const sig = [acc.nom, acc.cabinet, br.adresse, [acc.tel, br.emailContact].filter(Boolean).join(" – ")].filter(Boolean).join("\n");
  const pay = br.iban ? `sur le compte ${br.iban} au nom de ${acc.cabinet}, avec la référence « ${ref} »` : `avec la référence « ${ref} »`;
  const what = `l'appel de fonds « ${a.periode} » de la ${b.nom} (lot ${num}), d'un montant de ${eur(line.montant)}`;
  if (level === "demeure") return `À l'attention de ${who}\n\nObjet : mise en demeure de payer\n\nMadame, Monsieur,\n\nMalgré nos précédents rappels, ${what}, échu le ${fdate(a.echeance)}, reste impayé à ce jour (${late} jours de retard).\n\nPar la présente, nous vous mettons en demeure de régler cette somme dans un délai de 8 jours à compter de la réception de ce courrier, par virement ${pay}.\n\nÀ défaut de paiement dans ce délai, le syndicat des copropriétaires se réserve le droit d'engager une procédure de recouvrement.\n\nVeuillez agréer, Madame, Monsieur, nos salutations distinguées.\n\n${sig}`;
  if (level === "second") return `Bonjour ${who},\n\nMalgré notre premier rappel, nous n'avons pas encore reçu le paiement de ${what}, échu le ${fdate(a.echeance)} (${late} jours de retard).\n\nNous vous remercions de régler ce montant dans un délai de 15 jours, par virement ${pay}.\n\nSi le paiement a été fait entre-temps, merci de ne pas tenir compte de ce message.\n\nCordialement,\n${sig}`;
  return `Bonjour ${who},\n\nSauf erreur de notre part, ${what} était à régler le ${fdate(a.echeance)}.\n\nMerci d'effectuer le virement ${pay}.\n\nSi le paiement a été fait entre-temps, merci de ne pas tenir compte de ce message.\n\nCordialement,\n${sig}`;
}
function openReminder(acc, aId, lotId) {
  const { b, a, line } = findLine(acc, aId, lotId); if (!line) return;
  remCtx = { acc, b, a, line, lot: b.lots.find(l => l.id === lotId) };
  const lv = levelFor(status(a, line).d || 0);
  $("#rem-level").value = lv; $("#rem-text").value = reminderText(lv);
  $("#modal").hidden = false; $("#rem-level").focus();
}
$("#rem-level").addEventListener("change", e => { if (remCtx) $("#rem-text").value = reminderText(e.target.value); });
''' + script[end:]

# screenshots: full app or content only, any width
start = script.index("function shotHTML(")
end = script.index('$$("[data-tour]")')
script = script[:start] + r'''function shotHTML(acc, st, solo, w, mobile) {
  const saved = ui; ui = { ...UI0, ...st };
  try {
    const bv = brandVars(acc.brand.color);
    return `<div class="shot-inner" inert aria-hidden="true" style="width:${w}px">` + (solo
      ? `<div class="app-solo" style="${bv}"><section class="work">${VIEWS[ui.tab](acc)}</section></div>`
      : `<div class="app${mobile ? " m" : ""}" style="${bv}">${appInner(acc)}</div>`) + `</div>`;
  } finally { ui = saved; }
}
function buildShots() {
  const A = demoAccount("");
  const t = A.buildings[0], ass = t.depenses.find(d => d.categorie === "Assurance");
  const map = { dashboard: [A, { tab: "dashboard" }], mobile: [A, { tab: "dashboard" }, true], depenses: [A, { tab: "depenses", depB: t.id, depSel: ass.id }], appels: [A, { tab: "appels", apB: t.id }], paiements: [A, { tab: "paiements", filter: "retard" }], fonds: [A, { tab: "fonds", fB: t.id }], cabinet: [A, { tab: "cabinet" }] };
  $$(".shot-vp").forEach(vp => { const m = map[vp.dataset.shot]; if (m) vp.innerHTML = shotHTML(m[0], m[1], vp.dataset.solo === "1", +vp.dataset.w || 1180, !!m[2]); });
  const fit = vp => { const w = vp.clientWidth, inner = vp.firstElementChild; if (!w || !inner) return; const W = +vp.dataset.w || 1180, H = +vp.dataset.h || 740, s = w / W; inner.style.transform = `scale(${s})`; vp.style.height = Math.round(H * s) + "px"; };
  if ("ResizeObserver" in window) { const ro = new ResizeObserver(es => es.forEach(e => fit(e.target))); $$(".shot-vp").forEach(vp => ro.observe(vp)); }
  window.addEventListener("resize", () => $$(".shot-vp").forEach(fit));
  $$(".shot-vp").forEach(fit);
}
''' + script[end:]


rep('color: "#2F5E93", logo: null, adresse: "10, rue', 'color: "#1D3FE0", logo: null, adresse: "10, rue')
rep('const COLORS = ["#2F5E93",', 'const COLORS = ["#1D3FE0",')
rep('const SECTIONS = ["accueil", "excel", "apercu", "fonctions", "prix", "fonctionnement", "faq"];', 'const SECTIONS = ["accueil", "produit", "essayer", "pour-qui", "comparer", "prix", "faq", "contact"];')
rep('if (e.target.closest("[data-demo]")) openApp(DEMO_EMAIL);', 'const dm = e.target.closest("[data-demo]"); if (dm) { openApp(DEMO_EMAIL); if (dm.dataset.demoTab) { ui.tab = dm.dataset.demoTab; if (location.hash === "#app") renderApp(); } }')
rep('root.setAttribute("style", brandVars(acc.brand && acc.brand.color));', 'root.setAttribute("style", brandVars(acc.brand && acc.brand.color)); root.classList.toggle("m", MQ.matches);')
rep('function renderApp() {', 'const MQ = window.matchMedia("(max-width: 860px)");\nif (MQ.addEventListener) MQ.addEventListener("change", () => { if (document.body.dataset.view === "app") renderApp(); });\nfunction renderApp() {')
start = script.index("function renderHeader(view) {")
end = script.index("const SECTIONS")
script = script[:start] + r"""function renderHeader(view) {
  const nav = $("#top-nav"), acc = currentAccount();
  if (view === "app" && acc) { nav.innerHTML = `<span class="top-cab" style="${brandVars(acc.brand && acc.brand.color)}">${cabMark(acc, "sm")}<span>${esc(acc.cabinet)}</span></span><button class="btn btn-sm btn-line" type="button" data-logout>Déconnexion</button>`; return; }
  nav.innerHTML = `<nav class="top-links" aria-label="Sections"><a href="#produit">Produit</a><a href="#pour-qui">Pour qui</a><a href="#prix">Prix</a><a href="#faq">FAQ</a></nav><div class="top-actions">${acc ? `<a class="top-login" href="#app">Mon espace</a>` : `<a class="top-login" href="#connexion">Se connecter</a>`}<a class="btn btn-sm btn-blue" href="#inscription">Créer mon espace</a></div>`;
}
""" + script[end:]

markup = (root / "build/v3.markup.html").read_text()
logo = json.loads((root / "out/logo4/logo4_inline.json").read_text())
fav = "data:image/svg+xml," + urllib.parse.quote(logo["favicon"])
html = markup.replace("{{SCRIPT}}", script.strip()).replace("{{LOGO}}", logo["inline"]).replace("{{FAVICON}}", fav)
assert "{{" not in html.replace("${", "")
(root / "out/index.html").write_text(html)
print("bytes", len(html.encode()))
