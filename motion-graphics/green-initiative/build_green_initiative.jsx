/*  مبادرة السعودية الخضراء — Motion Graphics builder for Adobe After Effects  (v2 — 3D camera)
    ------------------------------------------------------------------------------------------
    Run:  File > Scripts > Run Script File…  and pick this file.
    Keep it in its folder, next to:
        layers/S01_L0.jpg, S01_L1.png, S01_L2.png …   depth layers (far / mid / near) per scene
        assets/tree1.png … tree3.png                   tree cut-outs
        audio/vo.mp3                                   voice-over
        assets/crown_prince.png   (optional) official photo — placeholder if missing
        assets/saudi_flag.png     (optional) official flag  — placeholder if missing
        ../channel-guide/safe-area-guide.png           guide layer (never renders)

    Each scene: real 3D camera move through 3 depth layers + floating particles + light + HUD lines.
    Captions are 2D (stay sharp and steady), right-aligned inside the channel safe area.
    On-screen text = the script's call-ups, word for word.
    Problems are written to build_log.txt next to this file.
*/
(function () {

// ───────────────────────────── CONFIG ─────────────────────────────
var CFG = {
    W: 1920, H: 1080, FPS: 25,
    // Scene starts (seconds in vo.mp3) — taken from the transcript of the VO.
    T: {
        S01: 0.00,    // "من خطط على ورق إلى زراعة ملايين الأشجار"
        S02: 5.62,    // "تقود المملكة… أطلقها ولي العهد… عام 2021 بعنوان مبادرة السعودية الخضراء"
        S03: 18.41,   // "تلك المبادرة تهدف إلى التصدي…"
        S04: 24.41,   // "وتضع نصب أعينها ثلاثة أهداف… الاقتصاد الأخضر"
        S05: 32.07,   // "وتقليل الانبعاثات الكربونية… 2060"
        S06: 38.46,   // "والتوسع في التشجير…"
        S07: 43.12,   // "ولأن الالتزامات… 700 مليار ريال"
        S08: 52.40,   // "تُرجمت إلى 77 برنامجاً…"
        S09: 61.85,   // "واليوم… 100 مليون شجرة… 118 ألف هكتار"
        S10: 75.37,   // "مع تنفيذ أكثر من 1150 مسحاً…"
        S11: 88.50,   // "هذه الجهود… 2.2 درجة مئوية"
        S12: 103.08   // "لترسخ المملكة…"
    },
    END_PAD: 1.0,
    ORANGE: [1, 0x60 / 255, 0],                   // #FF6000
    GREY:   [0x3C / 255, 0x3C / 255, 0x3C / 255], // #3C3C3C
    WHITE:  [1, 1, 1],
    FONT: { Black: "", Bold: "", Regular: "" },   // leave "" to auto-detect, or type PostScript names
    FONT_FAMILY_MATCH: /bloomberg|neue ?haas|neuehaas/i,
    XR: 1790,
    // Measured on AE 2026 screenshots: text renders shifted RIGHT by half its own width compared with
    // what sourceRectAtTime() reports at build time. The builder compensates by this fraction of the width.
    // If text ever sits too far LEFT on another AE version, set this to 0.
    TEXT_SHIFT: 0,
    SKETCH_T0: 0.15,
    // one caption system for every scene: sizes (px) and baselines (y) of the right-hand block
    TY: { TAG: 50, HEAD: 80, LABEL: 58, NUM: 180, NUM2: 140, UNIT: 70, UNIT2: 60, TITLE: 116 },
    Y:  { TAG: 300, HEAD: 430, LABEL: 425, NUM: 615, LABEL2: 715, NUM2: 860 },
    // section changes get the orange wipe; cuts inside a section are whip-pans across the table
    SECTION_CUTS: { S04: 1, S07: 1, S09: 1, S11: 1, S12: 1 },          // captions right edge (safe area)
    WIPE: 0.5,
    DEPTH: [1800, 900, 300],   // z of far / mid / near layers
    PARTICLES: 28
};

var LOG = [], DIAG = [], SFXQ = [], SFX_ALL = [], CUR = "S01";
var ORDER = ["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12"];
var ROOT = File($.fileName).parent;

// ───────────────────────────── HELPERS ─────────────────────────────
function f(rel) { return new File(ROOT.fsName + "/" + rel); }
function importIfExists(rel, folderItem) {
    var file = f(rel);
    if (!file.exists) return null;
    try {
        var it = app.project.importFile(new ImportOptions(file));
        if (folderItem) it.parentFolder = folderItem;
        return it;
    } catch (e) { LOG.push("import " + rel + ": " + e.toString()); return null; }
}

var fontCache = {};
function font(style) {
    if (fontCache[style]) return fontCache[style];
    var ps = CFG.FONT[style];
    if (!ps) {
        try {
            var all = app.fonts.allFonts;
            for (var i = 0; i < all.length && !ps; i++)
                for (var j = 0; j < all[i].length; j++) {
                    var fo = all[i][j];
                    if (!CFG.FONT_FAMILY_MATCH.test(fo.familyName + " " + fo.postScriptName)) continue;
                    var sn = (fo.styleName || "").toLowerCase();
                    var ok = (style === "Regular") ? /^(regular|roman|book|normal|text)$/.test(sn) : sn === style.toLowerCase();
                    if (ok && !/italic|oblique/.test(sn)) { ps = fo.postScriptName; break; }
                }
        } catch (e) {}
    }
    if (!ps) ps = "NeueHaasBloomberg-" + style;
    fontCache[style] = ps;
    return ps;
}

function easeKeys(prop, inf) {
    inf = inf || 80;
    var n = 1, t = prop.propertyValueType;
    if (t !== PropertyValueType.TwoD_SPATIAL && t !== PropertyValueType.ThreeD_SPATIAL &&
        t !== PropertyValueType.SHAPE && t !== PropertyValueType.OneD) {
        try { n = prop.value.length || 1; } catch (e) { n = 1; }
    }
    var arr = []; for (var k = 0; k < n; k++) arr.push(new KeyframeEase(0, inf));
    for (var i = 1; i <= prop.numKeys; i++) { try { prop.setTemporalEaseAtKey(i, arr, arr); } catch (e) {} }
}
function keys(prop, times, values, inf) {
    for (var i = 0; i < times.length; i++) prop.setValueAtTime(times[i], values[i]);
    easeKeys(prop, inf);
}
function tr(layer) { return layer.property("ADBE Transform Group"); }
function P(layer) { return tr(layer).property("ADBE Position"); }

// Keeps the chosen edge of the REAL text box on the layer's position, whatever the
// paragraph direction / justification does.  side: "r" | "c" | "l"
function edgeExpr(side) {
    return 'var b=sourceRectAtTime(time,false);var e=' +
        (side === "r" ? 'b.left+b.width' : side === "c" ? 'b.left+b.width/2' : 'b.left') + ';';
}

// Text layer. rtl=false for stand-alone numbers (keeps "-2.2" correct).
// Every caption is point text whose ANCHOR is computed live by After Effects at render time
// (sourceRectAtTime inside an expression): the anchor sits on the right edge (side r), centre (c)
// or left edge (l) of the real rendered glyphs, on the first baseline (y = 0). The layer position
// is then simply [edge x, baseline y]. Nothing is measured at build time.
// The expression only uses JS-engine-safe syntax (no array + array).
function anchorExpr(side) {
    return 'var r=sourceRectAtTime(time,false);[' +
        (side === "r" ? 'r.left+r.width' : side === "c" ? 'r.left+r.width/2' : 'r.left') + ',0]';
}
function text(comp, name, str, o) {
    var size = o.size || 60, side = o.side || "r";
    var l = comp.layers.addText(str);
    l.name = name;
    var p = l.property("ADBE Text Properties").property("ADBE Text Document");
    var td = p.value;
    try { td.resetCharStyle(); td.resetParagraphStyle(); } catch (e) {}
    td.text = str;
    try { td.font = font(o.w || "Bold"); } catch (e) { LOG.push(name + ": font " + font(o.w || "Bold") + " not found"); }
    td.fontSize = size;
    td.applyFill = true; td.fillColor = o.color || CFG.WHITE;
    td.applyStroke = false;
    td.justification = side === "c" ? ParagraphJustification.CENTER_JUSTIFY :
                       side === "l" ? ParagraphJustification.LEFT_JUSTIFY : ParagraphJustification.RIGHT_JUSTIFY;
    try { td.composerEngine = ComposerEngine.UNIVERSAL_TYPE_ENGINE; } catch (e) {}
    try { td.direction = (o.rtl === false) ? ParagraphDirection.DIRECTION_LEFT_TO_RIGHT : ParagraphDirection.DIRECTION_RIGHT_TO_LEFT; } catch (e) {}
    try { td.digitSet = DigitSet.ARABIC_DIGITS; } catch (e) {}   // 0-9, never ٠-٩
    try { td.autoLeading = false; td.leading = Math.round(size * 1.28); } catch (e) {}
    p.setValue(td);
    tr(l).property("ADBE Anchor Point").expression = anchorExpr(side);
    P(l).setValue([o.pos[0], o.pos[1]]);
    if (o.shadow !== false) shadow(l, o.shadowOp || 50);
    return l;
}

function shadow(l, op) {
    try {
        var fx = l.property("ADBE Effect Parade");
        fx.addProperty("ADBE Drop Shadow");
        var d = l.property("ADBE Effect Parade").property(l.property("ADBE Effect Parade").numProperties);
        d.property("ADBE Drop Shadow-0001").setValue([0, 0, 0, 1]);
        d.property("ADBE Drop Shadow-0002").setValue(op * 2.55);
        d.property("ADBE Drop Shadow-0003").setValue(135);
        d.property("ADBE Drop Shadow-0004").setValue(4);
        d.property("ADBE Drop Shadow-0005").setValue(22);
    } catch (e) {}
}

// Word-by-word reveal (keeps Arabic letters joined). All references re-fetched.
function revealWords(l, t0, dur, dy) {
    try {
        var AN = function () { return l.property("ADBE Text Properties").property("ADBE Text Animators"); };
        AN().addProperty("ADBE Text Animator");
        var ai = AN().numProperties;
        var A = function () { return AN().property(ai); };
        var PR = function () { return A().property("ADBE Text Animator Properties"); };
        PR().addProperty("ADBE Text Opacity");
        PR().property("ADBE Text Opacity").setValue(0);
        PR().addProperty("ADBE Text Position 3D");
        PR().property("ADBE Text Position 3D").setValue([0, dy === undefined ? 40 : dy, 0]);
        try { PR().addProperty("ADBE Text Blur"); PR().property("ADBE Text Blur").setValue([10, 10]); } catch (e) {}
        A().property("ADBE Text Selectors").addProperty("ADBE Text Selector");
        var adv = A().property("ADBE Text Selectors").property(1).property("ADBE Text Range Advanced");
        try { adv.property("ADBE Text Range Type2").setValue(3); } catch (e) {}   // words
        try { A().property("ADBE Text Selectors").property(1).property("ADBE Text Range Advanced").property("ADBE Text Range Shape").setValue(2); } catch (e) {}
        keys(A().property("ADBE Text Selectors").property(1).property("ADBE Text Percent Offset"), [t0, t0 + dur], [0, 100], 70);
    } catch (e) { LOG.push(l.name + ": reveal — " + e.toString()); fadeIn(l, t0, dur * 0.6); }
}

function fadeIn(l, t0, dur, from) {
    keys(tr(l).property("ADBE Opacity"), [t0, t0 + dur], [0, 100]);
    if (from) {
        var v = P(l).value;
        var a = v.length === 3 ? [v[0] + from[0], v[1] + from[1], v[2]] : [v[0] + from[0], v[1] + from[1]];
        keys(P(l), [t0, t0 + dur + 0.25], [a, v], 85);
    }
}

// ── shape helpers (always re-fetch: AE invalidates references after addProperty) ──
function contents(l) { return l.property("ADBE Root Vectors Group"); }
function grp(l, name) { return contents(l).property(name); }
function items(l, name) { return grp(l, name).property("ADBE Vectors Group"); }
function last(l, name) { return items(l, name).property(items(l, name).numProperties); }
function newGroup(l, name) { contents(l).addProperty("ADBE Vector Group"); contents(l).property(contents(l).numProperties).name = name; return name; }
function addItem(l, name, matchName) { items(l, name).addProperty(matchName); return last(l, name); }
function fill(l, name, color, op) {
    addItem(l, name, "ADBE Vector Graphic - Fill");
    last(l, name).property("ADBE Vector Fill Color").setValue(color);
    if (op !== undefined) last(l, name).property("ADBE Vector Fill Opacity").setValue(op);
}
function stroke(l, name, color, w) {
    addItem(l, name, "ADBE Vector Graphic - Stroke");
    last(l, name).property("ADBE Vector Stroke Color").setValue(color);
    last(l, name).property("ADBE Vector Stroke Width").setValue(w);
    try { last(l, name).property("ADBE Vector Stroke Line Cap").setValue(2); last(l, name).property("ADBE Vector Stroke Line Join").setValue(2); } catch (e) {}
}
function pathShape(verts, closed) { var s = new Shape(); s.vertices = verts; s.closed = closed !== false; return s; }
function path(l, name, verts, closed) { addItem(l, name, "ADBE Vector Shape - Group"); last(l, name).property("ADBE Vector Shape").setValue(pathShape(verts, closed)); }
function ellipse(l, name, size, pos) {
    addItem(l, name, "ADBE Vector Shape - Ellipse");
    last(l, name).property("ADBE Vector Ellipse Size").setValue(size);
    if (pos) last(l, name).property("ADBE Vector Ellipse Position").setValue(pos);
}
function rectItem(l, name, size, pos, round) {
    addItem(l, name, "ADBE Vector Shape - Rect");
    last(l, name).property("ADBE Vector Rect Size").setValue(size);
    if (pos) last(l, name).property("ADBE Vector Rect Position").setValue(pos);
    if (round) last(l, name).property("ADBE Vector Rect Roundness").setValue(round);
}
function trimIn(l, name, t0, dur) {
    addItem(l, name, "ADBE Vector Filter - Trim");
    keys(last(l, name).property("ADBE Vector Trim End"), [t0, t0 + dur], [0, 100], 75);
}

// Rectangle whose layer origin is its RIGHT-middle edge (scale-X reveals right→left).
function rectR(comp, name, w, h, color, pos, op) {
    var l = comp.layers.addShape(); l.name = name;
    newGroup(l, "Box"); rectItem(l, "Box", [w, h], [-w / 2, 0]); fill(l, "Box", color, op);
    P(l).setValue(pos);
    return l;
}

function slider(l, name, times, values) {
    l.property("ADBE Effect Parade").addProperty("ADBE Slider Control");
    var fx = l.property("ADBE Effect Parade");
    fx.property(fx.numProperties).name = name;
    keys(l.property("ADBE Effect Parade").property(name).property(1), times, values, 75);
}

function counter(comp, name, target, t0, dur, o) {
    var l = text(comp, name, String(target), o);
    slider(l, "Count", [t0, t0 + dur], [o.from || 0, target]);
    SFXQ.push({ f: "counter_roll.wav", t: t0, db: -15 });
    var dec = o.decimals || 0;
    l.property("ADBE Text Properties").property("ADBE Text Document").expression =
        'var v=effect("Count")(1).value;' + (dec ? '(Math.abs(v)<0.05?0:v).toFixed(' + dec + ');' : 'Math.round(v).toString();');
    return l;
}

// RTL unit word placed immediately to the LEFT of a number on the same baseline (live, at render time).
function stickLeftOf(l, refName, gap) {
    P(l).expression = 'var n=thisComp.layer("' + refName + '");var r=n.sourceRectAtTime(time,false);' +
        'var x=n.toComp([r.left,0])[0];[x-' + gap + ', n.position[1]]';
}

function solid(comp, color, name) { return comp.layers.addSolid(color, name, CFG.W, CFG.H, 1); }
function addMask(l, verts) {
    l.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
    var m = l.property("ADBE Mask Parade").property(l.property("ADBE Mask Parade").numProperties);
    m.property("ADBE Mask Shape").setValue(pathShape(verts, true));
    return l.property("ADBE Mask Parade").numProperties;
}
function mask(l, i) { return l.property("ADBE Mask Parade").property(i); }

function vignette(comp, op) {
    var l = solid(comp, [0, 0, 0], "Vignette");
    var i = addMask(l, [[160, 90], [1760, 90], [1760, 990], [160, 990]]);
    mask(l, i).inverted = true;
    mask(l, i).property("ADBE Mask Feather").setValue([560, 560]);
    tr(l).property("ADBE Opacity").setValue(op || 55);
    return l;
}

function scrimRight(comp, op) {
    var l = solid(comp, CFG.GREY, "Scrim");
    var i = addMask(l, [[1180, -200], [2300, -200], [2300, 1280], [1180, 1280]]);
    mask(l, i).property("ADBE Mask Feather").setValue([380, 0]);
    tr(l).property("ADBE Opacity").setValue(op || 70);
    return l;
}

function sectionTag(comp, str, y, t0, animate) {
    var name = "TAG_TXT";
    var t = text(comp, name, str, { w: "Black", size: CFG.TY.TAG, pos: [CFG.XR - 30, y], shadow: false });
    var box = comp.layers.addShape(); box.name = "TAG_BOX";
    newGroup(box, "Box"); rectItem(box, "Box", [200, 70], [-100, 0]); fill(box, "Box", CFG.ORANGE);
    items(box, "Box").property(1).property("ADBE Vector Rect Size").expression =
        'var r=thisComp.layer("' + name + '").sourceRectAtTime(time,false);[r.width+60, ' + Math.round(CFG.TY.TAG * 1.5) + ']';
    items(box, "Box").property(1).property("ADBE Vector Rect Position").expression =
        'var r=thisComp.layer("' + name + '").sourceRectAtTime(time,false);[-(r.width+60)/2,0]';
    P(box).expression = 'var t=thisComp.layer("' + name + '");var r=t.sourceRectAtTime(time,false);[' + CFG.XR + ', t.position[1]+r.top+r.height/2]';
    box.moveAfter(t);
    if (animate !== false) {
        keys(tr(box).property("ADBE Scale"), [t0, t0 + 0.45], [[0, 100], [100, 100]], 85);
        fadeIn(t, t0 + 0.2, 0.35, [40, 0]);
    }
    return t;
}

function accentBar(comp, x, y, w, t0) {
    var l = rectR(comp, "Accent", w, 8, CFG.ORANGE, [x, y]);
    keys(tr(l).property("ADBE Scale"), [t0, t0 + 0.5], [[0, 100], [100, 100]], 85);
    return l;
}

function headline(comp, str, y, t0, size) {
    var l = text(comp, "HEADLINE", str, { w: "Black", size: size || CFG.TY.HEAD, pos: [CFG.XR, y] });
    revealWords(l, t0, 0.9, 50);
    return l;
}
function label(comp, name, str, y, t0) {
    var l = text(comp, name, str, { w: "Bold", size: CFG.TY.LABEL, pos: [CFG.XR, y] });
    revealWords(l, t0, 0.6, 30);
    return l;
}

// ── 3D ──
function camera(c, move) {
    var cam = c.layers.addCamera("CAM", [CFG.W / 2, CFG.H / 2]);
    var Z = cam.property("ADBE Camera Options Group").property("ADBE Camera Zoom").value;
    var d = c.duration, m = move || {};
    var dolly = (m.dolly === undefined ? 320 : m.dolly);
    var p0 = [CFG.W / 2 + (m.x0 || 0), CFG.H / 2 + (m.y0 || 0), -Z];
    var p1 = [CFG.W / 2 + (m.x1 || 0), CFG.H / 2 + (m.y1 || 0), -Z + dolly];
    // gentle arc: the mid key bows sideways and slightly closer (orbit feel around the subject)
    var arc = m.arc === undefined ? 70 : m.arc;
    var pm = [(p0[0] + p1[0]) / 2 + arc, (p0[1] + p1[1]) / 2 - arc * 0.25, (p0[2] + p1[2]) / 2 + Math.abs(arc) * 0.6];
    var tEnd = Math.max(1.0, d - CFG.WIPE - 0.25);
    var push = m.push === undefined ? 240 : m.push;               // push-through that rides the wipe into the next shot
    var p2 = [p1[0], p1[1], p1[2] + push];
    keys(P(cam), [0, tEnd / 2, tEnd, d], [p0, pm, p1, p2], 45);
    try { P(cam).setTemporalEaseAtKey(4, [new KeyframeEase(0, 85)], [new KeyframeEase(0, 85)]); } catch (e) {}
    keys(tr(cam).property("ADBE Anchor Point"), [0, tEnd], [[CFG.W / 2 + (m.px0 || 0), CFG.H / 2, 0], [CFG.W / 2 + (m.px1 || 0), CFG.H / 2, 0]], 40);
    // micro handheld drift (very small, smooth)
    P(cam).expression = '[value[0]+Math.sin(time*0.9)*5+Math.sin(time*2.3)*1.5, value[1]+Math.cos(time*0.7)*4, value[2]]';
    try {
        cam.property("ADBE Camera Options Group").property("ADBE Camera Depth of Field").setValue(1);
        cam.property("ADBE Camera Options Group").property("ADBE Camera Focus Distance").setValue(Z + 200);
        cam.property("ADBE Camera Options Group").property("ADBE Camera Aperture").setValue(18);
    } catch (e) {}
    return Z;
}

// 3D layer that fills the frame at depth z (with extra margin for the camera move).
function at3D(l, item, Z, z, margin) {
    l.threeDLayer = true;
    var s = 100 * (Z + z) / Z * (CFG.W / item.width) * (margin || 1.18);
    tr(l).property("ADBE Scale").setValue([s, s, 100]);
    P(l).setValue([CFG.W / 2, CFG.H / 2, z]);
    return l;
}

function depthStack(c, id, Z) {
    var out = [];
    for (var k = 0; k < 3; k++) {
        var it = LAY[id][k]; if (!it) continue;
        var l = c.layers.add(it); l.name = "DEPTH_L" + k;
        at3D(l, it, Z, CFG.DEPTH[k], 1.18);
        out.push(l);
    }
    for (var j = out.length - 1; j >= 0; j--) out[j].moveToEnd(); // far ends at the bottom
    if (!out.length) { var ph = solid(c, CFG.GREY, id + " (MISSING LAYERS)"); ph.moveToEnd(); }
    // clean paper first; the original plate (with the model's real contact shadow) fades in as it lands
    var orig = importIfExists("layers/" + id + "_L0o.jpg", fFoot);
    if (orig && c.layer("DEPTH_L0")) {
        c.layers.add(orig); var lo = c.layer(1); lo.name = "DEPTH_L0_SHADOW";
        at3D(lo, orig, Z, CFG.DEPTH[0] - 1, 1.18);
        lo.moveBefore(c.layer("DEPTH_L0"));
        keys(tr(lo).property("ADBE Opacity"), [CFG.SKETCH_T0 + 1.6, CFG.SKETCH_T0 + 2.4], [0, 100], 50);
    }
    if (c.layer("DEPTH_L2")) sketchToModel(c, id, Z, c.layer("DEPTH_L2"), CFG.SKETCH_T0);
    return out;
}

// "From plans on paper": a pencil drawing of the model draws itself on the paper (right → left),
// then the real model rises out of it (bottom → top); the drawing stays faintly underneath.
function sketchToModel(c, id, Z, model, t0) {
    var it = importIfExists("layers/" + id + "_sketch.png", fFoot); if (!it) return;
    c.layers.add(it); var sk = c.layer(1); sk.name = "SKETCH";
    at3D(sk, it, Z, CFG.DEPTH[2] + 2, 1.18);
    sk.moveAfter(model);
    var W = it.width, H = it.height;
    var si = addMask(sk, [[W, 0], [W, 0], [W, H], [W, H]]);
    var sp = mask(sk, si).property("ADBE Mask Shape");
    sp.setValueAtTime(t0, pathShape([[W, -50], [W + 1, -50], [W + 1, H + 50], [W, H + 50]], true));
    sp.setValueAtTime(t0 + 0.9, pathShape([[-50, -50], [W + 1, -50], [W + 1, H + 50], [-50, H + 50]], true));
    easeKeys(sp, 60);
    mask(sk, si).property("ADBE Mask Feather").setValue([160, 0]);
    keys(tr(sk).property("ADBE Opacity"), [t0 + 1.7, t0 + 2.4], [100, 28], 50);
    var mi = addMask(model, [[0, H], [W, H], [W, H], [0, H]]);
    var mp = mask(model, mi).property("ADBE Mask Shape");
    mp.setValueAtTime(t0 + 0.8, pathShape([[-50, H + 60], [W + 50, H + 60], [W + 50, H + 61], [-50, H + 61]], true));
    mp.setValueAtTime(t0 + 1.8, pathShape([[-50, -60], [W + 50, -60], [W + 50, H + 61], [-50, H + 61]], true));
    easeKeys(mp, 70);
    mask(model, mi).property("ADBE Mask Feather").setValue([0, 180]);
    var v = P(model).value;
    keys(P(model), [t0 + 0.8, t0 + 1.9], [[v[0], v[1], v[2] + 60], v], 80);   // rises toward the lens
    SFXQ.push({ f: "pencil.wav", t: t0, db: -16 });
    SFXQ.push({ f: "rise.wav", t: t0 + 0.8, db: -14 });
}

var _seed = 7;
function rnd() { _seed = (_seed * 9301 + 49297) % 233280; return _seed / 233280; }

// Atmosphere. Fine dust motes drifting with a light wind (left → right) at many depths,
// plus a few large out-of-focus bokeh motes close to the lens. wind: px/s.
function particles(c, n, warm, wind) {
    wind = wind === undefined ? 18 : wind;
    for (var i = 0; i < n; i++) {
        var l = c.layers.addShape(); l.name = "Dust_" + (i + 1);
        newGroup(l, "D"); var sz = 2 + rnd() * 5; ellipse(l, "D", [sz, sz]);
        fill(l, "D", (warm && rnd() > 0.55) ? [1, 0.78, 0.5] : [1, 0.97, 0.92]);
        l.threeDLayer = true;
        var z = -300 + rnd() * 1700;
        P(l).setValue([rnd() * CFG.W * 1.4 - CFG.W * 0.2, rnd() * CFG.H * 1.2 - CFG.H * 0.1, z]);
        var spd = (wind * (0.6 + rnd() * 0.8)).toFixed(1);
        P(l).expression = 'var W=' + (CFG.W * 1.6) + ';var x=value[0]+time*' + spd + ';x=((x+' + (CFG.W * 0.3) + ')%W+W)%W-' + (CFG.W * 0.3) + ';' +
            '[x+Math.sin(time*0.8+' + i + ')*12, value[1]+Math.sin(time*0.5+' + (i * 1.7) + ')*18-time*3, value[2]]';
        tr(l).property("ADBE Opacity").expression = (15 + rnd() * 45).toFixed(0) + '*(0.6+0.4*Math.sin(time*1.3+' + i + '))';
        try { l.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2"); l.property("ADBE Effect Parade").property(1).property(1).setValue(1 + rnd() * 3); } catch (e) {}
        l.blendingMode = BlendingMode.ADD;
    }
}

// Soft volumetric god-rays from the key light (upper left), slowly breathing.
function godRays(c, ox, oy, op) {
    var l = c.layers.addShape(); l.name = "GodRays";
    newGroup(l, "Rays");
    for (var i = 0; i < 7; i++) {
        var a = (18 + i * 7 + rnd() * 4) * Math.PI / 180, len = 2600, w = 60 + rnd() * 140;
        var ex = Math.cos(a) * len, ey = Math.sin(a) * len, nx = -Math.sin(a) * w, ny = Math.cos(a) * w;
        path(l, "Rays", [[0, 0], [ex + nx, ey + ny], [ex - nx, ey - ny]], true);
    }
    fill(l, "Rays", [1, 0.86, 0.66]);
    P(l).setValue([ox, oy]);
    tr(l).property("ADBE Rotate Z").expression = 'Math.sin(time*0.25)*3';
    tr(l).property("ADBE Opacity").expression = (op || 14) + '*(0.75+0.25*Math.sin(time*0.6))';
    try { l.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2"); l.property("ADBE Effect Parade").property(1).property(1).setValue(60); } catch (e) {}
    l.blendingMode = BlendingMode.ADD;
    return l;
}

// Wind-blown sand: fast thin streaks skimming over a region (screen coords).
function sandWind(c, x0, y0, x1, y1, n) {
    for (var i = 0; i < n; i++) {
        var l = c.layers.addShape(); l.name = "SandStreak_" + (i + 1);
        newGroup(l, "S"); var ln = 40 + rnd() * 90; rectItem(l, "S", [ln, 1.5 + rnd() * 1.5], [0, 0], 1); fill(l, "S", [0.98, 0.86, 0.62]);
        var y = y0 + rnd() * (y1 - y0), spd = 260 + rnd() * 260, ph = rnd() * 10;
        P(l).setValue([x0, y]);
        P(l).expression = 'var span=' + (x1 - x0 + 200) + ';var x=' + x0 + '-100+((time+' + ph.toFixed(2) + ')*' + spd.toFixed(0) + ')%span;[x, value[1]+Math.sin(time*3+' + i + ')*3]';
        tr(l).property("ADBE Opacity").expression = 'var span=' + (x1 - x0 + 200) + ';var k=(((time+' + ph.toFixed(2) + ')*' + spd.toFixed(0) + ')%span)/span;' + (25 + rnd() * 35).toFixed(0) + '*Math.sin(k*Math.PI)';
        try { l.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2"); l.property("ADBE Effect Parade").property(1).property(1).setValue(2); } catch (e) {}
        l.blendingMode = BlendingMode.ADD;
    }
}

// Specular glint sweeping across a cut-out subject (masked to its alpha).
function glint(c, subjectName, t0) {
    var subj = c.layer(subjectName); if (!subj) return;
    var g = c.layers.addShape(); g.name = "Glint";
    newGroup(g, "Band"); path(g, "Band", [[-90, -900], [90, -900], [90, 900], [-90, 900]], true); fill(g, "Band", [1, 0.95, 0.85]);
    tr(g).property("ADBE Rotate Z").setValue(22);
    keys(P(g), [t0, t0 + 1.4], [[-300, CFG.H / 2], [CFG.W + 300, CFG.H / 2]], 55);
    tr(g).property("ADBE Opacity").setValue(55);
    try { g.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2"); g.property("ADBE Effect Parade").property(1).property(1).setValue(45); } catch (e) {}
    g.blendingMode = BlendingMode.ADD;
    var m = subj.duplicate(); m.name = subjectName + "_MATTE"; m.moveBefore(g);
    try { g.setTrackMatte(m, TrackMatteType.ALPHA); } catch (e) { try { g.moveAfter(m); g.trackMatteType = TrackMatteType.ALPHA; } catch (e2) { LOG.push("glint matte: " + e2.toString()); } }
    try { m.enabled = false; } catch (e) {}
}

// Bloom on emissive parts of a layer (blurred additive copy, gently pulsing).
function bloom(c, name, amt) {
    var src = c.layer(name); if (!src) return;
    var b = src.duplicate(); b.name = name + "_BLOOM"; b.moveBefore(src);
    try { b.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2"); b.property("ADBE Effect Parade").property(b.property("ADBE Effect Parade").numProperties).property(1).setValue(28); } catch (e) {}
    b.blendingMode = BlendingMode.ADD;
    tr(b).property("ADBE Opacity").expression = (amt || 30) + '*(0.8+0.2*Math.sin(time*2))';
}

// Animated turbulence (smoke billow / heat haze). amount keyed from a0 to a1 over the scene.
function turbulence(l, a0, a1, size, dur) {
    try {
        l.property("ADBE Effect Parade").addProperty("ADBE Turbulent Displace");
        var fx = function () { return l.property("ADBE Effect Parade").property(l.property("ADBE Effect Parade").numProperties); };
        keys(fx().property(2), [0, dur], [a0, a1], 40);       // Amount
        fx().property(3).setValue(size);                        // Size
        fx().property(6).expression = 'time*120';               // Evolution
    } catch (e) { LOG.push(l.name + ": turbulent displace " + e.toString()); }
}

function lightSweep(c, x0, x1) {
    var l = solid(c, [1, 0.85, 0.65], "LightSweep");
    try {
        l.property("ADBE Effect Parade").addProperty("ADBE Ramp");
        var r = function () { return l.property("ADBE Effect Parade").property(1); };
        r().property(1).setValue([x0, 200]); r().property(2).setValue([1, 0.82, 0.6, 1]);
        r().property(3).setValue([x0 + 900, 900]); r().property(4).setValue([0, 0, 0, 1]);
        r().property(5).setValue(2);   // radial
    } catch (e) {}
    l.blendingMode = BlendingMode.ADD;
    tr(l).property("ADBE Opacity").setValue(22);
    keys(P(l), [0, c.duration], [[CFG.W / 2 + (x0 - 960) * 0.2, CFG.H / 2], [CFG.W / 2 + (x1 - 960) * 0.2, CFG.H / 2]], 30);
    return l;
}

// Thin orange HUD rings / ticks floating in 3D (no text) — motion-graphic detail
function hud(c, x, y, z, t0) {
    var l = c.layers.addShape(); l.name = "HUD";
    newGroup(l, "Ring1"); ellipse(l, "Ring1", [260, 260]); stroke(l, "Ring1", CFG.ORANGE, 2); trimIn(l, "Ring1", t0, 1.2);
    newGroup(l, "Ring2"); ellipse(l, "Ring2", [330, 330]); stroke(l, "Ring2", CFG.WHITE, 1.5); trimIn(l, "Ring2", t0 + 0.2, 1.4);
    newGroup(l, "Ticks");
    for (var i = 0; i < 12; i++) {
        var a = i / 12 * Math.PI * 2;
        path(l, "Ticks", [[Math.cos(a) * 180, Math.sin(a) * 180], [Math.cos(a) * 196, Math.sin(a) * 196]], false);
    }
    stroke(l, "Ticks", CFG.ORANGE, 3);
    l.threeDLayer = true;
    P(l).setValue([x, y, z]);
    tr(l).property("ADBE Z Rotation").expression = 'time*12';
    tr(l).property("ADBE Opacity").setValue(55);
    fadeIn(l, t0, 0.6);
    return l;
}

function newComp(name, dur, folderItem) {
    var c = app.project.items.addComp(name, CFG.W, CFG.H, 1, dur, CFG.FPS);
    c.parentFolder = folderItem;
    try { c.motionBlur = true; c.shutterAngle = 180; } catch (e) {}
    return c;
}

// ───────────────────────────── BUILD ─────────────────────────────
app.beginUndoGroup("Build Green Initiative v2");

var proj = app.project || app.newProject();
var fRoot = proj.items.addFolder("GREEN_INITIATIVE_v2");
var fScenes = proj.items.addFolder("Scenes"); fScenes.parentFolder = fRoot;
var fFoot = proj.items.addFolder("Footage"); fFoot.parentFolder = fRoot;

var vo = importIfExists("audio/vo.mp3", fFoot);
var voDur = vo ? vo.duration : 113.2;
var TOTAL = Math.ceil((voDur + CFG.END_PAD) * CFG.FPS) / CFG.FPS;

var LAY = {};
for (var i = 0; i < ORDER.length; i++) {
    var id0 = ORDER[i];
    LAY[id0] = [importIfExists("layers/" + id0 + "_L0.jpg", fFoot),
                importIfExists("layers/" + id0 + "_L1.png", fFoot),
                importIfExists("layers/" + id0 + "_L2.png", fFoot)];
}
var TREES = [importIfExists("assets/tree1.png", fFoot), importIfExists("assets/tree2.png", fFoot), importIfExists("assets/tree3.png", fFoot)];
var PHOTO = importIfExists("assets/crown_prince.png", fFoot) || importIfExists("assets/crown_prince.jpg", fFoot);
var FLAG = importIfExists("assets/saudi_flag.png", fFoot);
var GUIDE = importIfExists("../channel-guide/safe-area-guide.png", fFoot);

function sceneLen(id) {
    var idx = 0; for (var i = 0; i < ORDER.length; i++) if (ORDER[i] === id) idx = i;
    var end = (idx < ORDER.length - 1) ? CFG.T[ORDER[idx + 1]] + CFG.WIPE : TOTAL;
    return end - CFG.T[id];
}

// Spreading green for aerial scenes: 2D sub-comp (dry → green) used as one deep 3D layer.
function spreadComp(id, origin, t0, dur, expand, len) {
    var it = LAY[id][0]; if (!it) return null;
    var sc = newComp(id + "_LAND", len, fScenes);
    sc.layers.add(it); sc.layer(1).name = "GREEN";
    var s = CFG.W / it.width * 100; tr(sc.layer("GREEN")).property("ADBE Scale").setValue([s, s]);
    var dry = sc.layer("GREEN").duplicate(); dry.name = "DRY";
    sc.layer("DRY").moveAfter(sc.layer("GREEN"));
    try {
        sc.layer("DRY").property("ADBE Effect Parade").addProperty("ADBE Tint");
        var tn = function () { return sc.layer("DRY").property("ADBE Effect Parade").property(1); };
        tn().property(1).setValue([0.30, 0.20, 0.09, 1]);
        tn().property(2).setValue([0.97, 0.85, 0.63, 1]);
        tn().property(3).setValue(100);
    } catch (e) {}
    var ox = origin[0] * it.width, oy = origin[1] * it.height, r = 60;
    var g = sc.layer("GREEN");
    var mi = addMask(g, [[ox - r, oy - r], [ox + r, oy - r], [ox + r, oy + r], [ox - r, oy + r]]);
    mask(sc.layer("GREEN"), mi).property("ADBE Mask Feather").setValue([220, 220]);
    keys(mask(sc.layer("GREEN"), mi).property("ADBE Mask Offset"), [t0, t0 + dur], [0, expand], 45);
    return sc;
}

var BUILD = {};

// S01 — "من خطط على ورق…": climate background, Saudi map + flag, general title
BUILD.S01 = function (c) {
    var Z = camera(c, { x0: -80, x1: 60, dolly: 380, px0: -40, px1: 30 });
    depthStack(c, "S01", Z);
    particles(c, CFG.PARTICLES, true, 22);
    vignette(c, 45);
    // Accurate 3D relief map (rendered from Natural Earth borders): body, orange glow, connection arcs
    var mapNames = ["S01_glow.png", "S01_map.png", "S01_lines.png"], mapL = [];
    for (var mi = 0; mi < mapNames.length; mi++) {
        var it = importIfExists("layers/" + mapNames[mi], fFoot); if (!it) { LOG.push("missing layers/" + mapNames[mi]); continue; }
        c.layers.add(it); var L = c.layer(1); L.name = mapNames[mi].replace(".png", "").replace("S01_", "MAP_").toUpperCase();
        at3D(L, it, Z, CFG.DEPTH[2], 1.18); mapL.push(L);
    }
    if (c.layer("MAP_GLOW")) {
        c.layer("MAP_GLOW").blendingMode = BlendingMode.ADD;
        keys(tr(c.layer("MAP_GLOW")).property("ADBE Opacity"), [1.8, 2.6], [0, 100]);
    }
    if (c.layer("MAP_MAP")) {
        var mm = c.layer("MAP_MAP"), sv = tr(mm).property("ADBE Scale").value;

        c.layer("MAP_GLOW").parent = mm; P(c.layer("MAP_GLOW")).setValue(tr(mm).property("ADBE Anchor Point").value);
        tr(c.layer("MAP_GLOW")).property("ADBE Scale").setValue([100, 100, 100]);
    }
    if (c.layer("MAP_MAP")) sketchToModel(c, "S01", Z, c.layer("MAP_MAP"), CFG.SKETCH_T0);
    if (c.layer("MAP_LINES")) {
        c.layer("MAP_LINES").blendingMode = BlendingMode.ADD;
        keys(tr(c.layer("MAP_LINES")).property("ADBE Opacity"), [2.0, 2.8], [0, 100]);
        if (c.layer("MAP_MAP")) { c.layer("MAP_LINES").parent = c.layer("MAP_MAP"); P(c.layer("MAP_LINES")).setValue(tr(c.layer("MAP_MAP")).property("ADBE Anchor Point").value); tr(c.layer("MAP_LINES")).property("ADBE Scale").setValue([100, 100, 100]); }
    }
    // climate: miniature clouds drifting over the map (scenario: background that suggests the climate)
    var CLOUD = importIfExists("assets/cloud.png", fFoot);
    if (CLOUD) {
        var cl = [[520, 210, -350, 34, 0.0], [1180, 170, -150, 26, 0.4], [880, 300, -520, 22, 0.8]];
        for (var ci = 0; ci < cl.length; ci++) {
            c.layers.add(CLOUD); var C1 = c.layer(1); C1.name = "Cloud_" + (ci + 1); C1.threeDLayer = true;
            tr(C1).property("ADBE Scale").setValue([cl[ci][3], cl[ci][3], 100]);
            P(C1).setValue([cl[ci][0], cl[ci][1], cl[ci][2]]);
            P(C1).expression = '[value[0]+time*' + (8 + ci * 4) + ', value[1]+Math.sin(time*0.7+' + ci + ')*6, value[2]]';
            fadeIn(C1, 0.3 + cl[ci][4], 0.8);
        }
    }
    var pin = c.layers.addShape(); pin.name = "PIN_RIYADH";
    newGroup(pin, "Dot"); ellipse(pin, "Dot", [22, 22]); fill(pin, "Dot", CFG.ORANGE);
    newGroup(pin, "Ring"); ellipse(pin, "Ring", [22, 22]); stroke(pin, "Ring", CFG.ORANGE, 3);
    items(pin, "Ring").property(1).property("ADBE Vector Ellipse Size").expression = 'var t=(time%1.6)/1.6;[22+90*t,22+90*t]';
    grp(pin, "Ring").property("ADBE Vector Transform Group").property("ADBE Vector Group Opacity").expression = '100*(1-(time%1.6)/1.6)';
    pin.threeDLayer = true;
    if (c.layer("MAP_MAP")) { pin.parent = c.layer("MAP_MAP"); P(pin).setValue([1011.5, 421.6, -2]); }
    fadeIn(pin, 2.4, 0.3);
    var flag;
    if (FLAG) { flag = c.layers.add(FLAG); var fs = 340 / FLAG.width * 100; tr(flag).property("ADBE Scale").setValue([fs, fs]); }
    else flag = c.layers.addSolid([0, 108 / 255, 53 / 255], "FLAG_PLACEHOLDER — assets/saudi_flag.png", 340, 227, 1);
    flag.name = "FLAG";
    try {
        c.layer("FLAG").property("ADBE Effect Parade").addProperty("ADBE Wave Warp");
        var ww = function () { return c.layer("FLAG").property("ADBE Effect Parade").property(1); };
        ww().property(2).setValue(10); ww().property(3).setValue(240); ww().property(5).setValue(1.2);
    } catch (e) {}
    flag = c.layer("FLAG");
    flag.threeDLayer = true;
    P(flag).setValue([1290, 400, -260]);
    shadow(flag, 45);
    fadeIn(flag, 1.0, 0.6, [80, 0]);
    SFXQ.push({ f: "impact_soft.wav", t: 1.6, db: -11 });
    var title = text(c, "TITLE", "مبادرة السعودية الخضراء", { w: "Black", size: CFG.TY.TITLE, pos: [CFG.W / 2, 780], side: "c" });
    revealWords(title, 1.6, 1.0, 60);
    var bar = rectR(c, "TitleBar", 220, 8, CFG.ORANGE, [CFG.W / 2 + 110, 655]);
    keys(tr(bar).property("ADBE Scale"), [1.5, 2.1], [[0, 100], [100, 100]], 85);
};

// S02 — photo + 2021 + "أطلقها ولي العهد…" (VO cues: "أطلقها" ≈ +3.7s, "2021" ≈ +7.8s)
BUILD.S02 = function (c) {
    var Z = camera(c, { x0: 60, x1: -60, dolly: 300 });
    depthStack(c, "S02", Z);
    particles(c, CFG.PARTICLES, true, 26);
    sandWind(c, 150, 420, 1050, 680, 22);
    SFXQ.push({ f: "wind.wav", t: 0, db: -24, len: c.duration, fade: 1.0 });
    var fx = 640, fy = 470, fw = 430, fh = 500;   // photo on the left; caption block on the right (safe area)
    var frame = rectR(c, "PhotoFrame", fw + 16, fh + 16, CFG.WHITE, [fx + (fw + 16) / 2, fy]);
    var ph;
    if (PHOTO) {
        ph = c.layers.add(PHOTO);
        var ps = Math.max(fw / PHOTO.width, fh / PHOTO.height) * 100;
        tr(ph).property("ADBE Scale").setValue([ps, ps]);
        var cx = PHOTO.width / 2, cy = PHOTO.height / 2, hw = fw / 2 / (ps / 100), hh = fh / 2 / (ps / 100);
        addMask(ph, [[cx - hw, cy - hh], [cx + hw, cy - hh], [cx + hw, cy + hh], [cx - hw, cy + hh]]);
    } else ph = c.layers.addSolid([0.55, 0.55, 0.55], "PHOTO_PLACEHOLDER — assets/crown_prince.png", fw, fh, 1);
    ph.name = "PHOTO";
    P(ph).setValue([fx, fy]);
    ph.moveBefore(frame);
    var acc = rectR(c, "PhotoAccent", 14, fh + 16, CFG.ORANGE, [fx + fw / 2 + 22, fy]);
    shadow(frame, 55);
    keys(tr(frame).property("ADBE Scale"), [0.3, 0.9], [[0, 100], [100, 100]], 85);
    keys(tr(acc).property("ADBE Scale"), [0.2, 0.6], [[100, 0], [100, 100]], 85);
    fadeIn(ph, 0.7, 0.5, [60, 0]);
    var cap = text(c, "CAPTION", "أطلقها ولي العهد السعودي\rالأمير محمد بن سلمان", { w: "Bold", size: CFG.TY.LABEL, pos: [CFG.XR, CFG.Y.HEAD] });
    revealWords(cap, 3.6, 1.0, 40);
    var yr = counter(c, "YEAR", 2021, 7.4, 1.3, { from: 2000, w: "Black", size: CFG.TY.NUM, pos: [CFG.XR, CFG.Y.NUM + 60], rtl: false, color: CFG.ORANGE });
    fadeIn(yr, 7.2, 0.4, [0, 40]);
    accentBar(c, CFG.XR, CFG.Y.TAG, 160, 0.4);
};

// S03 — climate change, rain
BUILD.S03 = function (c) {
    var Z = camera(c, { x0: -40, x1: 40, y0: 20, y1: -10, dolly: 260 });
    depthStack(c, "S03", Z);
    try {
        var rain = solid(c, [0, 0, 0], "Rain");
        rain.property("ADBE Effect Parade").addProperty("CC Rainfall");
        c.layer("Rain").blendingMode = BlendingMode.SCREEN;
        tr(c.layer("Rain")).property("ADBE Opacity").setValue(85);
        // rain falls only from the miniature cloud down onto the block (feathered cone)
        var ri = addMask(c.layer("Rain"), [[420, 200], [720, 200], [860, 560], [300, 560]]);
        mask(c.layer("Rain"), ri).property("ADBE Mask Feather").setValue([60, 60]);
    } catch (e) { LOG.push("S03 rain: " + e.toString()); }
    // lightning: two quick soft flashes
    SFXQ.push({ f: "rain.wav", t: 0, db: -17, len: c.duration, fade: 0.6 });
    SFXQ.push({ f: "thunder.wav", t: 1.15, db: -13 }); SFXQ.push({ f: "thunder.wav", t: 3.65, db: -16 });
    var fl = solid(c, [0.85, 0.9, 1], "Lightning"); fl.blendingMode = BlendingMode.ADD;
    keys(tr(fl).property("ADBE Opacity"), [1.10, 1.14, 1.22, 1.26, 1.36, 3.60, 3.64, 3.78], [0, 22, 4, 16, 0, 0, 18, 0], 10);
    particles(c, Math.round(CFG.PARTICLES * 0.5), false, 30);
    scrimRight(c, 65);
    accentBar(c, CFG.XR, CFG.Y.TAG, 160, 0.4);
    headline(c, "التصدي للتغيرات\rالمناخية", CFG.Y.HEAD, 0.5);
};

function goalsScene(c, id, line, tagAnim, move, headT) {
    var Z = camera(c, move);
    depthStack(c, id, Z);
    particles(c, CFG.PARTICLES, true);
    scrimRight(c, 60);
    sectionTag(c, "الأهداف:", CFG.Y.TAG, 0.25, tagAnim);
    headline(c, line, CFG.Y.HEAD, headT === undefined ? 0.5 : headT);
    return Z;
}

// S04 — green economy (headline on "تتصدرها قيادة الانتقال" ≈ +3.8s)
BUILD.S04 = function (c) {
    goalsScene(c, "S04", "الانتقال نحو\rالاقتصاد الأخضر", true, { x0: -90, x1: 40, dolly: 360, px0: -60, px1: 0 }, 3.6);
    var ln = c.layers.addShape(); ln.name = "UpTrend";
    newGroup(ln, "Line"); path(ln, "Line", [[400, 770], [520, 700], [630, 725], [760, 590], [870, 615], [990, 430]], false);
    var GREEN = [0.25, 0.85, 0.42];   // scenario: green rising arrows
    stroke(ln, "Line", GREEN, 8); trimIn(ln, "Line", 3.6, 1.6);
    newGroup(ln, "Head"); path(ln, "Head", [[935, 440], [990, 430], [985, 486]], false); stroke(ln, "Head", GREEN, 8);
    keys(grp(ln, "Head").property("ADBE Vector Transform Group").property("ADBE Vector Group Opacity"), [5.1, 5.3], [0, 100]);
    ln.threeDLayer = true; P(ln).setValue([CFG.W / 2, CFG.H / 2, -150]);
    shadow(ln, 40);
    glint(c, "DEPTH_L2", 3.9);
};

// S05 — emissions / CO2
BUILD.S05 = function (c) {
    goalsScene(c, "S05", "تقليل الانبعاثات\rالكربونية", false, { x0: 50, x1: -50, dolly: 300 });
    var fac = c.layer("DEPTH_L2");
    if (fac) {
        var smoke = fac.duplicate(); smoke.name = "SMOKE";
        var si = addMask(smoke, [[0, 0], [2400, 0], [2400, 430], [0, 430]]);
        mask(smoke, si).property("ADBE Mask Feather").setValue([90, 90]);
        try { mask(smoke, si).maskMode = MaskMode.INTERSECT; } catch (e) {}
        var fi = addMask(fac, [[0, 0], [2400, 0], [2400, 430], [0, 430]]);
        try { mask(fac, fi).maskMode = MaskMode.SUBTRACT; } catch (e) { mask(fac, fi).inverted = true; }
        mask(fac, fi).property("ADBE Mask Feather").setValue([90, 90]);
        turbulence(smoke, 28, 40, 70, c.duration);
        keys(tr(smoke).property("ADBE Opacity"), [0.8, c.duration], [100, 45], 40);      // smoke thins out
        P(smoke).expression = '[value[0]+time*6, value[1]-time*4, value[2]]';
    }
    var orb = c.layers.addShape(); orb.name = "CO2_ORB";
    newGroup(orb, "Orb"); ellipse(orb, "Orb", [280, 280]); fill(orb, "Orb", CFG.GREY, 55); stroke(orb, "Orb", CFG.WHITE, 4);
    P(orb).setValue([760, 360]);
    keys(tr(orb).property("ADBE Scale"), [0.3, 0.8], [[0, 0], [100, 100]], 85);
    P(orb).expression = '[value[0], value[1]+Math.sin(time*1.6)*8]';
    var co = text(c, "CO2", "CO", { w: "Black", size: 110, pos: [745, 400], rtl: false, side: "c" });
    var two = text(c, "CO2_sub", "2", { w: "Black", size: 58, pos: [0, 425], rtl: false, side: "l" });
    P(two).expression = 'var n=thisComp.layer("CO2");var r=n.sourceRectAtTime(time,false);[n.toComp([r.left+r.width,0])[0]+4, value[1]]';
    fadeIn(co, 0.6, 0.3); fadeIn(two, 0.7, 0.3);
    for (var i = 0; i < 3; i++) {
        var ch = c.layers.addShape(); ch.name = "Down_" + (i + 1);
        newGroup(ch, "Chevron"); path(ch, "Chevron", [[-60, -30], [0, 30], [60, -30]], false); stroke(ch, "Chevron", CFG.ORANGE, 16);
        P(ch).setValue([760, 560 + i * 70]);
        tr(ch).property("ADBE Opacity").expression = 'var t=time-' + (0.9 + i * 0.15) + ';t<0?0:(50+50*Math.sin(t*5-' + i + '))';
        P(ch).expression = 'var t=Math.max(0,time-0.9);[value[0], value[1]+(t*40)%30]';
    }
};

// S06 — afforestation: real 3D trees appearing one after another
BUILD.S06 = function (c) {
    sandWind(c, 0, 250, 1350, 650, 26);
    SFXQ.push({ f: "wind.wav", t: 0, db: -24, len: c.duration, fade: 0.8 });
    var Z = goalsScene(c, "S06", "التوسع في التشجير\rوحماية البيئة", false, { x0: -120, x1: 60, dolly: 420, px0: -80, px1: 0 });
    // trees stand on the sand tile: [x, y] on the 1920-wide plate, on-screen scale (%)
    var spots = [[300, 240, 9], [520, 225, 8], [740, 215, 8], [940, 205, 7], [1060, 200, 6],
                 [200, 400, 13], [430, 390, 12], [660, 375, 11], [880, 360, 10], [1060, 345, 9],
                 [320, 590, 17], [580, 570, 16], [830, 545, 15], [1040, 520, 13]];
    var idx = []; for (var k = 0; k < spots.length; k++) idx.push(k);
    idx.sort(function (a, b) { return spots[b][1] - spots[a][1]; }); // nearest (lowest on screen) first → ends on top
    for (var q = 0; q < idx.length; q++) {
        var i = idx[q], it = TREES[i % 3]; if (!it) continue;
        var t = c.layers.add(it); t.name = "Tree_" + (i + 1);
        t.threeDLayer = true;
        var z = CFG.DEPTH[2], k2 = (Z + z) / Z, mg = 1.18;           // same depth + margin as the tile layer
        var s = spots[i][2] * k2 * mg * (i % 3 === 0 ? 1.0 : 0.9);
        tr(t).property("ADBE Anchor Point").setValue([it.width / 2, it.height * 0.93, 0]);
        P(t).setValue([CFG.W / 2 + (spots[i][0] - CFG.W / 2) * mg * k2, CFG.H / 2 + (spots[i][1] - CFG.H / 2) * mg * k2, z - 1 - i * 0.1]);
        var t0 = 1.9 + i * 0.18;
        keys(tr(t).property("ADBE Scale"), [t0, t0 + 0.35, t0 + 0.55], [[0, 0, 100], [s * 1.08, s * 1.08, 100], [s, s, 100]], 70);
        var under = c.layer("DEPTH_L2") || c.layer("DEPTH_L1") || c.layer("DEPTH_L0");
        if (under) t.moveBefore(under);
        tr(t).property("ADBE Z Rotation").expression = 'Math.sin(time*1.8+' + i + ')*1.6+Math.sin(time*4.1+' + (i * 2) + ')*0.5';
    }
};

function plansScene(c, id, tagAnim, move) {
    var Z = camera(c, move);
    depthStack(c, id, Z);
    particles(c, CFG.PARTICLES, true);
    scrimRight(c, 55);
    sectionTag(c, "الخطط:", CFG.Y.TAG, 0.25, tagAnim);
    return Z;
}

// S07 — 700 billion riyals (cues: "استثمارات" ≈ +4.6s, "700 مليار ريال" ≈ +6.7…8.6s)
BUILD.S07 = function (c) {
    plansScene(c, "S07", true, { x0: -60, x1: 60, y0: 30, y1: -20, dolly: 380 });
    label(c, "LINE1", "استثمارات بقيمة", CFG.Y.LABEL, 4.4);
    var n = counter(c, "NUM", 700, 6.6, 1.8, { w: "Black", size: CFG.TY.NUM, pos: [CFG.XR, CFG.Y.NUM], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 6.5, 0.3, [0, 40]);
    var u = text(c, "UNIT", "مليار ريال", { w: "Bold", size: CFG.TY.UNIT, pos: [0, 0], boxW: 520 });
    stickLeftOf(u, "NUM", 28);
    fadeIn(u, 7.0, 0.4);
    glint(c, "DEPTH_L2", 6.8);
};

// S08 — 77 programmes (cue ≈ +0.7…2.6s)
BUILD.S08 = function (c) {
    plansScene(c, "S08", false, { x0: 80, x1: -40, dolly: 340, px0: 40, px1: -20 });
    bloom(c, "DEPTH_L2", 32);
    var n = counter(c, "NUM", 77, 0.6, 1.8, { w: "Black", size: CFG.TY.NUM, pos: [CFG.XR, CFG.Y.NUM], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 0.5, 0.3, [0, 40]);
    var u = text(c, "UNIT", "برنامجا متكاملا", { w: "Bold", size: CFG.TY.UNIT, pos: [0, 0], boxW: 620 });
    stickLeftOf(u, "NUM", 28);
    fadeIn(u, 1.0, 0.4);
};

function achievementsScene(c, id, tagAnim, move, origin, dur, expand) {
    var Z = camera(c, move);
    var land = spreadComp(id, origin, 0.3, dur, expand, c.duration);
    if (land) { c.layers.add(land); var L = c.layer(1); L.name = "LAND"; at3D(L, land, Z, 1200, 1.2); L.moveToEnd(); }
    particles(c, CFG.PARTICLES, false);
    scrimRight(c, 72);
    sectionTag(c, "الإنجازات:", CFG.Y.TAG, 0.25, tagAnim);
    return Z;
}

// S09 — 100 million trees (≈ +6.8s) / 118 thousand hectares (≈ +10.0s)
BUILD.S09 = function (c) {
    achievementsScene(c, "S09", true, { x0: -60, x1: 40, y0: -40, y1: 0, dolly: 380 }, [0.12, 0.85], 11.5, 1600);
    label(c, "A1_WORD", "زراعة", CFG.Y.LABEL, 6.5);
    var n1 = counter(c, "A1_NUM", 100, 6.8, 1.6, { w: "Black", size: CFG.TY.NUM, pos: [CFG.XR, CFG.Y.NUM], rtl: false, color: CFG.ORANGE });
    fadeIn(n1, 6.7, 0.3, [0, 30]);
    var u1 = text(c, "A1_UNIT", "مليون شجرة", { w: "Bold", size: CFG.TY.UNIT, pos: [0, 0], boxW: 520 }); stickLeftOf(u1, "A1_NUM", 28); fadeIn(u1, 7.2, 0.4);
    var tB = 9.6;
    var sep = rectR(c, "Divider", 560, 3, CFG.WHITE, [CFG.XR, CFG.Y.NUM + 45], 60);
    keys(tr(sep).property("ADBE Scale"), [tB - 0.3, tB + 0.2], [[0, 100], [100, 100]], 85);
    label(c, "A2_WORD", "استصلاح", CFG.Y.LABEL2, tB);
    var n2 = counter(c, "A2_NUM", 118, tB + 0.4, 1.2, { w: "Black", size: CFG.TY.NUM2, pos: [CFG.XR, CFG.Y.NUM2], rtl: false });
    fadeIn(n2, tB + 0.3, 0.3, [0, 30]);
    var u2 = text(c, "A2_UNIT", "ألف هكتارا", { w: "Bold", size: CFG.TY.UNIT2, pos: [0, 0], boxW: 480 }); stickLeftOf(u2, "A2_NUM", 26); fadeIn(u2, tB + 0.8, 0.4);
};

// S10 — 1150 field surveys (≈ +0.8…4.2s), bigger spread
BUILD.S10 = function (c) {
    achievementsScene(c, "S10", false, { x0: 0, x1: 0, y0: -60, y1: 20, dolly: 520 }, [0.5, 0.45], 9.0, 2000);
    var n = counter(c, "NUM", 1150, 0.7, 2.6, { w: "Black", size: CFG.TY.NUM, pos: [CFG.XR, CFG.Y.NUM], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 0.6, 0.3, [0, 40]);
    var u = text(c, "UNIT", "مسحا ميدانيا", { w: "Bold", size: CFG.TY.UNIT, pos: [0, 0], boxW: 560 });
    stickLeftOf(u, "NUM", 28);
    fadeIn(u, 1.2, 0.4);
    for (var sc = 0; sc < 2; sc++) {
        var sl = c.layers.addShape(); sl.name = "ScanLine_" + (sc + 1);
        newGroup(sl, "L"); rectItem(sl, "L", [1150, 3], [575, 0]); fill(sl, "L", CFG.ORANGE);
        newGroup(sl, "G"); rectItem(sl, "G", [1150, 40], [575, 0]); fill(sl, "G", CFG.ORANGE, 18);
        var st = 0.9 + sc * 2.4;
        keys(P(sl), [st, st + 2.0], [[0, 260], [0, 820]], 30);
        keys(tr(sl).property("ADBE Opacity"), [st, st + 0.2, st + 1.8, st + 2.0], [0, 100, 100, 0], 30);
        sl.blendingMode = BlendingMode.ADD;
    }
};

// S11 — Riyadh, thermometer, -2.2 (cues: "انخفاض" ≈ +7.7s, "2.2 درجة" ≈ +12.2s)
BUILD.S11 = function (c) {
    var Z = camera(c, { x0: -100, x1: 40, dolly: 360, px0: -60, px1: 0 });
    depthStack(c, "S11", Z);
    particles(c, CFG.PARTICLES, false);
    scrimRight(c, 55);
    accentBar(c, CFG.XR, CFG.Y.TAG, 160, 7.4);
    headline(c, "انخفاض درجة حرارة\rمراكز المدن", CFG.Y.HEAD, 7.6);
    if (c.layer("DEPTH_L2")) turbulence(c.layer("DEPTH_L2"), 6, 0, 45, 13.6);
    if (c.layer("DEPTH_L0")) turbulence(c.layer("DEPTH_L0"), 4, 0, 45, 13.6);
    glint(c, "DEPTH_L2", 12.2);
    var th = c.layers.addShape(); th.name = "Thermometer";
    newGroup(th, "Tube"); rectItem(th, "Tube", [46, 300], [0, -150], 23); fill(th, "Tube", CFG.WHITE, 25); stroke(th, "Tube", CFG.WHITE, 5);
    newGroup(th, "Mercury"); rectItem(th, "Mercury", [20, 250], [0, -125], 10); fill(th, "Mercury", CFG.ORANGE);
    newGroup(th, "Bulb"); ellipse(th, "Bulb", [96, 96], [0, 30]); fill(th, "Bulb", CFG.ORANGE); stroke(th, "Bulb", CFG.WHITE, 5);
    newGroup(th, "Ticks");
    for (var i = 0; i < 5; i++) path(th, "Ticks", [[34, -60 - i * 55], [54, -60 - i * 55]], false);
    stroke(th, "Ticks", CFG.WHITE, 3);
    slider(th, "Level", [11.8, 13.6], [250, 110]);
    items(th, "Mercury").property(1).property("ADBE Vector Rect Size").expression = '[20, effect("Level")(1)]';
    items(th, "Mercury").property(1).property("ADBE Vector Rect Position").expression = '[0, -effect("Level")(1)/2]';
    P(th).setValue([1000, 760]);
    fadeIn(th, 7.9, 0.5, [0, 40]);
    shadow(th, 40);
    var n = counter(c, "NUM", -2.2, 12.0, 1.6, { from: 0, decimals: 1, w: "Black", size: CFG.TY.NUM, pos: [CFG.XR, CFG.Y.NUM + 145], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 11.9, 0.3, [0, 30]);
    var u = text(c, "UNIT", "درجة", { w: "Bold", size: CFG.TY.UNIT, pos: [0, 0], boxW: 300 });
    stickLeftOf(u, "NUM", 28);
    fadeIn(u, 12.4, 0.4);
};

// S12 — OUT shot + title in the middle (camera pulls back)
BUILD.S12 = function (c) {
    var Z = camera(c, { x0: 0, x1: 0, y0: 30, y1: -20, dolly: -420 });
    depthStack(c, "S12", Z);
    particles(c, CFG.PARTICLES, true, 14);
    sandWind(c, 350, 420, 1500, 700, 14);
    SFXQ.push({ f: "wind.wav", t: 0, db: -26, len: c.duration, fade: 1.5 });
    SFXQ.push({ f: "impact_soft.wav", t: 0.8, db: -11 });
    vignette(c, 60);
    var title = text(c, "TITLE", "مبادرة السعودية الخضراء", { w: "Black", size: CFG.TY.TITLE, pos: [CFG.W / 2, 560], side: "c" });
    revealWords(title, 0.8, 1.1, 60);
    var b1 = rectR(c, "BarTop", 240, 8, CFG.ORANGE, [CFG.W / 2 + 120, 410]);
    var b2 = rectR(c, "BarBottom", 240, 8, CFG.ORANGE, [CFG.W / 2 + 120, 625]);
    keys(tr(b1).property("ADBE Scale"), [0.7, 1.3], [[0, 100], [100, 100]], 85);
    keys(tr(b2).property("ADBE Scale"), [0.9, 1.5], [[0, 100], [100, 100]], 85);
};

// ── Safe-area check (channel guide) — measures every caption/graphic at the end of its scene ──
var ZONES = [[59, 45, 253, 151, "logo"], [1571, 115, 1920, 151, "top bar"], [59, 801, 353, 907, "bottom-left box"], [0, 913, 1920, 1080, "bottom band"]];
function checkSafe(c, id) {
    var t = Math.max(0, c.duration - CFG.WIPE - 0.1);
    for (var i = 1; i <= c.numLayers; i++) {
        var l = c.layer(i);
        if (l.threeDLayer || l.guideLayer || !l.enabled) continue;
        if (!(l instanceof TextLayer) && !(l instanceof ShapeLayer)) continue;
        if (/^(Dust|Wipe|Scrim|Vignette|LightSweep)/.test(l.name)) continue;
        try { var ee = tr(l).property("ADBE Position").expressionError; if (ee) LOG.push("EXPR " + id + " / " + l.name + ": " + ee); } catch (e) {}
        var r; try { r = l.sourceRectAtTime(t, false); } catch (e) { continue; }
        if (!r || r.width <= 0) continue;
        var pos = tr(l).property("ADBE Position").valueAtTime(t, false);
        var anc = tr(l).property("ADBE Anchor Point").valueAtTime(t, false);
        var sc = tr(l).property("ADBE Scale").valueAtTime(t, false);
        var x0 = pos[0] + (r.left - anc[0]) * sc[0] / 100, y0 = pos[1] + (r.top - anc[1]) * sc[1] / 100;
        if (l instanceof TextLayer) x0 += CFG.TEXT_SHIFT * r.width * sc[0] / 100;
        var x1 = x0 + r.width * sc[0] / 100, y1 = y0 + r.height * sc[1] / 100;
        var box = "[" + Math.round(x0) + "," + Math.round(y0) + " → " + Math.round(x1) + "," + Math.round(y1) + "]";
        if (x0 < 0 || y0 < 0 || x1 > CFG.W || y1 > CFG.H) LOG.push("SAFE " + id + " / " + l.name + ": outside frame " + box);
        for (var z = 0; z < ZONES.length; z++) {
            var Zn = ZONES[z];
            if (x0 < Zn[2] && x1 > Zn[0] && y0 < Zn[3] && y1 > Zn[1]) LOG.push("SAFE " + id + " / " + l.name + ": overlaps " + Zn[4] + " " + box);
        }
    }
}

// ── Main comp ──
var main = newComp("GREEN_INITIATIVE_MAIN_v2", TOTAL, fRoot);
try { main.motionBlur = true; } catch (e) {}

for (var s = 0; s < ORDER.length; s++) {
    var id = ORDER[s];
    var sc = newComp(id, sceneLen(id), fScenes);
    _seed = 7 + s * 31;
    SFXQ = []; BOXES = {};
    try { BUILD[id](sc); } catch (err) { LOG.push(id + ": " + err.toString() + " (line " + err.line + ")"); }
    for (var qq = 0; qq < SFXQ.length; qq++) { SFXQ[qq].t += CFG.T[id]; if (SFXQ[qq].len) SFXQ[qq].len = Math.min(SFXQ[qq].len, sceneLen(id)); SFX_ALL.push(SFXQ[qq]); }
    try { checkSafe(sc, id); } catch (err) { LOG.push(id + " safe-check: " + err.toString()); }
    for (var mb = 1; mb <= sc.numLayers; mb++) {
        var ml = sc.layer(mb);
        if (/^(Dust|Bokeh|GodRays|Scrim|Vignette|LightSweep|Lightning)/.test(ml.name)) continue;
        try { ml.motionBlur = true; } catch (e) {}
    }
    main.layers.add(sc);
    var L = main.layer(1);
    L.startTime = CFG.T[id];
    L.name = id;
    try { L.motionBlur = true; } catch (e) {}
    if (s > 0 && !CFG.SECTION_CUTS[id]) {
        // whip-pan across the table: previous shot slides out to the right, new one slides in from the left
        var w0 = CFG.T[id], w1 = w0 + 0.45, prev = main.layer(ORDER[s - 1]);
        keys(P(L), [w0, w1], [[CFG.W / 2 - CFG.W * 1.05, CFG.H / 2], [CFG.W / 2, CFG.H / 2]], 85);
        if (prev) keys(P(prev), [w0 - 0.02, w1 - 0.05], [[CFG.W / 2, CFG.H / 2], [CFG.W / 2 + CFG.W * 1.05, CFG.H / 2]], 85);
        SFX_ALL.push({ f: "swish.wav", t: w0 - 0.12, db: -11 });
    }
    if (s > 0 && CFG.SECTION_CUTS[id]) {
        SFX_ALL.push({ f: "whoosh.wav", t: CFG.T[id] - 0.2, db: -9 });
        var t0 = CFG.T[id], t1 = t0 + CFG.WIPE;
        var mi = addMask(L, [[CFG.W, -10], [CFG.W + 10, -10], [CFG.W + 10, CFG.H + 10], [CFG.W, CFG.H + 10]]);
        var mp = mask(main.layer(id), mi).property("ADBE Mask Shape");
        mp.setValueAtTime(t0, pathShape([[CFG.W, -10], [CFG.W + 10, -10], [CFG.W + 10, CFG.H + 10], [CFG.W, CFG.H + 10]], true));
        mp.setValueAtTime(t1, pathShape([[-200, -10], [CFG.W + 10, -10], [CFG.W + 10, CFG.H + 10], [-200, CFG.H + 10]], true));
        easeKeys(mp, 75);
        var bo = rectR(main, "Wipe_O_" + id, 70, CFG.H + 20, CFG.ORANGE, [CFG.W + 70, CFG.H / 2]);
        keys(P(bo), [t0, t1], [[CFG.W + 70, CFG.H / 2], [-130, CFG.H / 2]], 75);
        bo.inPoint = t0; bo.outPoint = t1 + 0.04;
        var bg = rectR(main, "Wipe_G_" + id, 26, CFG.H + 20, CFG.GREY, [CFG.W + 96, CFG.H / 2]);
        keys(P(bg), [t0, t1], [[CFG.W + 96, CFG.H / 2], [-104, CFG.H / 2]], 75);
        bg.inPoint = t0; bg.outPoint = t1 + 0.04;
    }
    try { main.markerProperty.setValueAtTime(CFG.T[id], new MarkerValue(id)); } catch (e) {}
}

// warm grade that slowly builds over the story (light travels from neutral to golden)
var grade = main.layers.addSolid([1, 0.78, 0.5], "WarmGrade (story light)", CFG.W, CFG.H, 1);
grade.blendingMode = BlendingMode.SOFT_LIGHT;
keys(tr(grade).property("ADBE Opacity"), [0, TOTAL * 0.55, TOTAL], [0, 10, 18], 30);

// ── sound design (generated SFX in audio/sfx) + optional music bed ──
var fSfx = proj.items.addFolder("SFX"); fSfx.parentFolder = fRoot;
var SFXI = {};
function setDb(l, t, db) { try { l.property("ADBE Audio Group").property("ADBE Audio Levels").setValueAtTime(t, [db, db]); } catch (e) {} }
for (var q = 0; q < SFX_ALL.length; q++) {
    var e = SFX_ALL[q];
    if (!SFXI[e.f]) SFXI[e.f] = importIfExists("audio/sfx/" + e.f, fSfx);
    var it = SFXI[e.f]; if (!it) continue;
    var parts = e.len ? Math.ceil(e.len / (it.duration - 0.5)) : 1;
    for (var pp = 0; pp < parts; pp++) {
        main.layers.add(it); var al = main.layer(1); al.name = "SFX " + e.f;
        var st = Math.max(0, e.t + pp * (it.duration - 0.5));
        al.startTime = st;
        if (e.len) {
            var end = Math.min(e.t + e.len, st + it.duration); al.outPoint = end;
            var fd = e.fade || 0.5;
            if (pp === 0) { setDb(al, st, -60); setDb(al, st + fd, e.db); } else { setDb(al, st, e.db); }
            if (end >= e.t + e.len - 0.01) { setDb(al, end - fd, e.db); setDb(al, end, -60); }
        } else {
            try { al.property("ADBE Audio Group").property("ADBE Audio Levels").setValue([e.db, e.db]); } catch (e2) {}
        }
    }
}
var MUSIC = importIfExists("audio/music.mp3", fFoot) || importIfExists("audio/music.wav", fFoot);
if (MUSIC) {
    main.layers.add(MUSIC); var ml2 = main.layer(1); ml2.name = "MUSIC BED";
    setDb(ml2, 0, -60); setDb(ml2, 1.5, -20); setDb(ml2, TOTAL - 2.5, -20); setDb(ml2, TOTAL, -60);
} else LOG.push("No music bed: put audio/music.mp3 (or .wav) and re-run to add it at -20 dB.");

if (vo) { main.layers.add(vo); main.layer(1).name = "VO"; }
if (GUIDE) {
    main.layers.add(GUIDE); var gl = main.layer(1); gl.name = "SAFE AREA GUIDE (does not render)";
    gl.guideLayer = true; tr(gl).property("ADBE Opacity").setValue(60);
}

main.openInViewer();
try { var lf = f("build_log.txt"); lf.encoding = "UTF-8"; lf.open("w"); lf.write("BUILD 2026-11-08-K  TEXT_SHIFT=" + CFG.TEXT_SHIFT + "\n\n--- TEXT DIAGNOSTICS ---\n" + DIAG.join("\n") + "\n\n--- NOTES ---\n" + (LOG.length ? LOG.join("\n") : "OK — no errors")); lf.close(); } catch (e) {}
app.endUndoGroup();

alert("BUILD 2026-11-08-K — تم بناء المشروع ✔\n\nComp: GREEN_INITIATIVE_MAIN_v2 (" + TOTAL.toFixed(2) + "s)\n" +
      "Fonts: " + font("Black") + " / " + font("Bold") + " / " + font("Regular") + "\n" +
      (PHOTO ? "" : "• ضع صورة ولي العهد في assets/crown_prince.png\n") +
      (FLAG ? "" : "• ضع العلم الرسمي في assets/saudi_flag.png\n") +
      (LOG.length ? "\n⚠ " + LOG.length + " ملاحظة — التفاصيل في build_log.txt" : "\nبدون أخطاء"));
})();
