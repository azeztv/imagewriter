/*  مبادرة السعودية الخضراء — Motion Graphics builder for Adobe After Effects
    -------------------------------------------------------------------------
    Run:  File > Scripts > Run Script File…  and pick this file.
    The script must stay in its folder, next to:
        plates/S01.png … S12.png      background plates
        assets/tree1.png … tree3.png  tree cut-outs (transparent PNG)
        audio/vo.mp3                  voice-over
        assets/crown_prince.png       (optional) official photo  — placeholder if missing
        assets/saudi_flag.png         (optional) official flag   — placeholder if missing
        ../channel-guide/safe-area-guide.png  (guide layer, never renders)

    Everything you may want to tweak is in CFG below:
    scene start times (seconds in the VO), colours, fonts.
    On-screen text = the script's call-ups, word for word.
    Requires After Effects 2023 (23.0) or newer for RTL text options.
*/
(function () {

// ───────────────────────────── CONFIG ─────────────────────────────
var CFG = {
    W: 1920, H: 1080, FPS: 25,
    // Scene start times (seconds in vo.mp3). Estimated from the VO pauses — adjust if needed.
    T: {
        S01: 0.00,   // افتتاح — العنوان + الخريطة + العلم
        S02: 5.89,   // 2021 — ولي العهد
        S03: 15.37,  // التصدي للتغيرات المناخية
        S04: 24.63,  // الأهداف: الاقتصاد الأخضر
        S05: 32.28,  // الأهداف: الانبعاثات
        S06: 36.58,  // الأهداف: التشجير
        S07: 43.38,  // الخطط: 700 مليار
        S08: 52.71,  // الخطط: 77 برنامجا
        S09: 62.19,  // الإنجازات: 100 مليون / 118 ألف
        S10: 75.65,  // الإنجازات: 1150
        S11: 88.93,  // الرياض -2.2
        S12: 104.10  // OUT + العنوان
    },
    END_PAD: 1.0,               // seconds after the VO ends
    ORANGE: [1, 0x60 / 255, 0], // #FF6000
    GREY:   [0x3C / 255, 0x3C / 255, 0x3C / 255], // #3C3C3C
    WHITE:  [1, 1, 1],
    // Leave "" to auto-detect the installed Neue Haas Bloomberg fonts (AE 24+),
    // or type the exact PostScript names here.
    FONT: { Black: "", Bold: "", Regular: "" },
    FONT_FAMILY_MATCH: /bloomberg|neue ?haas|neuehaas/i,
    XR: 1800,                   // right edge for captions (inside safe area)
    WIPE: 0.5                   // transition length (s)
};

var LOG = [];
var ORDER = ["S01","S02","S03","S04","S05","S06","S07","S08","S09","S10","S11","S12"];
var ROOT = File($.fileName).parent;

// ───────────────────────────── HELPERS ─────────────────────────────
function f(rel) { return new File(ROOT.fsName + "/" + rel); }

function importIfExists(rel, folderItem) {
    var file = f(rel);
    if (!file.exists) return null;
    var it = app.project.importFile(new ImportOptions(file));
    if (folderItem) it.parentFolder = folderItem;
    return it;
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
    var n = 1;
    var t = prop.propertyValueType;
    if (t !== PropertyValueType.TwoD_SPATIAL && t !== PropertyValueType.ThreeD_SPATIAL &&
        t !== PropertyValueType.SHAPE && t !== PropertyValueType.OneD) {
        try { n = prop.value.length || 1; } catch (e) { n = 1; }
    }
    var arr = []; for (var k = 0; k < n; k++) arr.push(new KeyframeEase(0, inf));
    for (var i = 1; i <= prop.numKeys; i++) {
        try { prop.setTemporalEaseAtKey(i, arr, arr); } catch (e) {}
    }
}

function keys(prop, times, values, inf) {
    for (var i = 0; i < times.length; i++) prop.setValueAtTime(times[i], values[i]);
    easeKeys(prop, inf);
}

function tr(layer) { return layer.property("ADBE Transform Group"); }

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
    td.justification = (o.just !== undefined) ? o.just : ParagraphJustification.RIGHT_JUSTIFY;
    try { td.composerEngine = ComposerEngine.UNIVERSAL_TYPE_ENGINE; } catch (e) {}
    try {
        td.direction = (o.rtl === false) ? ParagraphDirection.DIRECTION_LEFT_TO_RIGHT
                                         : ParagraphDirection.DIRECTION_RIGHT_TO_LEFT;
    } catch (e) {}
    try { td.digitSet = DigitSet.ARABIC_DIGITS; } catch (e) {}   // 0-9, never ٠-٩
    try { td.autoLeading = false; td.leading = Math.round((o.size || 60) * 1.3); } catch (e) {}
    p.setValue(td);
    // Anchor = right edge / centre / left edge of the real text box on the baseline,
    // so placement never depends on RTL/LTR justification quirks.
    var side = (o.just === ParagraphJustification.CENTER_JUSTIFY) ? "c" :
               (o.just === ParagraphJustification.LEFT_JUSTIFY) ? "l" : "r";
    tr(l).property("ADBE Anchor Point").expression =
        'var b=sourceRectAtTime(0,false);[' + (side === "r" ? 'b.left+b.width' : side === "c" ? 'b.left+b.width/2' : 'b.left') + ',0]';
    tr(l).property("ADBE Position").setValue(o.pos);
    if (o.shadow !== false) shadow(l, o.shadowOp || 45);
    return l;
}

function shadow(l, op) {
    try {
        var d = l.property("ADBE Effect Parade").addProperty("ADBE Drop Shadow");
        d.property("ADBE Drop Shadow-0001").setValue([0, 0, 0, 1]);
        d.property("ADBE Drop Shadow-0002").setValue(op * 2.55);
        d.property("ADBE Drop Shadow-0003").setValue(135);
        d.property("ADBE Drop Shadow-0004").setValue(4);
        d.property("ADBE Drop Shadow-0005").setValue(18);
    } catch (e) {}
}

// Word-by-word reveal (keeps Arabic letters joined).
function revealWords(l, t0, dur, dy) {
    try {
    function AN() { return l.property("ADBE Text Properties").property("ADBE Text Animators"); }
    AN().addProperty("ADBE Text Animator");
    var ai = AN().numProperties;
    function A() { return AN().property(ai); }
    function PR() { return A().property("ADBE Text Animator Properties"); }
    PR().addProperty("ADBE Text Opacity");
    PR().property("ADBE Text Opacity").setValue(0);
    PR().addProperty("ADBE Text Position 3D");
    PR().property("ADBE Text Position 3D").setValue([0, dy === undefined ? 40 : dy, 0]);
    try { PR().addProperty("ADBE Text Blur"); PR().property("ADBE Text Blur").setValue([8, 8]); } catch (e) {}
    A().property("ADBE Text Selectors").addProperty("ADBE Text Selector");
    var sel = A().property("ADBE Text Selectors").property(1);
    var adv = sel.property("ADBE Text Range Advanced");
    try { adv.property("ADBE Text Range Type2").setValue(3); } catch (e) {}   // based on: words
    try { adv.property("ADBE Text Range Shape").setValue(2); } catch (e) {}   // ramp up
    try { adv.property("ADBE Text Levels Max Ease").setValue(60); } catch (e) {}
    keys(sel.property("ADBE Text Percent Offset"), [t0, t0 + dur], [0, 100], 70);
    } catch (e) { LOG.push(l.name + ": reveal animator — " + e.toString()); fadeIn(l, t0, dur * 0.6); }
}

function fadeIn(l, t0, dur, from) {
    var op = tr(l).property("ADBE Opacity");
    keys(op, [t0, t0 + dur], [0, 100]);
    if (from) {
        var pos = tr(l).property("ADBE Position");
        var v = pos.value;
        keys(pos, [t0, t0 + dur + 0.2], [[v[0] + from[0], v[1] + from[1]], v], 85);
    }
}

function contents(l) { return l.property("ADBE Root Vectors Group"); }
// fresh reference to the i-th item inside the named group of a shape layer
function item(l, groupName, i) { return contents(l).property(groupName).property("ADBE Vectors Group").property(i); }

function shapeGroup(l, name) {
    var g = contents(l).addProperty("ADBE Vector Group");
    g.name = name || "G";
    return g;
}
function addFill(g, color, op) {
    var fi = g.property("ADBE Vectors Group").addProperty("ADBE Vector Graphic - Fill");
    fi.property("ADBE Vector Fill Color").setValue(color);
    if (op !== undefined) fi.property("ADBE Vector Fill Opacity").setValue(op);
    return fi;
}
function addStroke(g, color, w) {
    var s = g.property("ADBE Vectors Group").addProperty("ADBE Vector Graphic - Stroke");
    s.property("ADBE Vector Stroke Color").setValue(color);
    s.property("ADBE Vector Stroke Width").setValue(w);
    try { s.property("ADBE Vector Stroke Line Cap").setValue(2); s.property("ADBE Vector Stroke Line Join").setValue(2); } catch (e) {}
    return s;
}

// Rectangle whose layer origin is its RIGHT-middle edge (so scale-X reveals right→left).
function rectR(comp, name, w, h, color, pos, op) {
    var l = comp.layers.addShape(); l.name = name;
    var g = shapeGroup(l, "Box");
    var r = g.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Rect");
    r.property("ADBE Vector Rect Size").setValue([w, h]);
    r.property("ADBE Vector Rect Position").setValue([-w / 2, 0]);
    addFill(g, color, op);
    tr(l).property("ADBE Position").setValue(pos);
    return l;
}

function pathShape(verts, closed, inT, outT) {
    var s = new Shape();
    s.vertices = verts; s.closed = closed !== false;
    if (inT) s.inTangents = inT;
    if (outT) s.outTangents = outT;
    return s;
}

function addPath(g, verts, closed) {
    var p = g.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Group");
    p.property("ADBE Vector Shape").setValue(pathShape(verts, closed));
    return p;
}

function trim(g, t0, dur) {
    var t = g.property("ADBE Vectors Group").addProperty("ADBE Vector Filter - Trim");
    keys(t.property("ADBE Vector Trim End"), [t0, t0 + dur], [0, 100], 75);
    return t;
}

function slider(l, name, times, values) {
    var e = l.property("ADBE Effect Parade").addProperty("ADBE Slider Control");
    e.name = name;
    keys(e.property(1), times, values, 75);
    return e;
}

// Counter: number layer driven by a slider. decimals: 0 or 1.
function counter(comp, name, target, t0, dur, o) {
    var l = text(comp, name, String(target), o);
    slider(l, "Count", [t0, t0 + dur], [o.from || 0, target]);
    var dec = o.decimals || 0;
    l.property("ADBE Text Properties").property("ADBE Text Document").expression =
        'var v=effect("Count")(1).value;' +
        (dec ? '(Math.abs(v)<0.05?0:v).toFixed(' + dec + ');' : 'Math.round(v).toString();');
    return l;
}

// Place a RTL text layer immediately to the LEFT of another layer (number + unit lines).
function stickLeftOf(l, refName, gap, dy) {
    tr(l).property("ADBE Position").expression =
        'var r=thisComp.layer("' + refName + '");var b=r.sourceRectAtTime(time,false);' +
        '[r.toComp([b.left,0])[0]-' + gap + ', r.position[1]+' + (dy || 0) + ']';
}

function plate(comp, item, scaleFrom, scaleTo, drift) {
    var l = comp.layers.add(item);
    l.name = "PLATE";
    var s = (CFG.W / item.width) * 100;
    var sc = tr(l).property("ADBE Scale");
    keys(sc, [0, comp.duration], [[s * scaleFrom, s * scaleFrom], [s * scaleTo, s * scaleTo]], 33);
    if (drift) {
        var p = tr(l).property("ADBE Position");
        keys(p, [0, comp.duration], [[CFG.W / 2 + drift[0], CFG.H / 2 + drift[1]], [CFG.W / 2, CFG.H / 2]], 33);
    }
    return l;
}

function placeholderPlate(comp, name) {
    var l = comp.layers.addSolid(CFG.GREY, name + " (MISSING PLATE)", CFG.W, CFG.H, 1);
    return l;
}

function vignette(comp, op) {
    var l = comp.layers.addSolid([0, 0, 0], "Vignette", CFG.W, CFG.H, 1);
    var m = l.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
    m.property("ADBE Mask Shape").setValue(pathShape([[160, 90], [1760, 90], [1760, 990], [160, 990]], true));
    m.inverted = true;
    m.property("ADBE Mask Feather").setValue([520, 520]);
    tr(l).property("ADBE Opacity").setValue(op || 55);
    return l;
}

// Soft grey scrim behind right-side captions.
function scrimRight(comp, op) {
    var l = comp.layers.addSolid(CFG.GREY, "Scrim", CFG.W, CFG.H, 1);
    var m = l.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
    m.property("ADBE Mask Shape").setValue(pathShape([[1080, -200], [2300, -200], [2300, 1280], [1080, 1280]], true));
    m.property("ADBE Mask Feather").setValue([420, 0]);
    tr(l).property("ADBE Opacity").setValue(op || 70);
    return l;
}

// Section tag (orange box + white Black text), e.g. "الأهداف:"
function sectionTag(comp, str, y, t0, animate) {
    var name = "TAG_TXT";
    var box = comp.layers.addShape(); box.name = "TAG_BOX";
    var g = shapeGroup(box, "Box");
    g.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Rect");
    addFill(contents(box).property("Box"), CFG.ORANGE);
    var t = text(comp, name, str, { w: "Black", size: 50, pos: [CFG.XR - 30, y], shadow: false });
    var r = item(box, "Box", 1);
    r.property("ADBE Vector Rect Size").expression =
        'var b=thisComp.layer("' + name + '").sourceRectAtTime(time,false);[b.width+60,b.height+34]';
    r.property("ADBE Vector Rect Position").expression =
        'var b=thisComp.layer("' + name + '").sourceRectAtTime(time,false);[-(b.width+60)/2,0]';
    tr(box).property("ADBE Position").expression =
        'var l=thisComp.layer("' + name + '");var b=l.sourceRectAtTime(time,false);[' + CFG.XR + ', l.position[1]+b.top+b.height/2]';
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

function headline(comp, str, y, t0, size, w) {
    var l = text(comp, "HEADLINE", str, { w: w || "Black", size: size || 84, pos: [CFG.XR, y] });
    revealWords(l, t0, 0.9, 50);
    return l;
}

function newComp(name, dur, folderItem) {
    var c = app.project.items.addComp(name, CFG.W, CFG.H, 1, dur, CFG.FPS);
    c.parentFolder = folderItem;
    return c;
}

// ───────────────────────────── BUILD ─────────────────────────────
app.beginUndoGroup("Build Green Initiative");

var proj = app.project || app.newProject();
var fRoot = proj.items.addFolder("GREEN_INITIATIVE");
var fScenes = proj.items.addFolder("Scenes"); fScenes.parentFolder = fRoot;
var fFoot = proj.items.addFolder("Footage"); fFoot.parentFolder = fRoot;

var vo = importIfExists("audio/vo.mp3", fFoot);
var voDur = vo ? vo.duration : 113.2;
var TOTAL = Math.ceil((voDur + CFG.END_PAD) * CFG.FPS) / CFG.FPS;

var PL = {};
for (var i = 0; i < ORDER.length; i++) PL[ORDER[i]] = importIfExists("plates/" + ORDER[i] + ".png", fFoot);
var TREES = [importIfExists("assets/tree1.png", fFoot), importIfExists("assets/tree2.png", fFoot), importIfExists("assets/tree3.png", fFoot)];
var PHOTO = importIfExists("assets/crown_prince.png", fFoot) || importIfExists("assets/crown_prince.jpg", fFoot);
var FLAG = importIfExists("assets/saudi_flag.png", fFoot);
var GUIDE = importIfExists("../channel-guide/safe-area-guide.png", fFoot);

function sceneLen(id) {
    var idx = 0; for (var i = 0; i < ORDER.length; i++) if (ORDER[i] === id) idx = i;
    var start = CFG.T[id];
    var end = (idx < ORDER.length - 1) ? CFG.T[ORDER[idx + 1]] + CFG.WIPE : TOTAL;
    return end - start;
}

function basePlate(c, id, s0, s1, drift) {
    if (PL[id]) return plate(c, PL[id], s0, s1, drift);
    return placeholderPlate(c, id);
}

var BUILD = {};

// S01 — opening: climate background, Saudi map + flag, general title
BUILD.S01 = function (c) {
    basePlate(c, "S01", 1.12, 1.0, [60, 0]);
    vignette(c, 45);
    // Map (Natural Earth outline), centre-left
    var MAP = [[-271.4,-148.7],[-241.8,-144.1],[-230.2,-153.0],[-223.9,-163.5],[-203.6,-167.6],[-199.2,-177.3],[-190.4,-182.3],[-216.9,-211.4],[-163.6,-226.0],[-158.5,-230.4],[-126.4,-222.5],[-86.8,-202.1],[-11.7,-143.5],[37.8,-141.2],[61.5,-138.4],[68.1,-124.5],[87.0,-125.2],[97.4,-100.1],[110.5,-93.5],[115.0,-83.2],[133.2,-71.0],[134.8,-58.9],[132.2,-49.2],[135.5,-39.4],[143.2,-31.3],[146.7,-21.7],[150.7,-14.6],[158.8,-8.8],[166.1,-10.9],[171.2,0.3],[172.2,7.0],[182.4,36.5],[262.4,51.2],[267.8,45.1],[280.0,65.7],[262.3,124.0],[182.4,153.1],[105.6,164.3],[80.8,177.4],[61.7,208.0],[49.3,212.9],[42.6,203.2],[32.4,204.6],[6.7,201.7],[1.8,198.8],[-28.9,199.5],[-36.2,202.1],[-47.1,194.5],[-54.1,208.8],[-51.4,221.1],[-63.1,230.4],[-66.6,218.0],[-74.6,209.2],[-76.6,197.6],[-90.4,187.1],[-104.6,162.7],[-112.1,139.0],[-130.5,118.9],[-142.4,114.1],[-160.0,86.3],[-163.1,66.1],[-162.0,48.8],[-177.2,16.5],[-189.7,5.1],[-204.1,-0.9],[-212.8,-17.6],[-211.4,-24.2],[-218.8,-39.3],[-226.6,-45.8],[-237.0,-67.5],[-253.2,-91.0],[-266.7,-111.0],[-280.0,-110.9],[-275.9,-126.9],[-274.7,-137.1]];
    var map = c.layers.addShape(); map.name = "MAP_KSA";
    var gF = shapeGroup(map, "Fill"); addPath(gF, MAP, true); var mf = addFill(gF, CFG.WHITE, 0);
    keys(mf.property("ADBE Vector Fill Opacity"), [1.2, 2.2], [0, 22]);
    var gS = shapeGroup(map, "Outline"); addPath(gS, MAP, true); addStroke(gS, CFG.WHITE, 4); trim(gS, 0.3, 1.8);
    var gG = shapeGroup(map, "Glow"); addPath(gG, MAP, true); addStroke(gG, CFG.ORANGE, 2); trim(gG, 0.5, 1.8);
    tr(map).property("ADBE Position").setValue([760, 395]);
    keys(tr(map).property("ADBE Scale"), [0.2, 2.6], [[92, 92], [100, 100]], 60);
    shadow(map, 40);
    // Riyadh pin
    var pin = c.layers.addShape(); pin.name = "PIN_RIYADH";
    var gp = shapeGroup(pin, "Dot");
    gp.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([18, 18]);
    addFill(gp, CFG.ORANGE);
    var gr = shapeGroup(pin, "Ring");
    gr.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Ellipse");
    addStroke(contents(pin).property("Ring"), CFG.ORANGE, 3);
    item(pin, "Ring", 1).property("ADBE Vector Ellipse Size").expression = 'var t=(time%1.6)/1.6;[18+70*t,18+70*t]';
    contents(pin).property("Ring").property("ADBE Vector Transform Group").property("ADBE Vector Group Opacity").expression = '100*(1-(time%1.6)/1.6)';
    tr(pin).property("ADBE Position").expression = 'thisComp.layer("MAP_KSA").toComp([41.8,-13.3])';
    fadeIn(pin, 2.0, 0.3);
    // Flag (official file if provided; otherwise a placeholder)
    var flag;
    if (FLAG) { flag = c.layers.add(FLAG); var fs = 340 / FLAG.width * 100; tr(flag).property("ADBE Scale").setValue([fs, fs]); }
    else {
        flag = c.layers.addSolid([0, 108 / 255, 53 / 255], "FLAG_PLACEHOLDER — replace with assets/saudi_flag.png", 340, 227, 1);
    }
    flag.name = "FLAG";
    tr(flag).property("ADBE Position").setValue([1290, 400]);
    try {
        var ww = flag.property("ADBE Effect Parade").addProperty("ADBE Wave Warp");
        ww.property(2).setValue(10); ww.property(3).setValue(240); ww.property(5).setValue(1.2);
    } catch (e) {}
    shadow(flag, 40);
    fadeIn(flag, 1.4, 0.6, [80, 0]);
    // Title
    var title = text(c, "TITLE", "مبادرة السعودية الخضراء",
        { w: "Black", size: 110, pos: [CFG.W / 2, 775], just: ParagraphJustification.CENTER_JUSTIFY });
    revealWords(title, 2.4, 1.0, 60);
    var bar = rectR(c, "TitleBar", 220, 8, CFG.ORANGE, [CFG.W / 2 + 110, 655]);
    keys(tr(bar).property("ADBE Scale"), [2.3, 2.9], [[0, 100], [100, 100]], 85);
};

// S02 — 2021 + crown prince photo
BUILD.S02 = function (c) {
    basePlate(c, "S02", 1.0, 1.1, [-40, 0]);
    // Photo frame (right)
    var fx = 1520, fy = 420, fw = 470, fh = 560;
    var frame = rectR(c, "PhotoFrame", fw + 16, fh + 16, CFG.WHITE, [fx + (fw + 16) / 2, fy]);
    var ph;
    if (PHOTO) {
        ph = c.layers.add(PHOTO);
        var ps = Math.max(fw / PHOTO.width, fh / PHOTO.height) * 100;
        tr(ph).property("ADBE Scale").setValue([ps, ps]);
        var m = ph.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
        var cx = PHOTO.width / 2, cy = PHOTO.height / 2, hw = fw / 2 / (ps / 100), hh = fh / 2 / (ps / 100);
        m.property("ADBE Mask Shape").setValue(pathShape([[cx - hw, cy - hh], [cx + hw, cy - hh], [cx + hw, cy + hh], [cx - hw, cy + hh]], true));
    } else {
        ph = c.layers.addSolid([0.55, 0.55, 0.55], "PHOTO_PLACEHOLDER — put assets/crown_prince.png", fw, fh, 1);
    }
    ph.name = "PHOTO";
    tr(ph).property("ADBE Position").setValue([fx, fy]);
    ph.moveBefore(frame);
    var orange = rectR(c, "PhotoAccent", 14, fh + 16, CFG.ORANGE, [fx + fw / 2 + 22, fy]);
    shadow(frame, 50);
    keys(tr(frame).property("ADBE Scale"), [0.3, 0.9], [[0, 100], [100, 100]], 85);
    keys(tr(orange).property("ADBE Scale"), [0.2, 0.6], [[100, 0], [100, 100]], 85);
    fadeIn(ph, 0.7, 0.5, [60, 0]);
    // 2021
    var yr = counter(c, "YEAR", 2021, 0.6, 1.4, { from: 1990, w: "Black", size: 300, pos: [1180, 520], rtl: false, color: CFG.WHITE });
    fadeIn(yr, 0.6, 0.4, [0, 40]);
    accentBar(c, 1180, 580, 300, 1.4);
    // Caption
    var cap = text(c, "CAPTION", "أطلقها ولي العهد السعودي\rالأمير محمد بن سلمان", { w: "Bold", size: 60, pos: [1180, 690] });
    revealWords(cap, 1.6, 1.0, 40);
};

// S03 — climate change & rain
BUILD.S03 = function (c) {
    basePlate(c, "S03", 1.0, 1.12, [0, -20]);
    try {
        var rain = c.layers.addSolid([0, 0, 0], "Rain", CFG.W, CFG.H, 1);
        rain.property("ADBE Effect Parade").addProperty("CC Rainfall");
        rain.blendingMode = BlendingMode.SCREEN;
        tr(rain).property("ADBE Opacity").setValue(70);
    } catch (e) {}
    scrimRight(c, 65);
    accentBar(c, CFG.XR, 380, 160, 0.4);
    headline(c, "التصدي للتغيرات\rالمناخية", 490, 0.5, 96);
};

function goalsScene(c, id, line, tagAnim, plateArgs) {
    basePlate(c, id, plateArgs[0], plateArgs[1], plateArgs[2]);
    scrimRight(c, 60);
    sectionTag(c, "الأهداف:", 330, 0.25, tagAnim);
    return headline(c, line, 470, 0.5, 86);
}

// S04 — green economy
BUILD.S04 = function (c) {
    goalsScene(c, "S04", "الانتقال نحو\rالاقتصاد الأخضر", true, [1.0, 1.1, [-30, 10]]);
    var ln = c.layers.addShape(); ln.name = "UpTrend";
    var g = shapeGroup(ln, "Line");
    addPath(g, [[160, 820], [330, 740], [470, 770], [640, 610], [780, 640], [960, 430]], false);
    addStroke(g, CFG.ORANGE, 8); trim(g, 0.6, 1.6);
    var h = shapeGroup(ln, "Head");
    addPath(h, [[905, 440], [960, 430], [955, 486]], false);
    addStroke(h, CFG.ORANGE, 8);
    keys(contents(ln).property("Head").property("ADBE Vector Transform Group").property("ADBE Vector Group Opacity"), [2.1, 2.3], [0, 100]);
    shadow(ln, 35);
};

// S05 — emissions / CO2
BUILD.S05 = function (c) {
    goalsScene(c, "S05", "تقليل الانبعاثات\rالكربونية", false, [1.0, 1.08, [20, 0]]);
    var orb = c.layers.addShape(); orb.name = "CO2_ORB";
    var g = shapeGroup(orb, "Orb");
    g.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Ellipse").property("ADBE Vector Ellipse Size").setValue([280, 280]);
    addFill(g, CFG.GREY, 55); addStroke(g, CFG.WHITE, 4);
    tr(orb).property("ADBE Position").setValue([760, 360]);
    keys(tr(orb).property("ADBE Scale"), [0.3, 0.8], [[0, 0], [100, 100]], 85);
    var co = text(c, "CO2", "CO", { w: "Black", size: 120, pos: [745, 400], rtl: false, just: ParagraphJustification.CENTER_JUSTIFY });
    var two = text(c, "CO2_sub", "2", { w: "Black", size: 64, pos: [838, 430], rtl: false, just: ParagraphJustification.LEFT_JUSTIFY });
    fadeIn(co, 0.6, 0.3); fadeIn(two, 0.7, 0.3);
    tr(orb).property("ADBE Position").expression = 'value+[0,Math.sin(time*1.6)*8]';
    // three orange chevrons sliding down
    for (var i = 0; i < 3; i++) {
        var ch = c.layers.addShape(); ch.name = "Down_" + (i + 1);
        var cg = shapeGroup(ch, "Chevron");
        addPath(cg, [[-60, -30], [0, 30], [60, -30]], false);
        addStroke(cg, CFG.ORANGE, 16);
        tr(ch).property("ADBE Position").setValue([760, 560 + i * 70]);
        tr(ch).property("ADBE Opacity").expression =
            'var t=time-' + (0.9 + i * 0.15) + ';t<0?0:(50+50*Math.sin(t*5-' + i + '))';
        tr(ch).property("ADBE Position").expression = 'var t=Math.max(0,time-0.9);value+[0,(t*40)%30]';
    }
};

// S06 — afforestation: trees appear one after another
BUILD.S06 = function (c) {
    goalsScene(c, "S06", "التوسع في التشجير\rوحماية البيئة", false, [1.0, 1.06, [0, 0]]);
    var horizon = 412;
    var spots = [[1060, 455], [990, 470], [905, 490], [810, 515], [700, 550], [575, 600], [430, 670], [270, 760], [90, 880],
                 [560, 470], [420, 485], [260, 505]];
    // insert nearest first so nearer trees stay in front (each insert goes just above the plate)
    var idx = []; for (var k = 0; k < spots.length; k++) idx.push(k);
    idx.sort(function (a, b) { return spots[b][1] - spots[a][1]; });
    var plateL = c.layer("PLATE");
    for (var q = 0; q < idx.length; q++) {
        var i = idx[q];
        var it = TREES[i % 3]; if (!it) continue;
        var t = c.layers.add(it); t.name = "Tree_" + (i + 1);
        var x = spots[i][0], y = spots[i][1];
        var s = (y - horizon) / (880 - horizon) * 75;   // perspective scale
        tr(t).property("ADBE Anchor Point").setValue([it.width / 2, it.height - 20]);
        tr(t).property("ADBE Position").setValue([x, y]);
        var t0 = 0.5 + i * 0.32;
        keys(tr(t).property("ADBE Scale"), [t0, t0 + 0.35, t0 + 0.55], [[0, 0], [s * 1.08, s * 1.08], [s, s]], 70);
        t.moveBefore(plateL);
    }
};

function plansScene(c, id, tagAnim, plateArgs) {
    basePlate(c, id, plateArgs[0], plateArgs[1], plateArgs[2]);
    scrimRight(c, 55);
    sectionTag(c, "الخطط:", 300, 0.25, tagAnim);
}

// S07 — 700 billion riyals
BUILD.S07 = function (c) {
    plansScene(c, "S07", true, [1.12, 1.0, [0, 30]]);
    var l1 = text(c, "LINE1", "استثمارات بقيمة", { w: "Bold", size: 66, pos: [CFG.XR, 430] });
    revealWords(l1, 0.5, 0.7, 40);
    var n = counter(c, "NUM", 700, 0.9, 1.6, { w: "Black", size: 230, pos: [CFG.XR, 650], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 0.9, 0.3, [0, 40]);
    var u = text(c, "UNIT", "مليار ريال", { w: "Bold", size: 84, pos: [0, 0] });
    stickLeftOf(u, "NUM", 30, 0);
    fadeIn(u, 1.2, 0.4);
};

// S08 — 77 programmes
BUILD.S08 = function (c) {
    plansScene(c, "S08", false, [1.0, 1.1, [40, 0]]);
    var n = counter(c, "NUM", 77, 0.4, 1.2, { w: "Black", size: 250, pos: [CFG.XR, 620], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 0.4, 0.3, [0, 40]);
    var u = text(c, "UNIT", "برنامجا متكاملا", { w: "Bold", size: 84, pos: [0, 0] });
    stickLeftOf(u, "NUM", 34, 0);
    fadeIn(u, 0.8, 0.4);
};

// Spreading green: the plate is "desertified" underneath and the real plate grows back over it.
function spreadGreen(c, id, originXY, t0, dur, endExpand) {
    var base = c.layer("PLATE");
    var dry = base.duplicate(); dry.name = "PLATE_DRY"; dry.moveAfter(base);
    try {
        var tint = dry.property("ADBE Effect Parade").addProperty("ADBE Tint");
        tint.property(1).setValue([0.32, 0.22, 0.10, 1]);
        tint.property(2).setValue([0.96, 0.84, 0.62, 1]);
        tint.property(3).setValue(100);
    } catch (e) {}
    var m = base.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
    var w = PL[id] ? PL[id].width : CFG.W, h = PL[id] ? PL[id].height : CFG.H;
    var ox = originXY[0] * w, oy = originXY[1] * h, r = 40;
    m.property("ADBE Mask Shape").setValue(pathShape([[ox - r, oy - r], [ox + r, oy - r], [ox + r, oy + r], [ox - r, oy + r]], true));
    m.property("ADBE Mask Feather").setValue([160, 160]);
    keys(m.property("ADBE Mask Offset"), [t0, t0 + dur], [0, endExpand], 50);
}

function achievementsScene(c, id, tagAnim, plateArgs) {
    basePlate(c, id, plateArgs[0], plateArgs[1], plateArgs[2]);
    scrimRight(c, 72);
    sectionTag(c, "الإنجازات:", 270, 0.25, tagAnim);
}

// S09 — 100 million trees / 118 thousand hectares
BUILD.S09 = function (c) {
    achievementsScene(c, "S09", true, [1.0, 1.12, [0, 0]]);
    spreadGreen(c, "S09", [0.12, 0.85], 0.2, 6.0, 1400);
    var a1 = text(c, "A1_WORD", "زراعة", { w: "Bold", size: 60, pos: [CFG.XR, 390] }); revealWords(a1, 0.6, 0.5, 30);
    var n1 = counter(c, "A1_NUM", 100, 0.8, 1.4, { w: "Black", size: 170, pos: [CFG.XR, 550], rtl: false, color: CFG.ORANGE });
    fadeIn(n1, 0.8, 0.3, [0, 30]);
    var u1 = text(c, "A1_UNIT", "مليون شجرة", { w: "Bold", size: 70, pos: [0, 0] }); stickLeftOf(u1, "A1_NUM", 28, 0); fadeIn(u1, 1.1, 0.4);
    var tB = 4.5;
    var a2 = text(c, "A2_WORD", "استصلاح", { w: "Bold", size: 60, pos: [CFG.XR, 668] }); revealWords(a2, tB, 0.5, 30);
    var n2 = counter(c, "A2_NUM", 118, tB + 0.2, 1.4, { w: "Black", size: 150, pos: [CFG.XR, 805], rtl: false, color: CFG.WHITE });
    fadeIn(n2, tB + 0.2, 0.3, [0, 30]);
    var u2 = text(c, "A2_UNIT", "ألف هكتارا", { w: "Bold", size: 64, pos: [0, 0] }); stickLeftOf(u2, "A2_NUM", 28, 0); fadeIn(u2, tB + 0.5, 0.4);
    var sep = rectR(c, "Divider", 520, 3, CFG.WHITE, [CFG.XR, 585], 60);
    keys(tr(sep).property("ADBE Scale"), [tB - 0.3, tB + 0.2], [[0, 100], [100, 100]], 85);
};

// S10 — 1150 field surveys (bigger spread)
BUILD.S10 = function (c) {
    achievementsScene(c, "S10", false, [1.25, 1.0, [0, -60]]);
    spreadGreen(c, "S10", [0.5, 0.45], 0.1, 5.0, 1700);
    var n = counter(c, "NUM", 1150, 0.5, 1.8, { w: "Black", size: 230, pos: [CFG.XR, 560], rtl: false, color: CFG.ORANGE });
    fadeIn(n, 0.5, 0.3, [0, 40]);
    var u = text(c, "UNIT", "مسحا ميدانيا", { w: "Bold", size: 84, pos: [CFG.XR, 690] });
    revealWords(u, 1.0, 0.7, 30);
};

// S11 — Riyadh, thermometer, -2.2
BUILD.S11 = function (c) {
    basePlate(c, "S11", 1.0, 1.1, [-50, 0]);
    scrimRight(c, 55);
    headline(c, "انخفاض درجة حرارة\rمراكز المدن", 260, 0.4, 76);
    // Thermometer
    var th = c.layers.addShape(); th.name = "Thermometer";
    var tube = shapeGroup(th, "Tube");
    var rr = tube.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Rect");
    rr.property("ADBE Vector Rect Size").setValue([46, 300]); rr.property("ADBE Vector Rect Roundness").setValue(23);
    rr.property("ADBE Vector Rect Position").setValue([0, -150]);
    addFill(contents(th).property("Tube"), CFG.WHITE, 25); addStroke(contents(th).property("Tube"), CFG.WHITE, 5);
    shapeGroup(th, "Bulb");
    contents(th).property("Bulb").property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Ellipse");
    item(th, "Bulb", 1).property("ADBE Vector Ellipse Size").setValue([96, 96]);
    item(th, "Bulb", 1).property("ADBE Vector Ellipse Position").setValue([0, 30]);
    addFill(contents(th).property("Bulb"), CFG.ORANGE); addStroke(contents(th).property("Bulb"), CFG.WHITE, 5);
    shapeGroup(th, "Mercury"); var merc = contents(th).property("Mercury");
    merc.property("ADBE Vectors Group").addProperty("ADBE Vector Shape - Rect");
    item(th, "Mercury", 1).property("ADBE Vector Rect Roundness").setValue(10);
    addFill(contents(th).property("Mercury"), CFG.ORANGE);
    slider(th, "Level", [1.0, 2.6], [250, 120]);
    var mr = item(th, "Mercury", 1);
    mr.property("ADBE Vector Rect Size").expression = '[20, effect("Level")(1)]';
    mr.property("ADBE Vector Rect Position").expression = '[0, -effect("Level")(1)/2]';
    for (var i = 0; i < 5; i++) {
        var tk = shapeGroup(th, "Tick" + i);
        addPath(tk, [[34, -60 - i * 55], [54, -60 - i * 55]], false); addStroke(tk, CFG.WHITE, 3);
    }
    tr(th).property("ADBE Position").setValue([1720, 700]);
    fadeIn(th, 0.6, 0.5, [0, 40]);
    shadow(th, 35);
    // -2.2 درجة   (number on the right, word to its left)
    var n = counter(c, "NUM", -2.2, 1.0, 1.6, { from: 0, decimals: 1, w: "Black", size: 210, pos: [1610, 700], rtl: false, color: CFG.WHITE });
    fadeIn(n, 1.0, 0.3, [0, 30]);
    var u = text(c, "UNIT", "درجة", { w: "Bold", size: 84, pos: [0, 0] });
    stickLeftOf(u, "NUM", 28, 0);
    fadeIn(u, 1.3, 0.4);
};

// S12 — OUT shot + title in the middle
BUILD.S12 = function (c) {
    basePlate(c, "S12", 1.35, 1.0, [0, 40]);
    vignette(c, 60);
    var title = text(c, "TITLE", "مبادرة السعودية الخضراء",
        { w: "Black", size: 120, pos: [CFG.W / 2, 560], just: ParagraphJustification.CENTER_JUSTIFY });
    revealWords(title, 1.0, 1.1, 60);
    var b1 = rectR(c, "BarTop", 240, 8, CFG.ORANGE, [CFG.W / 2 + 120, 410]);
    var b2 = rectR(c, "BarBottom", 240, 8, CFG.ORANGE, [CFG.W / 2 + 120, 625]);
    keys(tr(b1).property("ADBE Scale"), [0.9, 1.5], [[0, 100], [100, 100]], 85);
    keys(tr(b2).property("ADBE Scale"), [1.1, 1.7], [[0, 100], [100, 100]], 85);
};

// ── Main comp ──
var main = newComp("GREEN_INITIATIVE_MAIN", TOTAL, fRoot);
main.parentFolder = fRoot;

for (var s = 0; s < ORDER.length; s++) {
    var id = ORDER[s];
    var len = sceneLen(id);
    var sc = newComp(id, len, fScenes);
    try { BUILD[id](sc); } catch (err) { LOG.push(id + ": " + err.toString() + " (line " + err.line + ")"); }
    var L = main.layers.add(sc);
    L.startTime = CFG.T[id];
    L.name = id;
    if (s > 0) {
        // right → left reveal (RTL) with an orange + grey bar riding the edge
        var t0 = CFG.T[id], t1 = t0 + CFG.WIPE;
        var m = L.property("ADBE Mask Parade").addProperty("ADBE Mask Atom");
        var mp = m.property("ADBE Mask Shape");
        mp.setValueAtTime(t0, pathShape([[CFG.W, -10], [CFG.W + 10, -10], [CFG.W + 10, CFG.H + 10], [CFG.W, CFG.H + 10]], true));
        mp.setValueAtTime(t1, pathShape([[-200, -10], [CFG.W + 10, -10], [CFG.W + 10, CFG.H + 10], [-200, CFG.H + 10]], true));
        easeKeys(mp, 75);
        var bo = rectR(main, "Wipe_O_" + id, 70, CFG.H + 20, CFG.ORANGE, [CFG.W + 70, CFG.H / 2]);
        keys(tr(bo).property("ADBE Position"), [t0, t1], [[CFG.W + 70, CFG.H / 2], [-130, CFG.H / 2]], 75);
        bo.inPoint = t0; bo.outPoint = t1 + 0.04;
        var bg = rectR(main, "Wipe_G_" + id, 26, CFG.H + 20, CFG.GREY, [CFG.W + 96, CFG.H / 2]);
        keys(tr(bg).property("ADBE Position"), [t0, t1], [[CFG.W + 96, CFG.H / 2], [-104, CFG.H / 2]], 75);
        bg.inPoint = t0; bg.outPoint = t1 + 0.04;
    }
    try { var mk = new MarkerValue(id); main.markerProperty.setValueAtTime(CFG.T[id], mk); } catch (e) {}
}

if (vo) { var a = main.layers.add(vo); a.name = "VO"; a.moveToBeginning(); }
if (GUIDE) {
    var gl = main.layers.add(GUIDE); gl.name = "SAFE AREA GUIDE (does not render)";
    gl.guideLayer = true; tr(gl).property("ADBE Opacity").setValue(60); gl.moveToBeginning();
}

main.openInViewer();
try { var lf = f("build_log.txt"); lf.encoding = "UTF-8"; lf.open("w"); lf.write(LOG.length ? LOG.join("\n") : "OK — no errors"); lf.close(); } catch (e) {}
app.endUndoGroup();

alert("تم بناء المشروع ✔\n\nComp: GREEN_INITIATIVE_MAIN (" + TOTAL.toFixed(2) + "s)\n" +
      "Fonts: " + font("Black") + " / " + font("Bold") + " / " + font("Regular") + "\n" +
      (PHOTO ? "" : "• ضع صورة ولي العهد في assets/crown_prince.png\n") +
      (FLAG ? "" : "• ضع العلم الرسمي في assets/saudi_flag.png\n") +
      "• عدّل توقيتات المشاهد من CFG.T في أول السكريبت لو احتاجت.\n" +
      (LOG.length ? "\n⚠ " + LOG.length + " ملاحظة — التفاصيل في build_log.txt جنب السكريبت" : "\nبدون أخطاء"));
})();
