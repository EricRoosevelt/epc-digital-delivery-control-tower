// Plain-language glosses for codes the Framework already emits. A gloss sits
// beside the original code and never replaces it; a code not listed here is
// shown as unrecognised with its raw value, not mapped to the nearest state.

export const MODE_LABELS = {
  fixture: "夹具演示",
  real: "真实输入",
};

//: The adapter names its scenarios; these are this preview's words for them.
//: An unlisted name is shown as the adapter gave it.
export const RUN_LABELS = {
  "member-evidence": "成员证据（一份夹具记录）",
  "pair-verdicts": "成对裁决（同一份夹具记录）",
  "recheck-comparison": "复检：重开评审后，原来的一对构件不再配对（夹具）",
  "recheck-key-change-only": "复检：改了一条无关的规则，模型没有重新发布（夹具）",
  "recheck-semantics-changed": "复检：改了一条被引用规则的数据类型，模型没有重新发布（夹具）",
  "recheck-requirement-relaxed": "复检：放宽了一条被引用的规则，模型没有重新发布（夹具）",
  "recheck-prior-without-basis": "复检：原记录封存时没有保存比较依据（夹具）",
  "recheck-producing-reissued": "复检：交出方模型重新发布，检查结果读数相同（夹具）",
  "recheck-producing-reissued-content-changed":
    "复检：交出方模型重新发布，部分检查结果内容变了（夹具）",
  "recheck-consuming-reissued": "复检：接收方模型重新发布（夹具）",
  "recheck-both-reissued": "复检：双方模型都重新发布（夹具）",
  "recheck-member-gone": "复检：交出方模型重新发布，并删除了一个构件（夹具）",
  "real-refusal": "随附项目的真实运行",
};

// A key the record does not carry, and a key it carries as an empty string, are
// different facts. Neither is ever shown as null, 0, false or a dash that could
// be read as a value.
export const NOT_CARRIED = "记录未携带";
export const EMPTY_STRING = "（记录中为空字符串）";

// The fixture discipline's machine-visible marker. A fixture value has to be
// untrue in a way a reader and a test can see, so every value the fixtures mint
// carries it: `fixture/finding/…` for a re-validated finding key,
// `fixture-determination/…` for a determination reference. `test_purpose_isolation`
// holds that discipline against the published tree.
export const FIXTURE_MARKER = "fixture";

// Evidence provenance, decided **per citation** and never per envelope.
//
// Whether a label is true is a property of the one citation it sits beside, so
// the criterion has to be too. A fixture record can mix the two on one page:
// the four scenarios here cite nine finding keys that are all a real validation
// run's output, while the model-reissue scenario on the D1 walkthrough script
// cites nine of which six are fixture-minted repairs. An envelope-level rule
// would label those six "real validation output" — calling a simulation real,
// which is the one sentence this product cannot get wrong.
export const CITATION_PROVENANCE = {
  "finding-real": {
    key: "real",
    short: "真实验证输出",
    long: "未带夹具标记的 finding 引用：来自真实验证运行，真实 IFC 模型按真实规则评估的产物。",
  },
  "finding-fixture": {
    key: "fixture",
    short: "夹具铸造（模拟）",
    long:
      `带夹具标记（以 ${FIXTURE_MARKER} 开头）的 finding 引用：由夹具铸造，` +
      "不是任何真实验证运行的输出。",
  },
  "determination-fixture": {
    key: "fixture",
    short: "夹具判定（模拟）",
    long: `带夹具标记的判定引用：由夹具提供，没有任何协调评审真的发生过。`,
  },
  "determination-unmarked": {
    key: "unmarked",
    short: "来源未标注的判定",
    long:
      "未带夹具标记的判定引用：判定不是验证运行的输出，本界面也没有可核依据说明它来自哪里，" +
      "因此不作真实或模拟的断言。",
  },
};

/** The provenance of one citation, read off the citation itself. */
export function citationProvenance(kind, citation) {
  const marked = typeof citation === "string" && citation.startsWith(FIXTURE_MARKER);
  if (kind === "finding") return CITATION_PROVENANCE[marked ? "finding-fixture" : "finding-real"];
  if (kind === "determination") {
    return CITATION_PROVENANCE[marked ? "determination-fixture" : "determination-unmarked"];
  }
  return null;
}

// What kind of evidence a carry-over row is about, in the manager's words.
export const CITATION_KINDS = {
  finding: "检查结果引用",
  determination: "判定引用",
};

export const PROVENANCE_NOTICE =
  "本页每条引用旁的来源标注按该条引用自身判定（是否带夹具标记），不按整页或整份记录推断：";

// The policy row is not a citation and carries no marker, so nothing in the
// envelope says whose decision it was. The row states what the record carries
// and says the source is not in it — true of every row, which is what the
// per-row rule requires.
export const POLICY_SOURCE_NOTE = "政策来源未随信封返回：此值是记录携带的政策声明，不能据此判断它是项目决定还是夹具声明。";

export const DEMO_NOTICE =
  "夹具演示：政策与判定为模拟。不能用于正式项目决定，不提供真实评估记录导出。";

const ABSENCES = {
  "no-finding": "本绑定下尚未评估：没有 finding",
  "no-determination": "尚无判定",
  // Defensive only. The pipeline cannot put this on an element member
  // (domain.Finding refuses an element-level N/A); it is listed so an
  // unexpected value is read correctly rather than shown as unrecognised.
  "not-applicable-finding": "已有 finding，但检查不适用，未覆盖此主体",
};

// What became of one member of the sealed subscope. `text` is the gloss that sits
// beside the code; `next` is what the manager can do about it, and says so when
// the record gives them nothing to act on. No entry says "resolved": the record
// has no such disposition, and a member that left is not a member that was fixed.
export const DISPOSITION_ENTRIES = {
  present: {
    text: "当前仍有对应成员；裁决与条件另看",
    next: "看下面 Framework 给出的当前子范围：现在的裁决、下一步和责任角色都以它为准。",
  },
  "element-deleted-in-reissued-model": {
    text: "在重发模型中删除，不等于修复",
    next:
      "记录没有为已删除的构件给出下一步。请在源模型里核对这次删除是不是有意的设计变更；" +
      "本预览不能记录这种确认。",
  },
  "element-out-of-subject-class": {
    text: "已不属于此活动对象类别，不等于修复",
    next:
      "记录没有为它给出下一步。请核对构件的类别（导出映射）是不是有意改变；" +
      "类别变了只说明本活动不再检查它。",
  },
  "pairing-no-longer-derived": {
    text: "这两个构件现在不再被配成一对来检查，不等于开洞已补",
    next:
      "记录没有为这个成员对给出下一步。请核对让它不再被配对的那份依据（见“记录给出的原因”）" +
      "是不是你认可的结论；原来的问题没有被证明已修复。",
  },
  "outside-declared-scope": {
    text: "本次未声明该范围，不等于问题解除",
    next: "这个成员本次没有被重新检查。需要结论时，要重新发起一次包含它的复检；本预览不能发起。",
  },
};

export const DISPOSITIONS = Object.fromEntries(
  Object.entries(DISPOSITION_ENTRIES).map(([key, entry]) => [key, entry.text]),
);

// What the record could establish about the sealed recheck condition. There is
// no "condition met" among them, and none is worded as one.
export const CONDITION_ENTRIES = {
  "named-outcome-observed": {
    text: "仅命名结果已观察到；条件其余部分未检查",
    plain:
      "原复检条件里点名的那个结果，现在观察到了。条件句的其余部分没有被机器检查，" +
      "需要人对照原条件确认；这不是“整句条件已满足”。",
  },
  "named-outcome-not-observed": {
    text: "未观察到命名结果",
    plain: "原复检条件里点名的那个结果，现在没有观察到：原条件未达成。",
  },
  "no-machine-checkable-part": {
    text: "条件没有可机检部分，需要人阅读",
    plain: "原复检条件没有机器能检查的部分，需要人阅读原条件并判断；记录对它不下结论。",
  },
  "not-comparable": {
    text: "不可比较：对应成员集合不完整",
    plain:
      "无法对原复检条件下结论：原来的成员有的已经不在本次记录里，条件没有完整的对象可以检查。" +
      "这不代表条件已满足。",
  },
  "no-recheck-condition": {
    text: "原记录没有复检条件",
    plain: "原记录没有复检条件：原来的裁决没有留下待办。",
  },
};

export const CONDITION_STATES = Object.fromEntries(
  Object.entries(CONDITION_ENTRIES).map(([key, entry]) => [key, entry.text]),
);

// ---------------------------------------------------------------------------
// Evidence carry-over: four states, and the reasons under each (ADR 0005 §5.2)
// ---------------------------------------------------------------------------
//
// The record decides the state and the reason; this file only words them. There
// is no boolean beside the four and no ordering among them: none is "good".

export const CARRY_OVER_STATES = {
  equivalent: {
    label: "比较依据一致",
    meaning: "这条旧证据在本次记录里有唯一对应的一条，逐项比较都相同。",
    caveat: "这只说明不必因为引用换了键而重新收集这条证据，不代表整个交接不用复核。",
  },
  changed: {
    label: "比较依据有变化",
    meaning: "这条旧证据在本次记录里有唯一对应的一条，但至少有一个方面不同。",
    caveat: "结果读起来相同，也仍然算有变化；变了的是哪些方面，见这一条的说明。",
  },
  "no-counterpart": {
    label: "未找到对应证据",
    meaning: "可以比较，但本次记录没有引用与它对应的证据。",
    caveat: "没有对应证据不代表问题已修复。",
  },
  "not-provable": {
    label: "现有依据不足以比较",
    meaning: "比较本身无法建立，所以既不能说一致，也不能说变了。",
    caveat: "这是“无法比较”，不是“证据缺失”，也不是“没有对应证据”。",
  },
};

// `reason -> sentence`. Each one says what the record holds, in words a manager
// can repeat. The reason code itself stays visible in the evidence details.
export const CARRY_OVER_REASONS = {
  "finding-equivalent": "对应的检查结果只有一条，模型版本、检查结果内容、检查要求、检查程序逐项相同。",
  "finding-changed": "对应的检查结果只有一条，逐项比较后至少有一个方面不同。",
  "no-counterpart-in-the-cited-run":
    "本次记录依据的验证运行里，这个构件在这条要求下没有检查结果。",
  "counterpart-not-cited-under-the-current-binding":
    "验证运行里有对应的检查结果，但本次记录的读数没有引用它。",
  "sealed-citation-has-no-comparison-basis":
    "原记录封存时没有保存这条引用的比较依据（旧版本的记录）。本页不会用当前规则去补造，" +
    "所以只能如实显示无法比较。",
  "comparison-basis-version-unknown": "原记录保存的比较依据，是本系统不认识的版本。",
  "subject-not-present":
    "这条证据所针对的成员，在本次记录里已经不在（去向见“记录给出的原因”）。成员不在不等于已修复。",
  "counterpart-not-unique":
    "本次有不止一条候选的对应检查结果，系统不从中挑选（全部候选见“记录给出的原因”）。",
  "requirement-semantics-basis-unavailable": "封存一方或当前一方没有“检查要求”的比较依据。",
  "comparison-basis-incomplete":
    "封存一方或当前一方缺少部分比较依据（模型版本、检查结果内容摘要或检查程序指纹）。",
  "determination-same-reference-same-content": "同一份判定：引用相同，内容摘要也相同。",
  "determination-content-changed-under-the-same-reference":
    "引用相同，但判定的内容已经不是原记录读到的那一份（被重新作出、重新归属或重新签署）。" +
    "新判定照常作为证据读取，只是不能说它和原判定是同一份。",
  "determination-not-cited-by-this-record":
    "模型版本没有变，本次记录没有再引用这份判定：它被别的判定取代了。",
  "determination-not-attributable-to-this-context":
    "模型版本已经变化，原判定是针对旧版本作出的，不能归到当前版本。" +
    "不是证据不存在，也不是原判定错误；需要针对当前版本的判定。",
};

// What differed on a `changed` finding row. The noun is used both ways — "…变了"
// and "…未变" — so the page states the concrete fact instead of a tag.
export const CHANGED_ASPECTS = {
  "model-version": "模型版本",
  "finding-content": "检查结果内容",
  "requirement-semantics": "检查要求",
  checker: "检查程序",
};

// The order the aspects are spoken in: what was re-issued, what was read, what
// was asked, what did the asking.
export const ASPECT_ORDER = ["model-version", "finding-content", "requirement-semantics", "checker"];

export const ASPECT_NOTES = {
  onlyModelVersion:
    "只有模型版本变了，不等于检查结果的内容变了。记录也不就“这条证据能否沿用到新版本”下结论。",
  semanticsSameOutcome:
    "检查要求被修改过，检查结果读起来和原来一样——但它是按修改后的要求得出的，不能当作同一条证据。",
  semanticsAndContent:
    "检查要求被修改过，检查结果内容也变了：结果的变化可能来自要求的修改（例如要求放宽），" +
    "不能据此说模型修好了。记录不说明要求是放宽还是收紧。",
  contentUnderSameRequirement:
    "检查要求没有变，检查结果内容变了。这一行不记录结果是变好还是变差，请看当前裁决。",
  checker: "检查程序（检查器或它的配置）版本不同：同样的模型和要求也可能得出不同结果。",
  unrecognised: "含有未识别的变化方面，本页因此不列“未变”的方面。",
};

export const KEY_CHANGED = {
  yes: "引用换了键（新键就是上面“本次记录引用的对应证据”）。换键本身不算变化。",
  no: "引用的键没有换。",
};

export const ONLY_REKEYED = "只是引用换了键";

// Which side of the handover was re-issued. The case is looked up from the
// record's `changed_models`; the sentences name roles by placeholder and never
// a discipline. No case says whether the re-issue was good news.
export const REISSUE_CASES = {
  none: {
    headline: "两侧模型都没有重新发布（版本未变）",
    detail: "本次复检和原记录用的是同一对模型版本，所以下面的差异不来自模型改动。",
    caveats: [],
  },
  producing: {
    headline: "交出方的模型重新发布了，接收方的模型没有变",
    detail: "交出方（{from}）的模型 {producing} 是新版本；接收方（{to}）的模型 {consuming} 还是原版本。",
    caveats: [
      "交出方重新发布可能改变了穿越关系或成员范围，不能据此说接收方的工作（例如开洞）已经做好。",
      "针对旧版本作出的判定不能归到新版本。",
    ],
  },
  consuming: {
    headline: "接收方的模型重新发布了，交出方的模型没有变",
    detail: "接收方（{to}）的模型 {consuming} 是新版本；交出方（{from}）的模型 {producing} 还是原版本。",
    caveats: [
      "接收方重新发布可能是修复的途径，但不代表修复已经发生（例如洞口已完成）。",
      "针对旧版本作出的判定同样不能归到新版本。",
    ],
  },
  both: {
    headline: "交出方和接收方的模型都重新发布了",
    detail: "交出方（{from}）的模型 {producing} 和接收方（{to}）的模型 {consuming} 都是新版本。",
    caveats: [
      "两侧同时变化：本页不把任何一条证据的变化归到某一侧。",
      "重新发布不代表修复已经发生；针对旧版本作出的判定不能归到新版本。",
    ],
  },
  unrecognised: {
    headline: "记录的模型版本比较无法识别，按原值显示",
    detail:
      "记录给出的变化模型与本记录的交出方、接收方对不上，或两个字段互相矛盾。本页不猜是哪一侧。",
    caveats: [],
  },
};

export const REISSUE_NEUTRAL = "本页只说明哪一侧变了、记录证明了什么，不根据重新发布的方向预判好坏。";

// The sentences that must not be misread. Shown open on the recheck screens,
// never inside a collapsed block.
export const RECHECK_LIMITS = [
  "“比较依据一致”不代表整个交接不用复核。",
  "成员不在了、或找不到对应证据，不代表问题已修复。",
  "模型重新发布（不论哪一侧）不代表修复已经发生。",
  "“只有模型版本变了”不等于检查结果的内容变了。",
  "“无法比较”不是“证据缺失”：旧记录没保存比较依据时，本页如实显示无法比较。",
];

export const RECHECK_CANNOT = [
  "发起新的复检或上传新模型",
  "把事项标记为已解决、关闭或接受风险",
  "指派或通知责任人",
  "在 Revit 中打开或定位构件",
  "导出复检记录",
];

export const UNRECOGNISED = "未识别的值，按原值显示";

function glossed(table, value) {
  if (Object.hasOwn(table, value)) return { known: true, text: table[value] };
  return { known: false, text: UNRECOGNISED };
}

export const absence = (value) => glossed(ABSENCES, value);
export const disposition = (value) => glossed(DISPOSITIONS, value);
export const conditionState = (value) => glossed(CONDITION_STATES, value);
export const carryOverReason = (value) => glossed(CARRY_OVER_REASONS, value);

// Shown on every refusal, whatever the code: clearing the reason this run was
// refused is not a promise that the next one is assessable.
export const REFUSAL_SCOPE_NOTE = "处理当前拒绝原因不保证随后可评估；其余限制尚未由本次运行验证。";
