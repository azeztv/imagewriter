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
    XR: 1790,          // captions right edge (safe area)
    WIPE: 0.5,
    DEPTH: [1800, 900, 300],   // z of far / mid / near layers
    PARTICLES: 28
};

var LOG = [];
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
function text(comp, name, str, o) {
    var l = comp.layers.addText(str);
    l.name = name;
    var p = l.property("ADBE Text Properties").property("ADBE Text Document");
    var td = p.value;
    try { td.resetCharStyle(); td.resetParagraphStyle(); } catch (e) {}
    td.text = str;
    try { td.font = font(o.w || "Bold"); } catch (e) { LOG.push(name + ": font " + font(o.w || "Bold") + " not found"); }
    td.fontSize = o.size || 60;
    td.applyFill = true; td.fillColor = o.color || CFG.WHITE;
    td.applyStroke = false;
    var side = o.side || "r";
    td.justification = side === "c" ? ParagraphJustification.CENTER_JUSTIFY :
                       side === "l" ? ParagraphJustification.LEFT_JUSTIFY : ParagraphJustification.RIGHT_JUSTIFY;
    try { td.composerEngine = ComposerEngine.UNIVERSAL_TYPE_ENGINE; } catch (e) {}
    try { td.direction = (o.rtl === false) ? ParagraphDirection.DIRECTION_LEFT_TO_RIGHT : ParagraphDirection.DIRECTION_RIGHT_TO_LEFT; } catch (e) {}
    try { td.digitSet = DigitSet.ARABIC_DIGITS; } catch (e) {}   // 0-9, never ٠-٩
    try { td.autoLeading = false; td.leading = Math.round((o.size || 60) * 1.3); } catch (e) {}
    p.setValue(td);
    P(l).setValue(o.pos);
    P(l).expression = edgeExpr(side) + 'value+[(anchorPoint[0]-e)*scale[0]/100,0]';
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
    var dec = o.decimals || 0;
    l.property("ADBE Text Properties").property("ADBE Text Document").expression =
        'var v=effect("Count")(1).value;' + (dec ? '(Math.abs(v)<0.05?0:v).toFixed(' + dec + ');' : 'Math.round(v).toString();');
    return l;
}

// RTL unit word placed immediately to the LEFT of a number layer (same baseline).
function stickLeftOf(l, refName, gap) {
    P(l).expression =
        'var r=thisComp.layer("' + refName + '");var rb=r.sourceRectAtTime(time,false);' +
        'var X=r.toComp([rb.left,0])[0]-' + gap + ';' + edgeExpr("r") +
        '[X+(anchorPoint[0]-e)*scale[0]/100, r.position[1]]';
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
    var i = addMask(l, [[1060, -200], [2300, -200], [2300, 1280], [1060, 1280]]);
    mask(l, i).property("ADBE Mask Feather").setValue([460, 0]);
    tr(l).property("ADBE Opacity").setValue(op || 70);
    return l;
}

function sectionTag(comp, str, y, t0, animate) {
    var name = "TAG_TXT";
    var box = comp.layers.addShape(); box.name = "TAG_BOX";
    newGroup(box, "Box"); rectItem(box, "Box", [200, 80], [-100, 0]); fill(box, "Box", CFG.ORANGE);
    var t = text(comp, name, str, { w: "Black", size: 52, pos: [CFG.XR - 32, y], shadow: false });
    items(box, "Box").property(1).property("ADBE Vector Rect Size").expression = 'var b=thisComp.layer("' + name + '").sourceRectAtTime(time,false);[b.width+64,b.height+36]';
    items(box, "Box").property(1).property("ADBE Vector Rect Position").expression = 'var b=thisComp.layer("' + name + '").sourceRectAtTime(time,false);[-(b.width+64)/2,0]';
    P(box).expression = 'var l=thisComp.layer("' + name + '");var b=l.sourceRectAtTime(time,false);[' + CFG.XR + ', l.position[1]+b.top+b.height/2]';
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
    var l = text(comp, "HEADLINE", str, { w: "Black", size: size || 84, pos: [CFG.XR, y] });
    revealWords(l, t0, 0.9, 50);
    return l;
}

// ── 3D ──
function camera(c, move) {
    var cam = c.layers.addCamera("CAM", [CFG.W / 2, CFG.H / 2]);
    var Z = cam.property("ADBE Camera Options Group").property("ADBE Camera Zoom").value;
    var d = c.duration, m = move || {};
    var p0 = [CFG.W / 2 + (m.x0 || 0), CFG.H / 2 + (m.y0 || 0), -Z];
    var p1 = [CFG.W / 2 + (m.x1 || 0), CFG.H / 2 + (m.y1 || 0), -Z + (m.dolly === undefined ? 320 : m.dolly)];
    keys(P(cam), [0, d], [p0, p1], 40);
    keys(tr(cam).property("ADBE Anchor Point"), [0, d], [[CFG.W / 2 + (m.px0 || 0), CFG.H / 2, 0], [CFG.W / 2 + (m.px1 || 0), CFG.H / 2, 0]], 40);
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
    return out;
}

var _seed = 7;
function rnd() { _seed = (_seed * 9301 + 49297) % 233280; return _seed / 233280; }

function particles(c, n, warm) {
    for (var i = 0; i < n; i++) {
        var l = c.layers.addShape(); l.name = "Dust_" + (i + 1);
        newGroup(l, "D"); var sz = 3 + rnd() * 9; ellipse(l, "D", [sz, sz]);
        fill(l, "D", (warm && rnd() > 0.6) ? CFG.ORANGE : CFG.WHITE);
        l.threeDLayer = true;
        P(l).setValue([rnd() * CFG.W * 1.3 - CFG.W * 0.15, rnd() * CFG.H * 1.2 - CFG.H * 0.1, -500 + rnd() * 1500]);
        P(l).expression = 'value+[Math.sin(time*0.4+' + i + ')*40, -time*' + (6 + rnd() * 14).toFixed(1) + ', 0]+(wiggle(0.3,20)-value)';
        tr(l).property("ADBE Opacity").setValue(20 + rnd() * 55);
        try {
            l.property("ADBE Effect Parade").addProperty("ADBE Gaussian Blur 2");
            l.property("ADBE Effect Parade").property(1).property(1).setValue(2 + rnd() * 6);
        } catch (e) {}
    }
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
    particles(c, CFG.PARTICLES, true);
    lightSweep(c, 400, 900);
    vignette(c, 45);
    var MAP = [[-271.4,-148.7],[-241.8,-144.1],[-230.2,-153.0],[-223.9,-163.5],[-203.6,-167.6],[-199.2,-177.3],[-190.4,-182.3],[-216.9,-211.4],[-163.6,-226.0],[-158.5,-230.4],[-126.4,-222.5],[-86.8,-202.1],[-11.7,-143.5],[37.8,-141.2],[61.5,-138.4],[68.1,-124.5],[87.0,-125.2],[97.4,-100.1],[110.5,-93.5],[115.0,-83.2],[133.2,-71.0],[134.8,-58.9],[132.2,-49.2],[135.5,-39.4],[143.2,-31.3],[146.7,-21.7],[150.7,-14.6],[158.8,-8.8],[166.1,-10.9],[171.2,0.3],[172.2,7.0],[182.4,36.5],[262.4,51.2],[267.8,45.1],[280.0,65.7],[262.3,124.0],[182.4,153.1],[105.6,164.3],[80.8,177.4],[61.7,208.0],[49.3,212.9],[42.6,203.2],[32.4,204.6],[6.7,201.7],[1.8,198.8],[-28.9,199.5],[-36.2,202.1],[-47.1,194.5],[-54.1,208.8],[-51.4,221.1],[-63.1,230.4],[-66.6,218.0],[-74.6,209.2],[-76.6,197.6],[-90.4,187.1],[-104.6,162.7],[-112.1,139.0],[-130.5,118.9],[-142.4,114.1],[-160.0,86.3],[-163.1,66.1],[-162.0,48.8],[-177.2,16.5],[-189.7,5.1],[-204.1,-0.9],[-212.8,-17.6],[-211.4,-24.2],[-218.8,-39.3],[-226.6,-45.8],[-237.0,-67.5],[-253.2,-91.0],[-266.7,-111.0],[-280.0,-110.9],[-275.9,-126.9],[-274.7,-137.1]];
    var map = c.layers.addShape(); map.name = "MAP_KSA";
    newGroup(map, "Fill"); path(map, "Fill", MAP, true); fill(map, "Fill", CFG.WHITE, 0);
    keys(last(map, "Fill").property("ADBE Vector Fill Opacity"), [1.0, 2.0], [0, 24]);
    newGroup(map, "Outline"); path(map, "Outline", MAP, true); stroke(map, "Outline", CFG.WHITE, 4); trimIn(map, "Outline", 0.2, 1.6);
    newGroup(map, "Glow"); path(map, "Glow", MAP, true); stroke(map, "Glow", CFG.ORANGE, 2.5); trimIn(map, "Glow", 0.4, 1.6);
    map.threeDLayer = true;
    P(map).setValue([760, 395, -120]);
    keys(tr(map).property("ADBE Y Rotation"), [0, c.duration], [-12, 6], 40);
    shadow(map, 45);
    var pin = c.layers.addShape(); pin.name = "PIN_RIYADH";
    newGroup(pin, "Dot"); ellipse(pin, "Dot", [20, 20]); fill(pin, "Dot", CFG.ORANGE);
    newGroup(pin, "Ring"); ellipse(pin, "Ring", [20, 20]); stroke(pin, "Ring", CFG.ORANGE, 3);
    items(pin, "Ring").property(1).property("ADBE Vector Ellipse Size").expression = 'var t=(time%1.6)/1.6;[20+80*t,20+80*t]';
    grp(pin, "Ring").property("ADBE Vector Transform Group").property("ADBE Vector Group Opacity").expression = '100*(1-(time%1.6)/1.6)';
    pin.threeDLayer = true;
    pin.parent = c.layer("MAP_KSA");
    P(pin).setValue([41.8, -13.3, -2]);
    fadeIn(pin, 1.6, 0.3);
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
    var title = text(c, "TITLE", "مبادرة السعودية الخضراء", { w: "Black", size: 110, pos: [CFG.W / 2, 775], side: "c" });
    revealWords(title, 1.6, 1.0, 60);
    var bar = rectR(c, "TitleBar", 220, 8, CFG.ORANGE, [CFG.W / 2 + 110, 655]);
    keys(tr(bar).property("ADBE Scale"), [1.5, 2.1], [[0, 100], [100, 100]], 85);
};

// S02 — photo + 2021 + "أطلقها ولي العهد…" (VO cues: "أطلقها" ≈ +3.7s, "2021" ≈ +7.8s)
BUILD.S02 = function (c) {
    var Z = camera(c, { x0: 60, x1: -60, dolly: 300 });
    depthStack(c, "S02", Z);
    particles(c, CFG.PARTICLES, true);
    lightSweep(c, 1300, 700);
    var fx = 1520, fy = 420, fw = 470, fh = 560;
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
    var cap = text(c, "CAPTION", "أطلقها ولي العهد السعودي\rالأمير محمد بن سلمان", { w: "Bold", size: 60, pos: [1200, 690] });
    revealWords(cap, 3.6, 1.0, 40);
    var yr = counter(c, "YEAR", 2021, 7.4, 1.3, { from: 2000, w: "Black", size: 300, pos: [1200, 520], rtl: false });
    fadeIn(yr, 7.2, 0.4, [0, 40]);
    accentBar(c, 1200, 580, 300, 7.6);
};

// S03 — climate change, rain
BUILD.S03 = function (c) {
    var Z = camera(c, { x0: -40, x1: 40, y0: 20, y1: -10, dolly: 260 });
    depthStack(c, "S03", Z);
    try {
        var rain = solid(c, [0, 0, 0], "Rain");
        rain.property("ADBE Effect Parade").addProperty("CC Rainfall");
        c.layer("Rain").blendingMode = BlendingMode.SCREEN;
        tr(c.layer("Rain")).property("ADBE Opacity").setValue(75);
    } catch (e) { LOG.push("S03 rain: " + e.toString()); }
    scrimRight(c, 65);
    accentBar(c, CFG.XR, 380, 160, 0.4);
    headline(c, "التصدي للتغيرات\rالمناخية", 490, 0.5, 96);
};

function goalsScene(c, id, line, tagAnim, move, headT) {
    var Z = camera(c, move);
    depthStack(c, id, Z);
    particles(c, CFG.PARTICLES, true);
    scrimRight(c, 60);
    sectionTag(c, "الأهداف:", 330, 0.25, tagAnim);
    headline(c, line, 470, headT === undefined ? 0.5 : headT, 86);
    return Z;
}

// S04 — green economy (headline on "تتصدرها قيادة الانتقال" ≈ +3.8s)
BUILD.S04 = function (c) {
    goalsScene(c, "S04", "الانتقال نحو\rالاقتصاد الأخضر", true, { x0: -90, x1: 40, dolly: 360, px0: -60, px1: 0 }, 3.6);
    var ln = c.layers.addShape(); ln.name = "UpTrend";
    newGroup(ln, "Line"); path(ln, "Line", [[160, 820], [330, 740], [470, 770], [640, 610], [780, 640], [960, 430]], false);
    stroke(ln, "Line", CFG.ORANGE, 8); trimIn(ln, "Line", 3.6, 1.6);
    newGroup(ln, "Head"); path(ln, "Head", [[905, 440], [960, 430], [955, 486]], false); stroke(ln, "Head", CFG.ORANGE, 8);
    keys(grp(ln, "Head").property("ADBE Vector Transform Group").property("ADBE Vector Group Opacity"), [5.1, 5.3], [0, 100]);
    ln.threeDLayer = true; P(ln).setValue([CFG.W / 2, CFG.H / 2, -150]);
    shadow(ln, 40);
    hud(c, 1450, 820, -200, 3.8);
};

// S05 — emissions / CO2
BUILD.S05 = function (c) {
    goalsScene(c, "S05", "تقليل الانبعاثات\rالكربونية", false, { x0: 50, x1: -50, dolly: 300 });
    var orb = c.layers.addShape(); orb.name = "CO2_ORB";
    newGroup(orb, "Orb"); ellipse(orb, "Orb", [280, 280]); fill(orb, "Orb", CFG.GREY, 55); stroke(orb, "Orb", CFG.WHITE, 4);
    P(orb).setValue([760, 360]);
    keys(tr(orb).property("ADBE Scale"), [0.3, 0.8], [[0, 0], [100, 100]], 85);
    P(orb).expression = 'value+[0,Math.sin(time*1.6)*8]';
    var co = text(c, "CO2", "CO", { w: "Black", size: 120, pos: [760, 400], rtl: false, side: "c" });
    var two = text(c, "CO2_sub", "2", { w: "Black", size: 64, pos: [842, 432], rtl: false, side: "l" });
    fadeIn(co, 0.6, 0.3); fadeIn(two, 0.7, 0.3);
    for (var i = 0; i < 3; i++) {
        var ch = c.layers.addShape(); ch.name = "Down_" + (i + 1);
        newGroup(ch, "Chevron"); path(ch, "Chevron", [[-60, -30], [0, 30], [60, -30]], false); stroke(ch, "Chevron", CFG.ORANGE, 16);
        P(ch).setValue([760, 560 + i * 70]);
        tr(ch).property("ADBE Opacity").expression = 'var t=time-' + (0.9 + i * 0.15) + ';t<0?0:(50+50*Math.sin(t*5-' + i + '))';
        P(ch).expression = 'var t=Math.max(0,time-0.9);value+[0,(t*40)%30]';
    }
};

// S06 — afforestation: real 3D trees appearing one after another
BUILD.S06 = function (c) {
    var Z = goalsScene(c, "S06", "التوسع في التشجير\rوحماية البيئة", false, { x0: -120, x1: 60, dolly: 420, px0: -80, px1: 0 });
    // [screen x, screen y (ground contact), z depth]
    var spots = [[1060, 455, 1400], [990, 470, 1150], [905, 490, 900], [810, 515, 700], [700, 550, 500], [575, 600, 330], [430, 670, 180], [270, 760, 60], [90, 880, -60],
                 [560, 470, 1200], [420, 485, 1000], [260, 505, 800]];
    var idx = []; for (var k = 0; k < spots.length; k++) idx.push(k);
    idx.sort(function (a, b) { return spots[a][2] - spots[b][2]; }); // nearest first → ends on top
    for (var q = 0; q < idx.length; q++) {
        var i = idx[q], it = TREES[i % 3]; if (!it) continue;
        var t = c.layers.add(it); t.name = "Tree_" + (i + 1);
        t.threeDLayer = true;
        var z = spots[i][2];
        var k2 = (Z + z) / Z;
        var s = (spots[i][1] - 412) / (880 - 412) * 75 * k2;
        tr(t).property("ADBE Anchor Point").setValue([it.width / 2, it.height - 20, 0]);
        P(t).setValue([CFG.W / 2 + (spots[i][0] - CFG.W / 2) * k2, CFG.H / 2 + (spots[i][1] - CFG.H / 2) * k2, z]);
        var t0 = 0.4 + i * 0.3;
        keys(tr(t).property("ADBE Scale"), [t0, t0 + 0.35, t0 + 0.55], [[0, 0, 100], [s * 1.08, s * 1.08, 100], [s, s, 100]], 70);
        var under = c.layer("DEPTH_L2") || c.layer("DEPTH_L1") || c.layer("DEPTH_L0");
        if (under) t.moveBefore(under);
    }
};

function plansScene(c, id, tagAnim, move) {
    var Z = camera(c, move);
    depthStack(c, id, Z);
    particles(c, CFG.PARTICLES, true);
    lightSweep(c, 300, 800);
    scrimRight(c, 55);
    sectionTag(c, "الخطط:", 300, 0.25, tagAnim);
    return Z;
}

// S07 — 700 billion riyals (cues: "استثمارات" ≈ +4.6s, "700 مليار ريال" ≈ +6.7…8.6s)
BUILD.S07 = function (c) {
    plansScene(c, "S07", true, { x0: -60, x1: 60, y0: 30, y1: -20, dolly: 380 });
    var l1 = text(c, "LINE1", "استثمارات بقيمة", { w: "Bold", size: 66, pos: [CFG.XR, 430] });
    revealWords(l1, 4.4, 0.7, 40);
    var n = counter(c, "NUM", 700, 6.6, 1.8, { w: "Black", size: 230, pos: [CFG.XR, 650], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 6.5, 0.3, [0, 40]);
    var u = text(c, "UNIT", "مليار ريال", { w: "Bold", size: 84, pos: [0, 0] });
    stickLeftOf(u, "NUM", 30);
    fadeIn(u, 7.0, 0.4);
    hud(c, 520, 300, -250, 6.6);
};

// S08 — 77 programmes (cue ≈ +0.7…2.6s)
BUILD.S08 = function (c) {
    plansScene(c, "S08", false, { x0: 80, x1: -40, dolly: 340, px0: 40, px1: -20 });
    var n = counter(c, "NUM", 77, 0.6, 1.8, { w: "Black", size: 250, pos: [CFG.XR, 620], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 0.5, 0.3, [0, 40]);
    var u = text(c, "UNIT", "برنامجا متكاملا", { w: "Bold", size: 84, pos: [0, 0] });
    stickLeftOf(u, "NUM", 34);
    fadeIn(u, 1.0, 0.4);
};

function achievementsScene(c, id, tagAnim, move, origin, dur, expand) {
    var Z = camera(c, move);
    var land = spreadComp(id, origin, 0.3, dur, expand, c.duration);
    if (land) { c.layers.add(land); var L = c.layer(1); L.name = "LAND"; at3D(L, land, Z, 1200, 1.2); L.moveToEnd(); }
    particles(c, CFG.PARTICLES, false);
    scrimRight(c, 72);
    sectionTag(c, "الإنجازات:", 270, 0.25, tagAnim);
    return Z;
}

// S09 — 100 million trees (≈ +6.8s) / 118 thousand hectares (≈ +10.0s)
BUILD.S09 = function (c) {
    achievementsScene(c, "S09", true, { x0: -60, x1: 40, y0: -40, y1: 0, dolly: 380 }, [0.12, 0.85], 11.5, 1600);
    var a1 = text(c, "A1_WORD", "زراعة", { w: "Bold", size: 60, pos: [CFG.XR, 390] }); revealWords(a1, 6.5, 0.5, 30);
    var n1 = counter(c, "A1_NUM", 100, 6.8, 1.6, { w: "Black", size: 170, pos: [CFG.XR, 550], rtl: false, color: CFG.ORANGE });
    fadeIn(n1, 6.7, 0.3, [0, 30]);
    var u1 = text(c, "A1_UNIT", "مليون شجرة", { w: "Bold", size: 70, pos: [0, 0] }); stickLeftOf(u1, "A1_NUM", 28); fadeIn(u1, 7.2, 0.4);
    var tB = 9.6;
    var sep = rectR(c, "Divider", 520, 3, CFG.WHITE, [CFG.XR, 585], 60);
    keys(tr(sep).property("ADBE Scale"), [tB - 0.3, tB + 0.2], [[0, 100], [100, 100]], 85);
    var a2 = text(c, "A2_WORD", "استصلاح", { w: "Bold", size: 60, pos: [CFG.XR, 668] }); revealWords(a2, tB, 0.5, 30);
    var n2 = counter(c, "A2_NUM", 118, tB + 0.4, 1.6, { w: "Black", size: 150, pos: [CFG.XR, 805], rtl: false });
    fadeIn(n2, tB + 0.3, 0.3, [0, 30]);
    var u2 = text(c, "A2_UNIT", "ألف هكتارا", { w: "Bold", size: 64, pos: [0, 0] }); stickLeftOf(u2, "A2_NUM", 28); fadeIn(u2, tB + 0.8, 0.4);
};

// S10 — 1150 field surveys (≈ +0.8…4.2s), bigger spread
BUILD.S10 = function (c) {
    achievementsScene(c, "S10", false, { x0: 0, x1: 0, y0: -60, y1: 20, dolly: 520 }, [0.5, 0.45], 9.0, 2000);
    var n = counter(c, "NUM", 1150, 0.7, 2.6, { w: "Black", size: 230, pos: [CFG.XR, 560], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 0.6, 0.3, [0, 40]);
    var u = text(c, "UNIT", "مسحا ميدانيا", { w: "Bold", size: 84, pos: [CFG.XR, 690] });
    revealWords(u, 1.2, 0.7, 30);
    hud(c, 600, 640, -200, 0.8);
};

// S11 — Riyadh, thermometer, -2.2 (cues: "انخفاض" ≈ +7.7s, "2.2 درجة" ≈ +12.2s)
BUILD.S11 = function (c) {
    var Z = camera(c, { x0: -100, x1: 40, dolly: 360, px0: -60, px1: 0 });
    depthStack(c, "S11", Z);
    particles(c, CFG.PARTICLES, false);
    lightSweep(c, 500, 1000);
    scrimRight(c, 55);
    headline(c, "انخفاض درجة حرارة\rمراكز المدن", 260, 7.6, 76);
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
    P(th).setValue([1720, 700]);
    fadeIn(th, 7.9, 0.5, [0, 40]);
    shadow(th, 40);
    var n = counter(c, "NUM", -2.2, 12.0, 1.6, { from: 0, decimals: 1, w: "Black", size: 210, pos: [1610, 700], rtl: false });
    fadeIn(n, 11.9, 0.3, [0, 30]);
    var u = text(c, "UNIT", "درجة", { w: "Bold", size: 84, pos: [0, 0] });
    stickLeftOf(u, "NUM", 28);
    fadeIn(u, 12.4, 0.4);
};

// S12 — OUT shot + title in the middle (camera pulls back)
BUILD.S12 = function (c) {
    var Z = camera(c, { x0: 0, x1: 0, y0: 30, y1: -20, dolly: -420 });
    depthStack(c, "S12", Z);
    particles(c, CFG.PARTICLES, true);
    lightSweep(c, 1400, 900);
    vignette(c, 60);
    var title = text(c, "TITLE", "مبادرة السعودية الخضراء", { w: "Black", size: 120, pos: [CFG.W / 2, 560], side: "c" });
    revealWords(title, 0.8, 1.1, 60);
    var b1 = rectR(c, "BarTop", 240, 8, CFG.ORANGE, [CFG.W / 2 + 120, 410]);
    var b2 = rectR(c, "BarBottom", 240, 8, CFG.ORANGE, [CFG.W / 2 + 120, 625]);
    keys(tr(b1).property("ADBE Scale"), [0.7, 1.3], [[0, 100], [100, 100]], 85);
    keys(tr(b2).property("ADBE Scale"), [0.9, 1.5], [[0, 100], [100, 100]], 85);
};

// ── Main comp ──
var main = newComp("GREEN_INITIATIVE_MAIN_v2", TOTAL, fRoot);

for (var s = 0; s < ORDER.length; s++) {
    var id = ORDER[s];
    var sc = newComp(id, sceneLen(id), fScenes);
    _seed = 7 + s * 31;
    try { BUILD[id](sc); } catch (err) { LOG.push(id + ": " + err.toString() + " (line " + err.line + ")"); }
    main.layers.add(sc);
    var L = main.layer(1);
    L.startTime = CFG.T[id];
    L.name = id;
    if (s > 0) {
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

if (vo) { main.layers.add(vo); main.layer(1).name = "VO"; }
if (GUIDE) {
    main.layers.add(GUIDE); var gl = main.layer(1); gl.name = "SAFE AREA GUIDE (does not render)";
    gl.guideLayer = true; tr(gl).property("ADBE Opacity").setValue(60);
}

main.openInViewer();
try { var lf = f("build_log.txt"); lf.encoding = "UTF-8"; lf.open("w"); lf.write(LOG.length ? LOG.join("\n") : "OK — no errors"); lf.close(); } catch (e) {}
app.endUndoGroup();

alert("تم بناء المشروع v2 ✔\n\nComp: GREEN_INITIATIVE_MAIN_v2 (" + TOTAL.toFixed(2) + "s)\n" +
      "Fonts: " + font("Black") + " / " + font("Bold") + " / " + font("Regular") + "\n" +
      (PHOTO ? "" : "• ضع صورة ولي العهد في assets/crown_prince.png\n") +
      (FLAG ? "" : "• ضع العلم الرسمي في assets/saudi_flag.png\n") +
      (LOG.length ? "\n⚠ " + LOG.length + " ملاحظة — التفاصيل في build_log.txt" : "\nبدون أخطاء"));
})();
