const fs = require("fs");
const path = require("path");
const Module = require("module");

const SKILL_NODE_MODULES = __SKILL_NODE_MODULES__;
process.env.NODE_PATH = [SKILL_NODE_MODULES, process.env.NODE_PATH || ""].filter(Boolean).join(path.delimiter);
Module._initPaths();

const pptxgen = require("pptxgenjs");
const { svgToDataUri, warnIfSlideElementsOutOfBounds } = require("./pptxgenjs_helpers");

const SHAPE = (new pptxgen()).ShapeType;
const PPT_W = 13.333;
const PPT_H = 7.5;
const MIN_FONT_PT = 13.5; // 18px minimum readable text floor
const LAYOUT_ROOT = path.join(__dirname, "assets", "reference-layouts");
const SVG_FILES = { cover: "01_cover.svg", chapter: "02_chapter.svg", toc: "02_toc.svg", content: "03_content.svg", ending: "04_ending.svg" };
const SHELL_CACHE = new Map();

const THEMES = {
  academic_defense: { head: "Microsoft YaHei", body: "Microsoft YaHei", primary: "003366", accent: "0066CC", accent2: "CC0000", soft: "E8F4FC", softAlt: "F7FAFD", line: "D0D7E0", ink: "243143", muted: "5E6B7A", subtle: "94A3B8", white: "FFFFFF", radius: 0.08, chipRadius: 0.05, shadowColor: "AAB6C3" },
  medical_university: { head: "Microsoft YaHei", body: "Microsoft YaHei", primary: "0066B3", accent: "00A86B", accent2: "FF6B35", soft: "E6F3FA", softAlt: "F5FAFC", line: "D0D7E0", ink: "21414A", muted: "55737B", subtle: "8FA7AF", white: "FFFFFF", radius: 0.08, chipRadius: 0.05, shadowColor: "AAB6C3" },
  academic_premium: { head: "Segoe UI", body: "Segoe UI", primary: "163A5F", accent: "1E40AF", accent2: "D4AF37", soft: "EEF3F7", softAlt: "FBFCFE", line: "D9E3EB", ink: "1F3347", muted: "627A8D", subtle: "92A4B3", white: "FFFFFF", radius: 0.08, chipRadius: 0.06, shadowColor: "9AA8B5" },
  mckinsey: { head: "Segoe UI", body: "Segoe UI", primary: "163A5F", accent: "2C8CA7", accent2: "7BC242", soft: "EAF4F7", softAlt: "F7FAFC", line: "D7E5EC", ink: "203243", muted: "60788A", subtle: "8AA0AF", white: "FFFFFF", radius: 0.06, chipRadius: 0.05, shadowColor: "A2AFBA" },
  google_style: { head: "Segoe UI", body: "Segoe UI", primary: "1A73E8", accent: "34A853", accent2: "EA4335", soft: "E8F0FE", softAlt: "F8FBFF", line: "DADCE0", ink: "202124", muted: "5F6368", subtle: "9AA0A6", white: "FFFFFF", radius: 0.14, chipRadius: 0.08, shadowColor: "B6BCC4" },
  exhibit: { head: "Segoe UI", body: "Segoe UI", primary: "111827", accent: "6366F1", accent2: "D4AF37", soft: "F6F3EE", softAlt: "FCFAF6", line: "E4D7C4", ink: "2C241B", muted: "6B6258", subtle: "948B81", white: "FFFFFF", radius: 0.07, chipRadius: 0.05, shadowColor: "A79A88" },
  anthropic: { head: "Segoe UI", body: "Segoe UI", primary: "1A1A2E", accent: "4A90D9", accent2: "D97757", soft: "F5EDE4", softAlt: "FBF8F2", line: "E7D8C8", ink: "2E261E", muted: "6C655D", subtle: "9A938A", white: "FFFFFF", radius: 0.12, chipRadius: 0.08, shadowColor: "B4A89B" }
};

const DESIGN_RECIPES = {
  academic_precision: { theme: "academic_defense", tone: "classic", shell: { cover: "academic_defense", toc: "academic_defense", chapter: "academic_defense", content: "academic_defense", ending: "academic_defense" } },
  medical_precision: { theme: "medical_university", tone: "classic", shell: { cover: "medical_university", toc: "medical_university", chapter: "medical_university", content: "medical_university", ending: "medical_university" } },
  academic_premium: { theme: "academic_premium", tone: "executive", shell: { cover: "exhibit", toc: "mckinsey", chapter: "exhibit", content: "google_style", ending: "exhibit" } },
  executive_premium: { theme: "mckinsey", tone: "executive", shell: { cover: "mckinsey", toc: "mckinsey", chapter: "mckinsey", content: "mckinsey", ending: "mckinsey" } },
  product_modern: { theme: "google_style", tone: "product", shell: { cover: "google_style", toc: "google_style", chapter: "google_style", content: "google_style", ending: "google_style" } },
  editorial_premium: { theme: "exhibit", tone: "editorial", shell: { cover: "exhibit", toc: "exhibit", chapter: "exhibit", content: "exhibit", ending: "exhibit" } },
  ai_modern: { theme: "anthropic", tone: "ai", shell: { cover: "anthropic", toc: "anthropic", chapter: "anthropic", content: "google_style", ending: "anthropic" } },
  campus_academic: { theme: "academic_premium", tone: "executive", shell: { cover: "exhibit", toc: "mckinsey", chapter: "exhibit", content: "google_style", ending: "exhibit" }, defaultBranding: "subtle_badge" },
  campus_medical: { theme: "medical_university", tone: "classic", shell: { cover: "medical_university", toc: "medical_university", chapter: "medical_university", content: "medical_university", ending: "medical_university" }, defaultBranding: "subtle_badge" }
};

const LEGACY_DESIGN_MAP = {
  academic_defense: "academic_precision",
  medical_university: "medical_precision",
  mckinsey: "executive_premium",
  google_style: "product_modern",
  exhibit: "editorial_premium",
  anthropic: "ai_modern",
  "重庆大学": "campus_academic",
  chongqing_university: "campus_academic",
  chongqing: "campus_academic",
  cqu: "campus_academic"
};

const BRAND_PROFILES = {
  "重庆大学": {
    wordmark: "重庆大学",
    submark: "CHONGQING UNIVERSITY",
    logoPath: path.join(LAYOUT_ROOT, "重庆大学", "重庆大学logo.png"),
    accent: "D4A84B",
    fullShell: "重庆大学"
  },
  "chongqing university": {
    wordmark: "重庆大学",
    submark: "CHONGQING UNIVERSITY",
    logoPath: path.join(LAYOUT_ROOT, "重庆大学", "重庆大学logo.png"),
    accent: "D4A84B",
    fullShell: "重庆大学"
  },
  cqu: {
    wordmark: "重庆大学",
    submark: "CHONGQING UNIVERSITY",
    logoPath: path.join(LAYOUT_ROOT, "重庆大学", "重庆大学logo.png"),
    accent: "D4A84B",
    fullShell: "重庆大学"
  }
};

const FALLBACK_PLAN = {
  deck_identity: { title: process.env.DECK_TITLE || "Academic Defense", output_pptx: "academic-defense.pptx", visual_direction: "academic_premium" },
  slides: [
    { key: "cover", slide_type: "cover", title: process.env.DECK_TITLE || "Academic Defense", subtitle: "", speaker_note: "" },
    { key: "toc", slide_type: "toc", title: "Agenda", agenda_items: [], speaker_note: "" },
    { key: "background", slide_type: "content", title: "Research Background", takeaway: "State the problem, context, and why it matters.", bullets: ["Background", "Problem", "Value"], source_ids: [], visual: { type: "none" }, speaker_note: "" },
    { key: "thanks", slide_type: "closing", title: "Thank you for your attention", speaker_note: "" }
  ]
};

const SECTION_COPY = {
  background: { zh: { title: "研究背景", desc: "问题场景与选题意义" }, en: { title: "Research Background", desc: "Context, motivation, and topic value" } },
  problem: { zh: { title: "问题定义", desc: "研究目标与约束条件" }, en: { title: "Problem Definition", desc: "Objective, scope, and success criteria" } },
  technical_route: { zh: { title: "技术路线", desc: "总体框架与系统路径" }, en: { title: "Technical Route", desc: "Overall framework and system path" } },
  student_work_1: { zh: { title: "本人工作", desc: "核心设计与方法贡献" }, en: { title: "Core Contribution", desc: "Main design and method contribution" } },
  student_work_2: { zh: { title: "实现细节", desc: "关键实现与优化策略" }, en: { title: "Implementation Detail", desc: "Key implementation and optimization" } },
  experiment: { zh: { title: "实验设计", desc: "数据、指标与对比方案" }, en: { title: "Evaluation Design", desc: "Datasets, metrics, and baselines" } },
  results: { zh: { title: "核心结果", desc: "关键证据与效果解读" }, en: { title: "Core Results", desc: "Key evidence and result interpretation" } },
  innovation: { zh: { title: "创新总结", desc: "创新点与证据支撑" }, en: { title: "Innovation Summary", desc: "Novelty statements and supporting evidence" } },
  limitations: { zh: { title: "局限与展望", desc: "工作边界与后续方向" }, en: { title: "Boundary and Future Work", desc: "Limitations, scope, and next steps" } }
};

const CHAPTER_BREAKS = {
  background: { num: "01", zh: { title: "研究背景与问题", desc: "从场景、需求与目标出发" }, en: { title: "Research Context", desc: "Start from scenario, need, and objective" } },
  technical_route: { num: "02", zh: { title: "方法路径与实现", desc: "说明技术路线与本人工作" }, en: { title: "Method and Contribution", desc: "Explain the route and the student's work" } },
  experiment: { num: "03", zh: { title: "验证设计与结果", desc: "用可检验证据回答答辩问题" }, en: { title: "Evaluation and Findings", desc: "Use defensible evidence to answer the committee" } },
  innovation: { num: "04", zh: { title: "结论与展望", desc: "回收创新点、局限与未来工作" }, en: { title: "Conclusion and Outlook", desc: "Close on innovation, boundaries, and future work" } }
};

const LAYOUT_GUARDRAILS = {
  default: { maxBullets: 3, themeLabelSize: 13.5, themeSentenceSize: 13.5 }
};

const tx = (v) => String(v || "").replace(/\s+/g, " ").trim();
const safe = (v, n) => tx(v).length > n ? `${tx(v).slice(0, Math.max(n - 1, 1)).trim()}...` : tx(v);
const decode = (v) => String(v || "").replace(/\\u([0-9a-fA-F]{4})/g, (_, h) => String.fromCharCode(parseInt(h, 16)));
const hasHan = (v) => /[\u4e00-\u9fff]/.test(String(v || ""));
const xml = (v) => decode(v).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const pt = (v) => Math.max(v || MIN_FONT_PT, MIN_FONT_PT);

function isZh(plan) { return /zh|chinese/i.test(String(plan.deck_identity?.language || "")) || hasHan(plan.deck_identity?.title || ""); }
function tr(plan, zhText, enText) { return isZh(plan) ? zhText : enText; }
function readJson(file, fallback) {
  if (!fs.existsSync(file)) return fallback;
  const text = fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "");
  return JSON.parse(text);
}
function normalizeKey(value) { return String(value || "").trim().replace(/\s+/g, " ").toLowerCase(); }
function deckPlan() { return readJson(path.join(__dirname, "deck_plan.json"), FALLBACK_PLAN); }
function sourceLine(slideDef) { return (slideDef.source_ids || []).length ? slideDef.source_ids.join(" | ") : "--"; }
function sectionCopy(plan, key) { return SECTION_COPY[key]?.[isZh(plan) ? "zh" : "en"] || { title: safe(key.replace(/_/g, " "), 28), desc: "" }; }
function shellProfileExists(value) { return fs.existsSync(path.join(LAYOUT_ROOT, value)); }
function themeFor(name) { return THEMES[name] || THEMES.academic_premium; }

function splitTitle(text, firstLen = 44) {
  const value = tx(text);
  if (value.length <= firstLen) return [value, ""];
  const words = value.split(" ");
  if (words.length <= 1) return [safe(value, firstLen), safe(value.slice(firstLen), firstLen)];
  const first = [];
  let count = 0;
  while (words.length && count + words[0].length + (first.length ? 1 : 0) <= firstLen) {
    const next = words.shift();
    first.push(next);
    count += next.length + (first.length > 1 ? 1 : 0);
  }
  return [first.join(" "), safe(words.join(" "), firstLen)];
}

function blankTokens(svg) {
  return svg.replace(/\{\{\s*[A-Z0-9_]+\s*\}\}/g, "").replace(/[^\s<>{}]\{\s*[A-Z0-9_]+\s*\}\}/g, "");
}

function inlineLocalRefs(svg, baseDir) {
  return svg.replace(/(xlink:href|href)="([^"]+)"/g, (full, attr, href) => {
    if (/^(data:|https?:|#)/i.test(href)) return full;
    const file = path.resolve(baseDir, href);
    if (!fs.existsSync(file)) return full;
    const ext = path.extname(file).toLowerCase();
    const mime = ext === ".png" ? "image/png" : ext === ".jpg" || ext === ".jpeg" ? "image/jpeg" : ext === ".svg" ? "image/svg+xml" : null;
    if (!mime) return full;
    return `${attr}="data:${mime};base64,${fs.readFileSync(file).toString("base64")}"`;
  });
}

function sanitizeShellSvg(svg, profile, kind) {
  let out = svg;
  if (profile === "exhibit") {
    out = out.replace(/<text\b[^>]*>\s*CONFIDENTIAL\s*<\/text>\s*/gi, "");
  }
  if (kind === "content") {
    out = out.replace(/<rect\b[^>]*stroke-dasharray="[^"]+"[^>]*\/>\s*/g, "");
    out = out.replace(/<text\b[^>]*>\s*\{\{\s*CONTENT_AREA\s*\}\}\s*<\/text>\s*/g, "");
    out = out.replace(/<text\b[^>]*>[\s\S]*?Content Area:[\s\S]*?<\/text>\s*/g, "");
    out = out.replace(/<text\b[^>]*>[\s\S]*?Executor[\s\S]*?<\/text>\s*/g, "");
    if (["google_style", "mckinsey", "exhibit", "academic_defense", "medical_university", "anthropic"].includes(profile)) {
      out = out.replace(/\{\{\s*CONTENT_AREA\s*\}\}/g, "");
    }
  }
  return out;
}

function fillSvg(svg, vars) {
  let out = svg;
  Object.entries(vars || {}).forEach(([key, value]) => {
    const escaped = xml(value || "");
    out = out.replace(new RegExp(`\\{\\{\\s*${key}\\s*\\}\\}`, "g"), () => escaped);
    out = out.replace(new RegExp(`[^\\s<>{}]\\{\\s*${key}\\s*\\}\\}`, "g"), () => escaped);
  });
  return blankTokens(out);
}

function loadShell(profile, kind, vars) {
  const cacheKey = `${profile}:${kind}:${JSON.stringify(vars || {})}`;
  if (SHELL_CACHE.has(cacheKey)) return SHELL_CACHE.get(cacheKey);
  const dir = path.join(LAYOUT_ROOT, profile);
  let svg = fs.readFileSync(path.join(dir, SVG_FILES[kind]), "utf8");
  svg = inlineLocalRefs(svg, dir);
  svg = sanitizeShellSvg(svg, profile, kind);
  const uri = svgToDataUri(fillSvg(svg, vars));
  SHELL_CACHE.set(cacheKey, uri);
  return uri;
}

function resolveRecipeName(plan) {
  const requested = String(plan.deck_identity?.design_profile || plan.deck_identity?.visual_direction || "").trim();
  if (!requested) return "academic_premium";
  if (DESIGN_RECIPES[requested]) return requested;
  const mapped = LEGACY_DESIGN_MAP[normalizeKey(requested)];
  return mapped || "academic_premium";
}

function resolveBrand(plan, recipeName) {
  const candidates = [
    plan.deck_identity?.brand_wordmark,
    plan.deck_identity?.institution,
    plan.deck_identity?.visual_direction,
    plan.deck_identity?.design_profile
  ].filter(Boolean);
  const profile = candidates.map((value) => BRAND_PROFILES[normalizeKey(value)]).find(Boolean) || null;
  const desiredMode = String(plan.deck_identity?.branding_mode || DESIGN_RECIPES[recipeName].defaultBranding || (profile || plan.deck_identity?.institution ? "subtle_badge" : "none")).toLowerCase();
  return {
    mode: desiredMode,
    wordmark: plan.deck_identity?.brand_wordmark || profile?.wordmark || plan.deck_identity?.institution || "",
    submark: plan.deck_identity?.brand_submark || profile?.submark || "",
    logoPath: plan.deck_identity?.brand_logo_path || profile?.logoPath || "",
    wordmarkImagePath: plan.deck_identity?.brand_wordmark_image_path || "",
    accent: plan.deck_identity?.brand_accent || profile?.accent || "",
    fullShell: profile?.fullShell || ""
  };
}

function resolveContext(plan) {
  const recipeName = resolveRecipeName(plan);
  const recipe = DESIGN_RECIPES[recipeName] || DESIGN_RECIPES.academic_premium;
  const brand = resolveBrand(plan, recipeName);
  const theme = themeFor(recipe.theme);
  const shellFor = (kind) => {
    if (brand.mode === "full_template" && brand.fullShell && shellProfileExists(brand.fullShell)) return brand.fullShell;
    const selected = recipe.shell?.[kind] || recipe.shell?.all || "academic_defense";
    return shellProfileExists(selected) ? selected : "academic_defense";
  };
  return { recipeName, recipe, theme, brand, shellFor };
}

function tocEntries(plan) {
  return (plan.slides || [])
    .filter((s) => SECTION_COPY[s.key])
    .map((s) => sectionCopy(plan, s.key))
    .filter((v, i, arr) => arr.findIndex((x) => x.title === v.title) === i)
    .slice(0, 6);
}

function expandedSlides(plan) {
  const out = [];
  for (const slide of plan.slides || []) {
    if (CHAPTER_BREAKS[slide.key]) {
      const item = CHAPTER_BREAKS[slide.key];
      const copy = isZh(plan) ? item.zh : item.en;
      out.push({ key: `chapter_${slide.key}`, slide_type: "chapter", title: copy.title, takeaway: copy.desc, chapter_num: item.num, speaker_note: "" });
    }
    out.push(slide);
  }
  return out;
}

function toneShadow(ctx) {
  return ["product", "ai"].includes(ctx.recipe.tone)
    ? { type: "outer", color: ctx.theme.shadowColor, blur: 1.8, angle: 45, distance: 1, opacity: 0.14 }
    : { type: "outer", color: ctx.theme.shadowColor, blur: 1.2, angle: 45, distance: 0.8, opacity: 0.09 };
}

function isPremiumTone(ctx) {
  return ["executive", "editorial"].includes(ctx.recipe.tone);
}

function isModernTone(ctx) {
  return ["product", "ai"].includes(ctx.recipe.tone);
}

function designHint(slideDef, fallback = "") {
  return tx(slideDef.design_hint || slideDef.layout_hint || fallback);
}

function card(slide, x, y, w, h, ctx, opts = {}) {
  slide.addShape(SHAPE.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: opts.radius || ctx.theme.radius,
    line: { color: opts.line || ctx.theme.line, width: opts.lineWidth || 0.8, transparency: opts.lineTransparency ?? 0 },
    fill: { color: opts.fill || ctx.theme.white, transparency: opts.fillTransparency ?? 0 },
    shadow: opts.shadow === false ? undefined : toneShadow(ctx)
  });
  if (opts.accentLeft) {
    slide.addShape(SHAPE.rect, { x, y, w: 0.05, h, line: { color: opts.accentLeft, transparency: 100 }, fill: { color: opts.accentLeft } });
  }
  if (opts.accentTop) {
    slide.addShape(SHAPE.roundRect, { x, y, w, h: 0.07, rectRadius: ctx.theme.chipRadius, line: { color: opts.accentTop, transparency: 100 }, fill: { color: opts.accentTop } });
  }
}

function chip(slide, text, x, y, w, ctx, bg, fg) {
  const subtle = isPremiumTone(ctx);
  slide.addShape(SHAPE.roundRect, {
    x,
    y,
    w,
    h: subtle ? 0.36 : 0.38,
    rectRadius: subtle ? 0.04 : ctx.theme.chipRadius,
    line: { color: bg, transparency: subtle ? 18 : 100, width: subtle ? 0.7 : 0.1 },
    fill: { color: subtle ? ctx.theme.white : bg, transparency: subtle ? 3 : 0 }
  });
  slide.addText(safe(text, 32), {
    x: x + 0.05,
    y: y + 0.08,
    w: w - 0.1,
    h: 0.18,
    align: "center",
    fontFace: ctx.theme.body,
    fontSize: pt(13.5),
    bold: true,
    color: fg || (subtle ? bg : ctx.theme.white),
    margin: 0
  });
}

function eyebrow(slide, text, x, y, w, ctx, accent) {
  slide.addShape(SHAPE.rect, { x, y: y + 0.03, w: 0.04, h: 0.22, line: { color: accent, transparency: 100 }, fill: { color: accent } });
  slide.addText(safe(text, 32), {
    x: x + 0.09,
    y,
    w: w - 0.09,
    h: 0.22,
    fontFace: ctx.theme.body,
    fontSize: pt(13.5),
    bold: true,
    color: accent,
    margin: 0
  });
}

function bulletCap(box) {
  const requested = box.maxItems || 4;
  if (box.allowDense) return requested;
  return Math.min(requested, LAYOUT_GUARDRAILS.default.maxBullets);
}

function bulletCharBudget(item, box) {
  if (box.charBudget) return box.charBudget;
  const cjk = hasHan(item);
  if (box.w <= 3.6) return cjk ? 20 : 40;
  if (box.w <= 5.4) return cjk ? 28 : 58;
  return cjk ? 34 : 78;
}

function bullets(slide, items, box, ctx, fallback) {
  const runs = (items || []).slice(0, bulletCap(box)).map((item) => ({ text: safe(item, bulletCharBudget(item, box)), options: { bullet: { indent: 14 } } }));
  slide.addText(runs.length ? runs : [{ text: fallback, options: { bullet: { indent: 14 } } }], {
    x: box.x,
    y: box.y,
    w: box.w,
    h: box.h,
    fontFace: ctx.theme.body,
    fontSize: pt(box.size || 12.6),
    color: box.color || ctx.theme.ink,
    paraSpaceAfterPt: 7,
    breakLine: true,
    margin: 0
  });
}

function themeMeta(plan, slideDef) {
  const copy = sectionCopy(plan, slideDef.key);
  return {
    label: safe(slideDef.theme_label || copy.title || slideDef.key || "", 18),
    sentence: safe(slideDef.theme_sentence || copy.desc || slideDef.takeaway || "", isZh(plan) ? 26 : 54)
  };
}

function themeBadgeWidth(label) {
  const factor = hasHan(label) ? 0.28 : 0.12;
  return Math.max(0.92, Math.min(1.92, 0.42 + String(label || "").length * factor));
}

function renderContentTheme(slide, slideDef, plan, ctx) {
  const meta = themeMeta(plan, slideDef);
  if (!meta.label) return;
  const shell = ctx.shellFor("content");
  const y = shell === "mckinsey" ? 1.64 : shell === "exhibit" ? 1.16 : 1.46;
  const x = 1.02;
  const w = themeBadgeWidth(meta.label);
  slide.addShape(SHAPE.roundRect, {
    x,
    y,
    w,
    h: 0.38,
    rectRadius: 0.08,
    line: { color: ctx.theme.accent, transparency: 72, width: 0.6 },
    fill: { color: ctx.theme.accent, transparency: 90 }
  });
  slide.addText(meta.label, {
    x: x + 0.08,
    y: y + 0.08,
    w: w - 0.16,
    h: 0.18,
    fontFace: ctx.theme.body,
    fontSize: LAYOUT_GUARDRAILS.default.themeLabelSize,
    bold: true,
    color: ctx.theme.accent,
    align: "center",
    margin: 0
  });
  if (meta.sentence) {
    slide.addText(meta.sentence, {
      x: x + w + 0.16,
      y: y + 0.07,
      w: 6.4,
      h: 0.2,
      fontFace: ctx.theme.body,
      fontSize: LAYOUT_GUARDRAILS.default.themeSentenceSize,
      color: ctx.theme.muted,
      margin: 0
    });
  }
}

function renderBrandBadge(slide, ctx, kind) {
  if (ctx.brand.mode !== "subtle_badge" || (!ctx.brand.wordmark && !ctx.brand.wordmarkImagePath)) return;
  const shell = ctx.shellFor(kind);
  const darkShell = ["exhibit", "anthropic"].includes(shell) && ["cover", "chapter", "ending"].includes(kind);
  const x = kind === "cover" ? 9.92 : 10.22;
  const y = kind === "cover" ? 0.24 : 0.19;
  const w = kind === "cover" ? 2.8 : 2.46;
  const h = kind === "cover" ? 0.54 : 0.48;
  const logoExists = ctx.brand.logoPath && fs.existsSync(ctx.brand.logoPath);
  const wordmarkImageExists = ctx.brand.wordmarkImagePath && fs.existsSync(ctx.brand.wordmarkImagePath);
  slide.addShape(SHAPE.roundRect, {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    line: { color: darkShell ? ctx.theme.white : ctx.theme.line, transparency: darkShell ? 50 : 15, width: 0.6 },
    fill: { color: "FFFFFF", transparency: darkShell ? 8 : 0 },
    shadow: darkShell ? undefined : toneShadow(ctx)
  });
  if (logoExists) {
    slide.addImage({ path: ctx.brand.logoPath, x: x + 0.08, y: y + 0.05, w: 0.36, h: h - 0.1 });
  }
  const textX = x + (logoExists ? 0.5 : 0.16);
  if (wordmarkImageExists) {
    slide.addImage({ path: ctx.brand.wordmarkImagePath, x: textX, y: y + 0.1, w: w - (logoExists ? 0.62 : 0.26), h: kind === "cover" ? 0.18 : 0.16 });
  } else {
    slide.addText(safe(ctx.brand.wordmark, 18), { x: textX, y: y + 0.12, w: w - (logoExists ? 0.58 : 0.24), h: 0.2, fontFace: ctx.theme.head, fontSize: pt(kind === "cover" ? 14.4 : 13.6), bold: true, color: ctx.theme.primary, margin: 0 });
  }
}

function enforceMinReadableText(slide) {
  if (slide.__minReadableTextInstalled) return slide;
  const rawAddText = slide.addText.bind(slide);
  slide.addText = (text, options = {}) => {
    const next = { ...options };
    if (typeof next.fontSize === "number") next.fontSize = pt(next.fontSize);
    else next.fontSize = MIN_FONT_PT;
    if (typeof next.h === "number" && next.h < 0.2) next.h = 0.2;
    return rawAddText(text, next);
  };
  slide.__minReadableTextInstalled = true;
  return slide;
}

function shellVars(kind, slideDef, plan, ctx, index, total) {
  const copy = sectionCopy(plan, slideDef.key);
  const [titleLine1, titleLine2] = splitTitle(slideDef.title || copy.title, isZh(plan) ? 18 : 42);
  const title = slideDef.title || plan.deck_identity?.title || "Academic Defense";
  const subtitle = slideDef.subtitle || plan.deck_identity?.date || "";
  const vars = {
    LOGO: "",
    TITLE: title,
    SUBTITLE: subtitle,
    AUTHOR: plan.deck_identity?.author || "",
    ADVISOR: plan.deck_identity?.advisor || "",
    INSTITUTION: plan.deck_identity?.institution || "",
    DATE: plan.deck_identity?.date || "",
    PAGE_NUM: `${index}/${total}`,
    TOTAL_PAGES: String(total),
    SECTION_NUM: String(index).padStart(2, "0"),
    SECTION_NAME: copy.title,
    PAGE_TITLE: titleLine1,
    PAGE_TITLE_LINE2: titleLine2,
    PAGE_LABEL: (copy.title || slideDef.key || "").toUpperCase(),
    KEY_MESSAGE: safe(slideDef.takeaway || "", 120),
    CONTENT_AREA: "",
    SOURCE: sourceLine(slideDef),
    NOTE: "",
    THANK_YOU: slideDef.title || tr(plan, "感谢各位老师聆听", "Thank you for your attention"),
    ENDING_SUBTITLE: slideDef.takeaway || tr(plan, "欢迎各位老师批评指正", "Questions and comments are welcome"),
    CONTACT_INFO: plan.deck_identity?.author || "",
    EMAIL: "",
    DEPARTMENT: plan.deck_identity?.advisor || "",
    COPYRIGHT: `${plan.deck_identity?.title || "Academic Defense"} · ${plan.deck_identity?.date || ""}`,
    PROJECT_ID: plan.deck_identity?.institution || "",
    COVER_QUOTE: "",
    COVER_TAGLINE: "",
    CHAPTER_NUM: slideDef.chapter_num || String(index).padStart(2, "0"),
    CHAPTER_TITLE: slideDef.title || copy.title,
    CHAPTER_DESC: slideDef.takeaway || copy.desc,
    CONTACT_NAME: plan.deck_identity?.author || ""
  };
  if (kind === "toc") {
    tocEntries(plan).forEach((item, i) => {
      vars[`TOC_ITEM_${i + 1}_TITLE`] = item.title;
      vars[`TOC_ITEM_${i + 1}_DESC`] = item.desc;
    });
  }
  return vars;
}

function visualPanel(slide, slideDef, plan, ctx, x, y, w, h) {
  const type = slideDef.visual?.type || (slideDef.key === "results" ? "chart" : "none");
  const imagePath = slideDef.visual?.path && fs.existsSync(slideDef.visual.path) ? slideDef.visual.path : "";
  card(slide, x, y, w, h, ctx, { fill: ctx.theme.white, line: ctx.theme.line });
  chip(slide, type.replace(/_/g, " "), x + 0.18, y + 0.16, 1.35, ctx, ctx.theme.primary);
  if (imagePath) {
    slide.addImage({ path: imagePath, x: x + 0.28, y: y + 0.52, w: w - 0.56, h: h - 0.78 });
    if (slideDef.visual?.caption) {
      slide.addText(safe(slideDef.visual.caption, 72), {
        x: x + 0.34,
        y: y + h - 0.34,
        w: w - 0.68,
        h: 0.2,
        fontFace: ctx.theme.body,
        fontSize: pt(13.5),
        color: ctx.theme.muted,
        margin: 0,
        align: "center"
      });
    }
    return;
  }
  if (type === "system_architecture") {
    [["Input Layer", 0.55], ["Core Module", 1.62], ["Output & Validation", 2.72]].forEach(([label, dy], i) => {
      card(slide, x + 0.38, y + dy, w - 0.76, i === 1 ? 0.78 : 0.62, ctx, { fill: i === 1 ? ctx.theme.soft : ctx.theme.softAlt, line: ctx.theme.line, shadow: false });
      slide.addText(tr(plan, i === 0 ? "输入层" : i === 1 ? "核心模块" : "输出验证", label), { x: x + 0.55, y: y + dy + 0.16, w: w - 1.1, h: 0.16, align: "center", fontFace: ctx.theme.head, fontSize: i === 1 ? 15.2 : 13.2, bold: true, color: ctx.theme.primary, margin: 0 });
    });
    slide.addShape(SHAPE.line, { x: x + w / 2, y: y + 1.24, w: 0, h: 0.33, line: { color: ctx.theme.accent, width: 1.2, endArrowType: "triangle" } });
    slide.addShape(SHAPE.line, { x: x + w / 2, y: y + 2.35, w: 0, h: 0.34, line: { color: ctx.theme.accent, width: 1.2, endArrowType: "triangle" } });
    return;
  }
  if (type === "workflow" || type === "technical_roadmap") {
    (slideDef.bullets || [tr(plan, "步骤 1", "Step 1"), tr(plan, "步骤 2", "Step 2"), tr(plan, "步骤 3", "Step 3")]).slice(0, 3).forEach((item, i) => {
      const bx = x + 0.32 + i * 1.8;
      card(slide, bx, y + 1.42, 1.46, 1.82, ctx, { fill: i === 1 ? ctx.theme.soft : ctx.theme.softAlt, line: ctx.theme.line });
      slide.addText(safe(item, 26), { x: bx + 0.12, y: y + 1.95, w: 1.2, h: 0.58, align: "center", valign: "mid", fontFace: ctx.theme.head, fontSize: 12.2, bold: true, color: ctx.theme.primary, margin: 0 });
      if (i < 2) slide.addShape(SHAPE.line, { x: bx + 1.46, y: y + 2.32, w: 0.34, h: 0, line: { color: ctx.theme.accent, width: 1.1, endArrowType: "triangle" } });
    });
    return;
  }
  if (type === "chart") {
    [0.44, 0.72, 0.9].forEach((ratio, i) => {
      const bx = x + 0.82 + i * 1.44;
      const bh = h * ratio * 0.5;
      slide.addShape(SHAPE.rect, { x: bx, y: y + h - 0.62 - bh, w: 0.78, h: bh, line: { color: i === 1 ? ctx.theme.accent2 : ctx.theme.accent, transparency: 100 }, fill: { color: i === 1 ? ctx.theme.accent2 : ctx.theme.accent } });
      slide.addText(String(i + 1), { x: bx, y: y + h - 0.5, w: 0.78, h: 0.12, align: "center", fontFace: ctx.theme.body, fontSize: 8.6, color: ctx.theme.muted, margin: 0 });
    });
    slide.addShape(SHAPE.line, { x: x + 0.62, y: y + h - 0.66, w: w - 1.18, h: 0, line: { color: ctx.theme.line, width: 1 } });
    slide.addShape(SHAPE.line, { x: x + 0.62, y: y + 0.7, w: 0, h: h - 1.36, line: { color: ctx.theme.line, width: 1 } });
    slide.addText(tr(plan, "可在这里替换成原生 PPT 图表", "Replace this panel with a native PowerPoint chart"), { x: x + 1.96, y: y + 1.48, w: w - 2.42, h: 0.9, fontFace: ctx.theme.head, fontSize: 15.6, bold: true, color: ctx.theme.primary, valign: "mid", margin: 0 });
    return;
  }
  slide.addText(tr(plan, "优先重绘结构图或图表，避免截图", "Prefer a redrawn editable diagram instead of a screenshot"), { x: x + 0.5, y: y + 1.74, w: w - 1.0, h: 0.9, fontFace: ctx.theme.head, fontSize: 15.2, bold: true, color: ctx.theme.primary, align: "center", valign: "mid", margin: 0 });
}

function layoutNarrativePremiumSpread(slide, slideDef, plan, ctx) {
  eyebrow(slide, tr(plan, "核心判断", "Core Thesis"), 1.02, 2.02, 1.84, ctx, ctx.theme.primary);
  slide.addText(safe(slideDef.takeaway || slideDef.title, 110), {
    x: 1.02,
    y: 2.34,
    w: 9.18,
    h: 0.98,
    fontFace: ctx.theme.head,
    fontSize: 21.4,
    bold: true,
    color: ctx.theme.primary,
    valign: "mid",
    margin: 0
  });
  slide.addShape(SHAPE.line, { x: 1.02, y: 3.46, w: 10.96, h: 0, line: { color: ctx.theme.line, width: 0.85 } });
  slide.addText(tr(plan, "Supporting Evidence", "Supporting Evidence"), {
    x: 1.02,
    y: 3.72,
    w: 2.16,
    h: 0.16,
    fontFace: ctx.theme.body,
    fontSize: 8.6,
    bold: true,
    color: ctx.theme.accent,
    margin: 0
  });
  bullets(slide, slideDef.bullets, { x: 1.02, y: 4.08, w: 6.16, h: 1.7, size: 12.2, maxItems: 4 }, ctx, tr(plan, "在这里补充本页的论证依据", "Add the supporting evidence for this slide here"));
  card(slide, 8.22, 3.78, 3.76, 1.96, ctx, { fill: ctx.theme.white, line: ctx.theme.line, shadow: false });
  eyebrow(slide, tr(plan, "答辩提示", "Defense Cue"), 8.48, 3.98, 1.3, ctx, ctx.theme.accent2);
  slide.addText(`Sources  ${sourceLine(slideDef)}`, {
    x: 8.48,
    y: 4.34,
    w: 2.96,
    h: 0.18,
    fontFace: ctx.theme.body,
    fontSize: 9.0,
    color: ctx.theme.muted,
    margin: 0
  });
  slide.addText(tr(plan, "优先把这一页讲成一个判断句，再用少量高质量证据支撑。", "Present this page as one judgment sentence backed by a small set of strong evidence."), {
    x: 8.48,
    y: 4.76,
    w: 2.96,
    h: 0.72,
    fontFace: ctx.theme.body,
    fontSize: 10.8,
    color: ctx.theme.ink,
    margin: 0
  });
}

function layoutNarrativePremium(slide, slideDef, plan, ctx) {
  slide.addShape(SHAPE.rect, { x: 0.98, y: 2.0, w: 0.05, h: 3.76, line: { color: ctx.theme.primary, transparency: 100 }, fill: { color: ctx.theme.primary } });
  eyebrow(slide, tr(plan, "核心论证", "Core Argument"), 1.18, 2.08, 2.0, ctx, ctx.theme.primary);
  slide.addText(safe(slideDef.takeaway || slideDef.title, 82), {
    x: 1.18,
    y: 2.48,
    w: 5.6,
    h: 0.9,
    fontFace: ctx.theme.head,
    fontSize: 19.2,
    bold: true,
    color: ctx.theme.primary,
    valign: "mid",
    margin: 0
  });
  bullets(slide, slideDef.bullets, { x: 1.18, y: 3.56, w: 5.56, h: 2.02, size: 12.2, maxItems: 4 }, ctx, tr(plan, "在这里补充本页的论证依据", "Add the supporting evidence for this slide here"));
  if (slideDef.visual?.path && fs.existsSync(slideDef.visual.path)) {
    visualPanel(slide, slideDef, plan, ctx, 7.32, 2.04, 4.78, 3.72);
    return;
  }
  card(slide, 7.32, 2.04, 4.78, 3.72, ctx, { fill: ctx.theme.white, line: ctx.theme.line, shadow: false });
  eyebrow(slide, tr(plan, "答辩提示", "Defense Cue"), 7.62, 2.2, 1.42, ctx, ctx.theme.accent2);
  slide.addText(safe(slideDef.takeaway || slideDef.title, 86), {
    x: 7.62,
    y: 2.68,
    w: 3.96,
    h: 0.84,
    fontFace: ctx.theme.head,
    fontSize: 17.0,
    bold: true,
    color: ctx.theme.primary,
    valign: "mid",
    margin: 0
  });
  slide.addShape(SHAPE.line, { x: 7.62, y: 3.74, w: 3.92, h: 0, line: { color: ctx.theme.line, width: 0.8 } });
  slide.addText(`Sources  ${sourceLine(slideDef)}`, {
    x: 7.62,
    y: 4.04,
    w: 3.92,
    h: 0.22,
    fontFace: ctx.theme.body,
    fontSize: 9.2,
    color: ctx.theme.muted,
    margin: 0
  });
  slide.addText(tr(plan, "把这一页控制成一个判断句，并用 2 到 4 条证据支撑。", "Keep this slide to one judgment sentence backed by 2 to 4 concrete points."), {
    x: 7.62,
    y: 4.46,
    w: 3.9,
    h: 0.9,
    fontFace: ctx.theme.body,
    fontSize: 11.2,
    color: ctx.theme.ink,
    margin: 0
  });
}

function layoutMethodPremium(slide, slideDef, plan, ctx) {
  if (designHint(slideDef) === "method_process_band" && ["workflow", "technical_roadmap"].includes(slideDef.visual?.type || "")) {
    eyebrow(slide, tr(plan, "方法路径", "Method Path"), 1.02, 2.02, 1.7, ctx, ctx.theme.primary);
    slide.addText(safe(slideDef.takeaway || slideDef.title, 88), {
      x: 1.02,
      y: 2.34,
      w: 4.12,
      h: 0.9,
      fontFace: ctx.theme.head,
      fontSize: 19.0,
      bold: true,
      color: ctx.theme.primary,
      valign: "mid",
      margin: 0
    });
    bullets(slide, slideDef.bullets, { x: 1.02, y: 3.42, w: 3.98, h: 2.2, size: 11.6, maxItems: 4 }, ctx, tr(plan, "说明方法步骤与本人工作如何对应", "Clarify how the method steps map to the student's work"));
    visualPanel(slide, slideDef, plan, ctx, 5.28, 2.14, 6.88, 3.82);
    return;
  }
  slide.addShape(SHAPE.rect, { x: 0.98, y: 2.0, w: 0.05, h: 4.02, line: { color: ctx.theme.primary, transparency: 100 }, fill: { color: ctx.theme.primary } });
  eyebrow(slide, tr(plan, "方法逻辑", "Method Logic"), 1.18, 2.08, 2.0, ctx, ctx.theme.primary);
  slide.addText(safe(slideDef.takeaway || slideDef.title, 82), {
    x: 1.18,
    y: 2.48,
    w: 3.52,
    h: 0.94,
    fontFace: ctx.theme.head,
    fontSize: 18.4,
    bold: true,
    color: ctx.theme.primary,
    valign: "mid",
    margin: 0
  });
  bullets(slide, slideDef.bullets, { x: 1.18, y: 3.56, w: 3.34, h: 2.08, size: 11.8, maxItems: 4 }, ctx, tr(plan, "说明本人完成了哪些关键模块", "Clarify which core modules were implemented by the student"));
  visualPanel(slide, slideDef, plan, ctx, 5.16, 2.0, 7.0, 4.02);
}

function layoutResultsPremium(slide, slideDef, plan, ctx) {
  const values = (slideDef.bullets || []).slice(0, 3);
  [1.0, 4.18, 7.36].forEach((x, i) => {
    eyebrow(slide, `0${i + 1}`, x, 2.02, 0.56, ctx, i === 1 ? ctx.theme.accent2 : ctx.theme.accent);
    slide.addText(safe(values[i] || tr(plan, "核心指标", "Key Metric"), 36), {
      x,
      y: 2.34,
      w: 2.5,
      h: 0.42,
      fontFace: ctx.theme.head,
      fontSize: 15.2,
      bold: true,
      color: ctx.theme.primary,
      margin: 0
    });
    if (i < 2) slide.addShape(SHAPE.line, { x: x + 2.72, y: 2.12, w: 0, h: 0.86, line: { color: ctx.theme.line, width: 0.8 } });
  });
  card(slide, 0.96, 3.38, 5.78, 2.48, ctx, { fill: ctx.theme.softAlt, line: ctx.theme.line, shadow: false });
  eyebrow(slide, tr(plan, "结果解读", "Interpretation"), 1.18, 3.56, 1.44, ctx, ctx.theme.primary);
  bullets(slide, slideDef.bullets?.slice(0, 5), { x: 1.18, y: 4.02, w: 5.0, h: 1.42, size: 11.8, maxItems: 4 }, ctx, tr(plan, "补充这一页的定量或定性解释", "Add the quantitative or qualitative readout here"));
  visualPanel(slide, { ...slideDef, visual: { type: slideDef.visual?.type || "chart" } }, plan, ctx, 6.96, 3.38, 5.22, 2.48);
}

function layoutInnovationPremium(slide, slideDef, plan, ctx) {
  const items = (slideDef.bullets || []).slice(0, 3);
  eyebrow(slide, tr(plan, "创新拆解", "Innovation Breakdown"), 1.02, 2.0, 1.84, ctx, ctx.theme.primary);
  slide.addText(safe(slideDef.takeaway || tr(plan, "创新点必须同时对应方法变化与证据支持", "Innovation must connect both to design choices and supporting evidence"), 92), {
    x: 1.02,
    y: 2.32,
    w: 9.0,
    h: 0.8,
    fontFace: ctx.theme.head,
    fontSize: 18.8,
    bold: true,
    color: ctx.theme.primary,
    valign: "mid",
    margin: 0
  });
  [1.02, 4.42, 7.82].forEach((x, i) => {
    slide.addText(`0${i + 1}`, {
      x,
      y: 3.02,
      w: 0.72,
      h: 0.42,
      fontFace: ctx.theme.head,
      fontSize: 24,
      bold: true,
      color: i === 1 ? ctx.theme.accent2 : ctx.theme.accent,
      margin: 0
    });
    slide.addShape(SHAPE.line, { x, y: 3.54, w: 2.74, h: 0, line: { color: ctx.theme.line, width: 0.8 } });
    slide.addText(safe(items[i] || tr(plan, "创新点待补充", "Innovation point"), 44), {
      x,
      y: 3.76,
      w: 2.82,
      h: 0.68,
      fontFace: ctx.theme.head,
      fontSize: 15.6,
      bold: true,
      color: ctx.theme.primary,
      valign: "mid",
      margin: 0
    });
    slide.addText(tr(plan, "同时说明设计变化、改进对象和结果证据。", "State the design change, the target of improvement, and the result evidence."), {
      x,
      y: 4.62,
      w: 2.78,
      h: 0.74,
      fontFace: ctx.theme.body,
      fontSize: 10.6,
      color: ctx.theme.muted,
      margin: 0
    });
  });
  slide.addShape(SHAPE.line, { x: 1.02, y: 5.86, w: 10.98, h: 0, line: { color: ctx.theme.line, width: 0.8 } });
  slide.addText(safe(slideDef.takeaway || tr(plan, "每一项创新都必须可定位、可解释、可被证据支持。", "Each innovation point should be specific, interpretable, and evidence-backed."), 110), {
    x: 1.02,
    y: 6.04,
    w: 10.98,
    h: 0.22,
    fontFace: ctx.theme.body,
    fontSize: 10.6,
    color: ctx.theme.primary,
    align: "center",
    margin: 0
  });
}

function layoutLimitationsPremium(slide, slideDef, plan, ctx) {
  const items = slideDef.bullets || [];
  const left = items.slice(0, Math.ceil(items.length / 2));
  const right = items.slice(Math.ceil(items.length / 2));
  eyebrow(slide, tr(plan, "边界与展望", "Boundary and Outlook"), 1.02, 2.0, 1.92, ctx, ctx.theme.primary);
  slide.addText(safe(slideDef.takeaway || tr(plan, "主动说明边界，会让结论更可信。", "Explicitly stating the boundaries makes the conclusion more credible."), 92), {
    x: 1.02,
    y: 2.32,
    w: 8.8,
    h: 0.72,
    fontFace: ctx.theme.head,
    fontSize: 18.4,
    bold: true,
    color: ctx.theme.primary,
    valign: "mid",
    margin: 0
  });
  slide.addShape(SHAPE.rect, { x: 1.02, y: 3.26, w: 0.04, h: 2.18, line: { color: ctx.theme.primary, transparency: 100 }, fill: { color: ctx.theme.primary } });
  slide.addShape(SHAPE.rect, { x: 6.72, y: 3.26, w: 0.04, h: 2.18, line: { color: ctx.theme.accent2, transparency: 100 }, fill: { color: ctx.theme.accent2 } });
  slide.addText(tr(plan, "局限性", "Limitations"), {
    x: 1.2,
    y: 3.24,
    w: 1.62,
    h: 0.18,
    fontFace: ctx.theme.body,
    fontSize: 8.6,
    bold: true,
    color: ctx.theme.primary,
    margin: 0
  });
  slide.addText(tr(plan, "后续工作", "Future Work"), {
    x: 6.9,
    y: 3.24,
    w: 1.62,
    h: 0.18,
    fontFace: ctx.theme.body,
    fontSize: 8.6,
    bold: true,
    color: ctx.theme.accent2,
    margin: 0
  });
  bullets(slide, left, { x: 1.2, y: 3.7, w: 4.74, h: 1.66, size: 11.8, maxItems: 4 }, ctx, tr(plan, "主动交代当前方案的适用范围。", "State the current scope and limitations directly."));
  bullets(slide, right, { x: 6.9, y: 3.7, w: 4.74, h: 1.66, size: 11.8, maxItems: 4 }, ctx, tr(plan, "说明后续如何扩展或增强。", "Explain how the work can be extended next."));
  slide.addShape(SHAPE.line, { x: 1.02, y: 5.84, w: 10.98, h: 0, line: { color: ctx.theme.line, width: 0.8 } });
  slide.addText(tr(plan, "回答问题时，先承认边界，再说明为什么当前结论依然成立。", "When questioned, acknowledge the boundary first and then explain why the current conclusion still holds."), {
    x: 1.02,
    y: 6.02,
    w: 10.98,
    h: 0.22,
    fontFace: ctx.theme.body,
    fontSize: 10.6,
    color: ctx.theme.primary,
    align: "center",
    margin: 0
  });
}

function layoutNarrative(slide, slideDef, plan, ctx) {
  card(slide, 0.96, 1.98, 6.95, 3.96, ctx, { fill: ctx.theme.softAlt, line: ctx.theme.line, accentLeft: ctx.theme.primary, shadow: false });
  chip(slide, tr(plan, "论证要点", "Argument"), 1.18, 2.14, 1.16, ctx, ctx.theme.primary);
  bullets(slide, slideDef.bullets, { x: 1.18, y: 2.56, w: 6.26, h: 2.82, size: 12.4, maxItems: 4 }, ctx, tr(plan, "在这里补充页面证据", "Add slide-level evidence here"));
  card(slide, 8.18, 1.98, 4.0, 1.5, ctx, { fill: ctx.theme.white, line: ctx.theme.line });
  chip(slide, tr(plan, "页面结论", "Slide Claim"), 8.38, 2.14, 1.14, ctx, ctx.theme.accent);
  slide.addText(safe(slideDef.takeaway || slideDef.title, 78), { x: 8.38, y: 2.54, w: 3.42, h: 0.62, fontFace: ctx.theme.head, fontSize: 16, bold: true, color: ctx.theme.primary, valign: "mid", margin: 0 });
  card(slide, 8.18, 3.78, 4.0, 2.16, ctx, { fill: ctx.theme.white, line: ctx.theme.line });
  chip(slide, tr(plan, "证据与来源", "Evidence"), 8.38, 3.96, 1.04, ctx, ctx.theme.accent2);
  bullets(slide, (slideDef.source_ids || []).map((v) => `Source: ${v}`), { x: 8.38, y: 4.32, w: 3.32, h: 1.2, size: 11.0, maxItems: 3 }, ctx, `Sources: ${sourceLine(slideDef)}`);
}

function layoutMethod(slide, slideDef, plan, ctx) {
  card(slide, 0.96, 1.98, 4.05, 4.1, ctx, { fill: ctx.theme.softAlt, line: ctx.theme.line, accentLeft: ctx.theme.primary, shadow: false });
  chip(slide, tr(plan, "关键路径", "Method Logic"), 1.18, 2.14, 1.24, ctx, ctx.theme.primary);
  slide.addText(safe(slideDef.takeaway || slideDef.title, 70), { x: 1.18, y: 2.56, w: 3.36, h: 0.74, fontFace: ctx.theme.head, fontSize: 16.8, bold: true, color: ctx.theme.primary, valign: "mid", margin: 0 });
  bullets(slide, slideDef.bullets, { x: 1.18, y: 3.34, w: 3.28, h: 2.2, size: 11.8, maxItems: 4 }, ctx, tr(plan, "说明本人完成了哪些模块", "Clarify which modules were implemented by the student"));
  visualPanel(slide, slideDef, plan, ctx, 5.34, 1.98, 6.84, 4.1);
}

function layoutResults(slide, slideDef, plan, ctx) {
  const values = (slideDef.bullets || []).slice(0, 3);
  [0.96, 4.26, 7.56].forEach((x, i) => {
    card(slide, x, 1.98, 2.9, 1.38, ctx, { fill: i === 1 ? ctx.theme.soft : ctx.theme.softAlt, line: ctx.theme.line, shadow: false });
    chip(slide, `0${i + 1}`, x + 0.18, 2.13, 0.46, ctx, i === 1 ? ctx.theme.accent2 : ctx.theme.accent);
    slide.addText(safe(values[i] || tr(plan, "核心指标", "Key Metric"), 36), { x: x + 0.18, y: 2.56, w: 2.4, h: 0.46, fontFace: ctx.theme.head, fontSize: 14.8, bold: true, color: ctx.theme.primary, valign: "mid", margin: 0 });
  });
  card(slide, 0.96, 3.68, 5.72, 2.24, ctx, { fill: ctx.theme.white, line: ctx.theme.line, accentLeft: ctx.theme.primary, shadow: false });
  chip(slide, tr(plan, "结果解读", "Interpretation"), 1.18, 3.84, 1.14, ctx, ctx.theme.primary);
  bullets(slide, slideDef.bullets?.slice(0, 5), { x: 1.18, y: 4.24, w: 5.02, h: 1.26, size: 11.8, maxItems: 4 }, ctx, tr(plan, "补充这一页的定量或定性解读", "Add quantitative or qualitative interpretation here"));
  visualPanel(slide, { ...slideDef, visual: { type: slideDef.visual?.type || "chart" } }, plan, ctx, 6.92, 3.68, 5.26, 2.24);
}

function layoutInnovation(slide, slideDef, plan, ctx) {
  (slideDef.bullets || []).slice(0, 3).forEach((item, i) => {
    const x = 0.96 + i * 3.76;
    card(slide, x, 2.04, 3.32, 2.38, ctx, { fill: i === 1 ? ctx.theme.soft : ctx.theme.white, line: ctx.theme.line, accentTop: i === 1 ? ctx.theme.accent2 : ctx.theme.accent });
    chip(slide, `0${i + 1}`, x + 0.2, 2.22, 0.48, ctx, i === 1 ? ctx.theme.accent2 : ctx.theme.accent);
    slide.addText(safe(item, 42), { x: x + 0.22, y: 2.76, w: 2.78, h: 0.72, fontFace: ctx.theme.head, fontSize: 15.8, bold: true, color: ctx.theme.primary, valign: "mid", margin: 0 });
    slide.addText(tr(plan, "对应方法设计与实验结果的双重证据", "Tie each claim to both method design and result evidence"), { x: x + 0.22, y: 3.62, w: 2.78, h: 0.4, fontFace: ctx.theme.body, fontSize: 10.4, color: ctx.theme.muted, margin: 0 });
  });
  card(slide, 0.96, 4.72, 11.24, 1.04, ctx, { fill: ctx.theme.softAlt, line: ctx.theme.soft, shadow: false });
  slide.addText(safe(slideDef.takeaway || tr(plan, "创新点需要用设计逻辑和结果证据共同支撑", "Innovation claims need both design logic and result evidence"), 110), { x: 1.18, y: 5.0, w: 10.76, h: 0.38, fontFace: ctx.theme.head, fontSize: 15.2, bold: true, color: ctx.theme.primary, align: "center", margin: 0 });
}

function layoutLimitations(slide, slideDef, plan, ctx) {
  const items = slideDef.bullets || [];
  card(slide, 0.96, 2.0, 5.46, 3.98, ctx, { fill: ctx.theme.softAlt, line: ctx.theme.line, accentLeft: ctx.theme.primary, shadow: false });
  card(slide, 6.72, 2.0, 5.46, 3.98, ctx, { fill: ctx.theme.white, line: ctx.theme.line, accentLeft: ctx.theme.accent2, shadow: false });
  chip(slide, tr(plan, "工作边界", "Limitations"), 1.18, 2.18, 1.12, ctx, ctx.theme.primary);
  chip(slide, tr(plan, "后续工作", "Future Work"), 6.94, 2.18, 1.12, ctx, ctx.theme.accent2);
  bullets(slide, items.slice(0, Math.ceil(items.length / 2)), { x: 1.18, y: 2.62, w: 4.78, h: 2.94, size: 12.0, maxItems: 4 }, ctx, tr(plan, "主动说明适用范围与不足", "State the applicable scope and known limits"));
  bullets(slide, items.slice(Math.ceil(items.length / 2)), { x: 6.94, y: 2.62, w: 4.78, h: 2.94, size: 12.0, maxItems: 4 }, ctx, tr(plan, "说明可以如何继续扩展", "Describe how the work can be extended next"));
}

function finish(slide, pptx) { warnIfSlideElementsOutOfBounds(slide, pptx); }

function addCover(pptx, plan, ctx, slideDef, index, total) {
  const slide = enforceMinReadableText(pptx.addSlide());
  slide.addImage({ data: loadShell(ctx.shellFor("cover"), "cover", shellVars("cover", slideDef, plan, ctx, index, total)), x: 0, y: 0, w: PPT_W, h: PPT_H });
  renderBrandBadge(slide, ctx, "cover");
  slide.addNotes(slideDef.speaker_note || "");
  finish(slide, pptx);
}

function addToc(pptx, plan, ctx, slideDef, index, total) {
  const slide = enforceMinReadableText(pptx.addSlide());
  slide.addImage({ data: loadShell(ctx.shellFor("toc"), "toc", shellVars("toc", slideDef, plan, ctx, index, total)), x: 0, y: 0, w: PPT_W, h: PPT_H });
  renderBrandBadge(slide, ctx, "toc");
  slide.addNotes(slideDef.speaker_note || "");
  finish(slide, pptx);
}

function addChapter(pptx, plan, ctx, slideDef, index, total) {
  const slide = enforceMinReadableText(pptx.addSlide());
  slide.addImage({ data: loadShell(ctx.shellFor("chapter"), "chapter", shellVars("chapter", slideDef, plan, ctx, index, total)), x: 0, y: 0, w: PPT_W, h: PPT_H });
  renderBrandBadge(slide, ctx, "chapter");
  slide.addNotes(slideDef.speaker_note || "");
  finish(slide, pptx);
}

function addContent(pptx, plan, ctx, slideDef, index, total) {
  const slide = enforceMinReadableText(pptx.addSlide());
  slide.addImage({ data: loadShell(ctx.shellFor("content"), "content", shellVars("content", slideDef, plan, ctx, index, total)), x: 0, y: 0, w: PPT_W, h: PPT_H });
  renderBrandBadge(slide, ctx, "content");
  renderContentTheme(slide, slideDef, plan, ctx);
  if (slideDef.key === "technical_route" || slideDef.key === "student_work_1") {
    if (isPremiumTone(ctx)) layoutMethodPremium(slide, slideDef, plan, ctx);
    else layoutMethod(slide, slideDef, plan, ctx);
  }
  else if (slideDef.key === "results" || slideDef.key === "experiment") {
    if (isPremiumTone(ctx)) layoutResultsPremium(slide, slideDef, plan, ctx);
    else layoutResults(slide, slideDef, plan, ctx);
  }
  else if (slideDef.key === "innovation") {
    if (isPremiumTone(ctx)) layoutInnovationPremium(slide, slideDef, plan, ctx);
    else layoutInnovation(slide, slideDef, plan, ctx);
  }
  else if (slideDef.key === "limitations") {
    if (isPremiumTone(ctx)) layoutLimitationsPremium(slide, slideDef, plan, ctx);
    else layoutLimitations(slide, slideDef, plan, ctx);
  }
  else if (isPremiumTone(ctx)) {
    if (designHint(slideDef) === "statement_spread") layoutNarrativePremiumSpread(slide, slideDef, plan, ctx);
    else layoutNarrativePremium(slide, slideDef, plan, ctx);
  }
  else layoutNarrative(slide, slideDef, plan, ctx);
  slide.addNotes(slideDef.speaker_note || "");
  finish(slide, pptx);
}

function addEnding(pptx, plan, ctx, slideDef, index, total) {
  const slide = enforceMinReadableText(pptx.addSlide());
  slide.addImage({ data: loadShell(ctx.shellFor("ending"), "ending", shellVars("ending", slideDef, plan, ctx, index, total)), x: 0, y: 0, w: PPT_W, h: PPT_H });
  renderBrandBadge(slide, ctx, "ending");
  slide.addNotes(slideDef.speaker_note || "");
  finish(slide, pptx);
}

function main() {
  const plan = deckPlan();
  const ctx = resolveContext(plan);
  const slides = expandedSlides(plan);
  const pptx = new pptxgen();
  pptx.layout = "LAYOUT_WIDE";
  pptx.author = "Codex Academic PPT Skill";
  pptx.company = "Codex";
  pptx.subject = "Academic presentation";
  pptx.title = plan.deck_identity?.title || "Academic Defense";
  pptx.theme = { headFontFace: ctx.theme.head, bodyFontFace: ctx.theme.body, lang: isZh(plan) ? "zh-CN" : "en-US" };
  slides.forEach((slideDef, i) => {
    const index = i + 1;
    if (slideDef.slide_type === "cover") addCover(pptx, plan, ctx, slideDef, index, slides.length);
    else if (slideDef.slide_type === "toc") addToc(pptx, plan, ctx, slideDef, index, slides.length);
    else if (slideDef.slide_type === "chapter") addChapter(pptx, plan, ctx, slideDef, index, slides.length);
    else if (slideDef.slide_type === "closing" || slideDef.key === "thanks") addEnding(pptx, plan, ctx, slideDef, index, slides.length);
    else addContent(pptx, plan, ctx, slideDef, index, slides.length);
  });
  return pptx.writeFile({ fileName: plan.deck_identity?.output_pptx || "academic-defense.pptx" });
}

(async () => {
  await main();
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
