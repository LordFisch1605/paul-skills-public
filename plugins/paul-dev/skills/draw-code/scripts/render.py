#!/usr/bin/env python3
"""Render a drawing spec (JSON) into one self-contained HTML file.

    python render.py spec.json --out docs/what-step-does.html

Two modes, chosen by the spec's "mode" field:

  flow   a storyboard of one execution path: numbered panels, what goes in and
         what comes out of each, plus an optional zoom into one step.
  class  a browsable method reference: signatures, line ranges, call edges.

The output has no build step and no dependencies. It pulls two webfonts from
Google Fonts when online and falls back to system faces when not.

Stdlib only.
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

CSS = """
:root{--ink:#14110f;--ink-2:#4a433d;--ink-3:#8a817a;--ground:#faf9f7;--surface:#fff;
--line:#e3dfd9;--red:#d7263d;--orange:#e8710a;--blue:#2a6dd0;--green:#2f7d4f}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
--ink:#f2efea;--ink-2:#b8b0a7;--ink-3:#7e766e;--ground:#14120f;--surface:#1d1a16;
--line:#332e28;--red:#ff7a8a;--orange:#ffa54d;--blue:#7fb0f5;--green:#6fc08d}}
:root[data-theme="dark"]{--ink:#f2efea;--ink-2:#b8b0a7;--ink-3:#7e766e;--ground:#14120f;
--surface:#1d1a16;--line:#332e28;--red:#ff7a8a;--orange:#ffa54d;--blue:#7fb0f5;--green:#6fc08d}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
font:400 16px/1.6 "IBM Plex Sans",system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1020px;margin:0 auto;padding-inline:20px;padding-block:0 64px}
code,.mono{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.88em}
header{padding-block:48px 32px;border-bottom:1px solid var(--line)}
h1{font:400 clamp(30px,5.5vw,46px)/1.06 "Instrument Serif",Georgia,serif;margin:0 0 12px;
text-wrap:balance;letter-spacing:-.01em}
.sub{color:var(--ink-2);max-width:64ch;margin:0}
.eyebrow{font:500 12px/1 "IBM Plex Sans",sans-serif;letter-spacing:.14em;text-transform:uppercase;
color:var(--ink-3);margin:0 0 16px}
.facts{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px}
.fact{font:500 12px/1 "IBM Plex Mono",monospace;padding:7px 10px;border:1px solid var(--line);
border-radius:3px;color:var(--ink-2);background:var(--surface)}
.fact b{color:var(--ink);font-weight:500}
.prov{margin-top:20px;padding:12px 15px;border-radius:4px;font-size:13.5px;
border:1px solid var(--line);background:var(--surface);color:var(--ink-2)}
.prov.read{border-left:3px solid var(--orange)}
.prov.parsed{border-left:3px solid var(--green)}
.prov b{color:var(--ink)}
main{padding-block:36px}
.paper{background:#fff;border:1px solid #e3dfd9;border-radius:4px;overflow-x:auto;padding:4px}
.paper svg{display:block;min-width:680px;width:100%;height:auto}
.drill{display:grid;grid-template-columns:214px 1fr;gap:0;min-height:340px}
@media (max-width:640px){.drill{grid-template-columns:1fr}}
.drill-col{padding:16px;border-right:1px solid #e3dfd9}
@media (max-width:640px){.drill-col{border-right:0;border-bottom:1px solid #e3dfd9}}
.drill-col h4{font:500 10px/1 "IBM Plex Sans",sans-serif;letter-spacing:.13em;
text-transform:uppercase;color:#8a817a;margin:0 0 10px}
.chip{display:block;width:100%;text-align:left;cursor:pointer;margin-bottom:3px;
font-family:"IBM Plex Mono",monospace;font-size:12.5px;color:#14110f;background:transparent;
border:1px solid transparent;border-radius:3px;padding:5px 8px}
.chip:hover{background:#f4f1ec}
.chip[aria-pressed="true"]{background:#14110f;color:#fff;border-color:#14110f}
.chip:focus-visible{outline:2px solid #2a6dd0;outline-offset:1px}
.detail{padding:18px 20px;color:#14110f}
.detail h5{font:600 15px/1.3 "IBM Plex Sans",sans-serif;margin:0 0 3px}
.detail .sig{font-family:"IBM Plex Mono",monospace;font-size:12px;color:#8a817a;margin:0 0 14px}
.detail .row{display:flex;gap:10px;padding:5px 0;border-top:1px dotted #e3dfd9;font-size:13.5px}
.detail .row > span:first-child{font:500 10px/1.5 "IBM Plex Sans",sans-serif;letter-spacing:.1em;
text-transform:uppercase;color:#8a817a;min-width:62px}
.calls{display:flex;flex-wrap:wrap;gap:5px;margin-top:3px}
.calls code{background:#f4f1ec;padding:2px 6px;border-radius:3px;font-size:11.5px;color:#14110f}
.calls .none{color:#8a817a;font-style:italic;font-size:12.5px}
.calls code.ext{background:#fff;border:1px dashed #cfc8c0}
.hint{font-size:13px;color:#4a433d;margin:0;font-style:italic}
.detail .row > span:first-child em{display:block;font-style:normal;letter-spacing:.06em;
color:#b3a99f;font-size:9px}
.calls .none{max-width:44ch}
footer{padding-block:28px 0;border-top:1px solid var(--line);color:var(--ink-3);font-size:13px}
footer code{color:var(--ink-2)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
"""

KIT = """
const NS="http://www.w3.org/2000/svg";
const INK="#14110f",RED="#d7263d",ORANGE="#e8710a",BLUE="#2a6dd0",GREY="#8a817a";
let seed=987123;
const rnd=()=>(seed=(seed*1664525+1013904223)%4294967296)/4294967296;
const j=a=>(rnd()-.5)*2*a;
const el=(n,at,p)=>{const e=document.createElementNS(NS,n);
  for(const k in at)e.setAttribute(k,at[k]);if(p)p.appendChild(e);return e};
function wobble(pts,amp=1.7){const s=[];
  for(let i=0;i<pts.length-1;i++){const[x1,y1]=pts[i],[x2,y2]=pts[i+1];
    const st=Math.max(2,Math.round(Math.hypot(x2-x1,y2-y1)/16));
    for(let k=0;k<=st;k++){const t=k/st;
      s.push([x1+(x2-x1)*t+j(amp),y1+(y2-y1)*t+j(amp)])}}
  let d=`M ${s[0][0].toFixed(1)} ${s[0][1].toFixed(1)}`;
  for(let i=1;i<s.length-1;i++){const[cx,cy]=s[i],[nx,ny]=s[i+1];
    d+=` Q ${cx.toFixed(1)} ${cy.toFixed(1)} ${((cx+nx)/2).toFixed(1)} ${((cy+ny)/2).toFixed(1)}`}
  return d}
const stroke=(p,pts,o={})=>{for(let k=0;k<(o.passes||2);k++)
  el("path",{d:wobble(pts,o.amp??1.7),fill:"none",stroke:o.color||INK,
    "stroke-width":o.w||1.9,"stroke-linecap":"round",
    ...(o.dash?{"stroke-dasharray":o.dash}:{})},p)};
const box=(p,x,y,w,h,o={})=>stroke(p,[[x,y],[x+w,y],[x+w,y+h],[x,y+h],[x,y]],{amp:1.5,...o});
function arrow(p,pts,color=INK,dash=null){
  stroke(p,pts,{color,w:1.9,passes:1,amp:1.3,dash});
  const[ax,ay]=pts[pts.length-2],[bx,by]=pts[pts.length-1];
  const a=Math.atan2(by-ay,bx-ax),L=9,S=.42;
  el("path",{d:`M ${bx} ${by} L ${bx-L*Math.cos(a-S)} ${by-L*Math.sin(a-S)}
    M ${bx} ${by} L ${bx-L*Math.cos(a+S)} ${by-L*Math.sin(a+S)}`,
    fill:"none",stroke:color,"stroke-width":1.9,"stroke-linecap":"round"},p)}
const txt=(p,x,y,s,o={})=>{const t=el("text",{x,y,fill:o.color||INK,
  "text-anchor":o.anchor||"middle",
  "font-family":o.mono?"'IBM Plex Mono', monospace":"Caveat, cursive",
  "font-size":o.size||17,...(o.weight?{"font-weight":o.weight}:{})},p);
  t.textContent=s;return t};
function worker(p,cx,cy,s=1){const pts=[];
  for(let a=0;a<360;a+=15){const r=a*Math.PI/180;
    pts.push(`${(cx+Math.cos(r)*13*s*(1+j(.07))).toFixed(1)},${(cy+Math.sin(r)*16*s*(1+j(.07))).toFixed(1)}`)}
  el("path",{d:`M ${pts.join(" L ")} Z`,fill:INK},p);
  el("circle",{cx:cx-4.4*s,cy:cy-3.4*s,r:2.3*s,fill:"#fff"},p);
  el("circle",{cx:cx+4.4*s,cy:cy-3.4*s,r:2.3*s,fill:"#fff"},p);
  stroke(p,[[cx-5*s,cy+15*s],[cx-6*s,cy+25*s]],{w:2.1*s,passes:1,amp:.5});
  stroke(p,[[cx+5*s,cy+15*s],[cx+6.5*s,cy+25*s]],{w:2.1*s,passes:1,amp:.5})}
const clip=(s,n)=>s&&s.length>n?s.slice(0,n-1)+"\\u2026":s||"";
"""

FLOW_JS = """
(function(){
  const S=SPEC, p=document.getElementById("story"); if(!p) return;
  const W=232,H=136,COLS=4,X0=14,GX=248,GY=196,Y0=46;
  const steps=S.steps||[], rows=Math.ceil(steps.length/COLS)||1;
  const gates=(S.zoom&&S.zoom.gates)||[];
  const storyBottom=Y0+(rows-1)*GY+H;
  let total=storyBottom+30;
  const GW=276,GH=104,GY0=storyBottom+120;
  if(gates.length) total=GY0+GH+(gates.some(g=>g.exit)?86:24)+40;
  p.setAttribute("viewBox",`0 0 1020 ${Math.round(total)}`);

  txt(p,14,26,clip(S.flowLabel||"one call",64),{anchor:"start",size:22,color:GREY});

  steps.forEach((s,i)=>{
    const col=i%COLS,row=Math.floor(i/COLS);
    const cx=X0+col*GX, cy=Y0+row*GY;
    box(p,cx,cy,W,H);
    el("circle",{cx:cx+20,cy:cy+20,r:12,fill:INK},p);
    txt(p,cx+20,cy+25,String(s.n??i+1),{color:"#fff",size:15,weight:500});
    txt(p,cx+40,cy+26,clip(s.title,18),{anchor:"start",size:20});
    if(s.code) txt(p,cx+14,cy+52,clip(s.code,30),{anchor:"start",mono:1,size:11,weight:500});
    if(s.ref)  txt(p,cx+14,cy+67,clip(s.ref,30),{anchor:"start",mono:1,size:10,color:GREY});
    if(s.in){ arrow(p,[[cx+16,cy+92],[cx+50,cy+92]],ORANGE);
      txt(p,cx+56,cy+97,clip(s.in,24),{anchor:"start",size:15,color:ORANGE}); }
    if(s.out){ arrow(p,[[cx+16,cy+118],[cx+50,cy+118]],BLUE);
      txt(p,cx+56,cy+123,clip(s.out,24),{anchor:"start",size:15,color:BLUE}); }
    const last=i===steps.length-1;
    if(!last&&col<COLS-1) arrow(p,[[cx+W+4,cy+H/2],[cx+GX-6,cy+H/2]],"#3a332d");
    else if(!last) arrow(p,[[cx+W/2,cy+H+4],[cx+W/2,cy+H+22],
      [X0+W/2,cy+H+22],[X0+W/2,cy+GY-6]],"#3a332d");
  });

  if(!gates.length) return;
  // clamp the step to the grid that exists - an out-of-range fromStep used to put the
  // bracket thousands of pixels below the viewBox, attached to nothing
  const zstep=Math.max(1,Math.min(steps.length,S.zoom.fromStep??steps.length));
  const zi=(zstep-1)%COLS, zrow=Math.floor((zstep-1)/COLS);
  const zx=X0+zi*GX, zy=Y0+zrow*GY+H;
  stroke(p,[[zx+20,zy+4],[zx+20,GY0-62],[zx+W-20,GY0-62],[zx+W-20,zy+4]],
    {passes:1,amp:1,dash:"6 5",color:GREY});
  arrow(p,[[zx+W/2,GY0-62],[520,GY0-20]],GREY,"6 5");
  txt(p,700,GY0-38,clip(S.zoom.title||"zoom",42),{anchor:"start",size:19,color:GREY});
  if(S.zoom.ref) txt(p,14,GY0-38,clip(S.zoom.ref,40),{anchor:"start",mono:1,size:11,color:GREY});

  const GXs=[24,372,720];
  gates.slice(0,3).forEach((g,i)=>{
    const cx=GXs[i];
    box(p,cx,GY0,GW,GH);
    el("circle",{cx:cx+22,cy:GY0+24,r:13,fill:INK},p);
    txt(p,cx+22,GY0+29,String(g.n??i+1),{color:"#fff",size:15,weight:500});
    txt(p,cx+44,GY0+30,clip(g.title,16),{anchor:"start",size:21});
    if(g.code) txt(p,cx+16,GY0+60,clip(g.code,32),{anchor:"start",mono:1,size:11,weight:500});
    if(g.exit){ arrow(p,[[cx+GW/2,GY0+GH+2],[cx+GW/2,GY0+GH+34]],RED);
      txt(p,cx+GW/2,GY0+GH+54,clip(g.exit,30),{size:17,color:RED}); }
    else if(g.note) txt(p,cx+16,GY0+82,clip(g.note,34),{anchor:"start",size:15,color:BLUE});
    if(i<Math.min(gates.length,3)-1) arrow(p,[[cx+GW+4,GY0+GH/2],[GXs[i+1]-6,GY0+GH/2]],ORANGE);
  });
  if(S.zoom.footnote) txt(p,200,GY0+GH+96,clip(S.zoom.footnote,46),{color:GREY,size:18});
  worker(p,880,GY0+GH+68,1.05);
  stroke(p,[[893,GY0+GH+60],[918,GY0+GH+40]],{w:2.5,passes:1,amp:.6});
})();
"""

CLASS_JS = """
(function(){
  const S=SPEC, list=document.getElementById("fnlist"), detail=document.getElementById("fndetail");
  if(!list||!detail) return;
  const M=S.methods||[];
  const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const show=i=>{
    const f=M[i];
    list.querySelectorAll(".chip").forEach((c,k)=>c.setAttribute("aria-pressed",String(k===i)));
    const own=(f.calls||[]).map(c=>`<code>${esc(c)}</code>`).join("");
    const ext=(f.callsModule||[]).map(c=>`<code class="ext">${esc(c)}</code>`).join("");
    const body=(own+ext)||`<span class="none">no self-calls or same-file calls found &mdash; calls through another object, via super(), or inherited are not detected</span>`;
    detail.innerHTML =
      `<h5>${esc(f.name)}()</h5><p class="sig">${esc(S.sourceName||S.source||"")} &middot; lines ${esc(f.lines)}</p>`+
      `<div class="row"><span>takes</span><span>${esc(f.takes)||"<em>nothing</em>"}</span></div>`+
      `<div class="row"><span>returns</span><span>${esc(f.returns)||"&mdash;"}</span></div>`+
      `<div class="row"><span>calls</span><span><span class="calls">${body}</span></span></div>`+
      (f.note?`<div class="row"><span>note<em>model</em></span><span class="hint">${esc(f.note)}</span></div>`:"");
  };
  M.forEach((f,i)=>{
    const b=document.createElement("button");
    b.className="chip"; b.type="button"; b.textContent=f.name;
    b.setAttribute("aria-pressed","false");
    b.addEventListener("click",()=>show(i));
    list.appendChild(b);
  });
  let start=M.findIndex(m=>m.name===S.openOn);
  show(start>=0?start:0);
})();
"""


def e(s) -> str:
    return html.escape(str(s if s is not None else ""))


def embed(obj) -> str:
    """JSON for a <script> block.

    json.dumps leaves `<` alone, so a spec string containing `</script>` — entirely
    plausible in a web project's docstrings — would close the block early and break
    every script after it. Escaping the three characters that can start a tag, plus
    the two line separators JS treats as newlines, keeps it valid JSON either way.
    """
    return (json.dumps(obj)
            .replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
            .replace(" ", "\\u2028")
            .replace(" ", "\\u2029"))


def facts_html(spec: dict) -> str:
    facts = spec.get("facts") or []
    if not facts:
        return ""
    items = "".join(f'<span class="fact">{e(f)}</span>' for f in facts)
    return f'<div class="facts">{items}</div>'


def provenance_html(spec: dict, mode: str, mismatch: str = "") -> str:
    """The banner has to describe what this page actually checked, not what the skill can check.

    Flow mode renders no signatures and no call edges, and its step refs are ranges a
    model chose by hand — so the class-mode banner would be a straight lie there.
    """
    if mismatch:
        return ('<p class="prov read"><b>Claimed machine-extracted, and it does not match.</b> '
                f'{e(mismatch)} Treat every line range on this page as unverified.</p>')

    if spec.get("provenance") != "parsed":
        return ('<p class="prov read"><b>Not machine-checked.</b> Line ranges and call edges '
                'here were read by a model and may be wrong. Check anything you are about to '
                'rely on.</p>')

    if mode == "flow":
        return ('<p class="prov read"><b>Written by hand, against a parsed file.</b> The steps, '
                'their order and their line refs were chosen and typed by a model reading the '
                'source &mdash; no parser produced them, and nothing here verifies them. Only '
                'the chips and the file facts came from the extractor.</p>')

    return ('<p class="prov parsed"><b>Machine-extracted.</b> Method line ranges, signatures '
            'and call edges were read off the file\'s syntax tree, not inferred from names. '
            '&ldquo;Calls&rdquo; means direct calls to methods on <code>self</code> and to '
            'functions defined in this same file &mdash; calls through another object, through '
            'a variable holding a function, via <code>super()</code>, or inherited from a base '
            'class are <b>not</b> detected. The <em>note</em> on each method, and the fact chips '
            'above, are written or counted by a model.</p>')


def check_parsed(spec: dict, spec_path: Path) -> str:
    """Re-extract the source and compare, so "parsed" cannot be claimed over typed numbers.

    Returns an empty string when it checks out or cannot be checked, otherwise a sentence
    naming the first mismatch. Only class mode on a readable .py file can be checked.
    """
    if spec.get("provenance") != "parsed" or spec.get("mode", "class") != "class":
        return ""
    src = spec.get("source")
    if not src:
        return ""
    cand = Path(src)
    if not cand.is_file():
        cand = spec_path.parent / src
    if not cand.is_file() or cand.suffix != ".py":
        return ""

    import subprocess
    tool = Path(__file__).with_name("extract_py.py")
    try:
        run = subprocess.run([sys.executable, str(tool), str(cand)],
                             capture_output=True, text=True, timeout=60)
        if run.returncode != 0:
            return ""
        real = json.loads(run.stdout)
    except Exception:
        return ""

    actual = {}
    for c in real.get("classes", []):
        for m in c.get("methods", []):
            actual[m["name"]] = m["lines"]
    for f in real.get("functions", []):
        actual[f["name"]] = f["lines"]
    if not actual:
        return ""

    for m in spec.get("methods") or []:
        name, claimed = m.get("name"), m.get("lines")
        if name in actual and claimed and claimed != actual[name]:
            return (f"{name}() is given as lines {claimed}, but the file says "
                    f"{actual[name]}.")
    return ""


def normalise_methods(spec: dict) -> None:
    """Accept the extractor's {"self":[],"module":[]} call shape as well as flat lists."""
    for m in spec.get("methods") or []:
        c = m.get("calls")
        if isinstance(c, dict):
            m["calls"] = c.get("self") or []
            m.setdefault("callsModule", c.get("module") or [])
        elif c is None:
            m["calls"] = []


def build(spec: dict, mismatch: str = "") -> str:
    mode = spec.get("mode", "class")
    normalise_methods(spec)
    # `source` may be a full path so check_parsed can find the file; show only the name
    if spec.get("source"):
        spec["sourceName"] = Path(spec["source"]).name
    if mode == "flow":
        body = '<div class="paper"><svg id="story" role="img" aria-label="%s"></svg></div>' % e(
            spec.get("title", "execution storyboard"))
        script = KIT + FLOW_JS
    else:
        body = ('<div class="paper"><div class="drill">'
                '<div class="drill-col"><h4>%s</h4><div id="fnlist"></div></div>'
                '<div class="detail" id="fndetail"></div></div></div>') % e(
            spec.get("className") or spec.get("title", "methods"))
        script = CLASS_JS

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(spec.get('title', 'Code drawing'))}</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=Instrument+Serif&display=swap">
<style>{CSS}</style></head>
<body><div class="wrap">
<header>
  <p class="eyebrow">{e(Path(spec['source']).name) if spec.get('source') else ''}{' &middot; ' + e(spec['lines']) + ' lines' if spec.get('lines') else ''}</p>
  <h1>{e(spec.get('title', 'Code drawing'))}</h1>
  <p class="sub">{e(spec.get('subtitle', ''))}</p>
  {provenance_html(spec, mode, mismatch)}
  {facts_html(spec)}
</header>
<main>{body}</main>
<footer>Generated by <code>paul-dev:draw-code</code>. Regenerate it rather than editing it by hand.</footer>
</div>
<script>const SPEC={embed(spec)};</script>
<script>{script}</script>
</body></html>
"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Render a drawing spec into standalone HTML.")
    ap.add_argument("spec", help="the spec JSON file")
    ap.add_argument("--out", required=True, help="where to write the HTML")
    args = ap.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.is_file():
        print(f"not a file: {spec_path}", file=sys.stderr)
        return 2
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    mode = spec.get("mode", "class")
    if mode not in ("flow", "class"):
        print(f'mode must be "flow" or "class", got {mode!r}', file=sys.stderr)
        return 2
    if mode == "flow" and not spec.get("steps"):
        print("flow mode needs a non-empty steps list", file=sys.stderr)
        return 2
    if mode == "class" and not spec.get("methods"):
        print("class mode needs a non-empty methods list", file=sys.stderr)
        return 2

    mismatch = check_parsed(spec, spec_path)
    if mismatch:
        print(f'WARNING: spec claims "parsed" but does not match the source. {mismatch}\n'
              f'         The page now says so. Re-run extract_py.py and rebuild the spec.',
              file=sys.stderr)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(spec, mismatch), encoding="utf-8")
    print(f"wrote {out}  ({mode} mode, {out.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
