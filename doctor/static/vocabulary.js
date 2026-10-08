// Plain-language glosses for codes the Framework already emits. A gloss sits
// beside the original code and never replaces it; a code not listed here is
// shown as unrecognised with its raw value, not mapped to the nearest state.

// The two entries, in the manager's words. The second is deliberately not
// called "real input": nothing can be imported here, and what it shows is one
// attempt to check the project that ships with the repository.
export const MODE_LABELS = {
  fixture: "模拟示例",
  real: "随附项目的检查尝试",
  // A run somebody finished in a workspace named when the server was started.
  // Not "upload" and not "your model": nothing can be chosen from the page.
  workspace: "工作区里的真实检查",
};

//: The adapter names its scenarios; these are this preview's words for them.
//: An unlisted name is shown as the adapter gave it.
export const RUN_LABELS = {
  "member-evidence": "一次首次检查：交了模型，发现这些事项",
  "pair-verdicts": "同一份检查记录：成对构件的判断（模拟示例）",
  // One example is carried end to end in this revision and has a name that says
  // what it shows; its name states only what its record holds (no model was
  // re-issued, and a verdict differs), which a test pins. What the example was
  // *given* is a different statement and lives in EXAMPLES, shown in the
  // directory only. The others keep a number until they are written up the
  // same way.
  "recheck-both-reissued": "复检记录 1（模拟示例）",
  "recheck-comparison": "复检记录 2（模拟示例）",
  "recheck-consuming-reissued": "复检记录 3（模拟示例）",
  "recheck-key-change-only": "复检记录 4（模拟示例）",
  "recheck-member-gone": "复检记录 5（模拟示例）",
  "recheck-prior-without-basis": "复检记录 6（模拟示例）",
  "recheck-producing-reissued": "复检记录 7（模拟示例）",
  "recheck-producing-reissued-content-changed": "复检记录 8（模拟示例）",
  "recheck-requirement-relaxed": "模型未改，但交接判断发生变化",
  "recheck-semantics-changed": "复检记录 10（模拟示例）",
  "real-refusal": "对随附样例项目的一次检查尝试",
};

// The example directory, in the order a manager should meet the examples: an
// ordinary first check, then a recheck of the same record. `question` is what a
// manager would open the example to find out; `given` is what the example was
// handed, written by whoever built the example. Neither is something a run
// derived, so both are shown in the directory only, under EXAMPLE_NOTE, and
// never on a result page.
//
// The adapter's `scenario_index()` returns a name and a mode and nothing else,
// so these sentences are this preview's transcription of the adapter's own
// description of the scenario. They belong in the adapter's index.
export const EXAMPLES = {
  "member-evidence": {
    step: "第一步",
    question: "交出方交了模型：有哪些事项要处理，各由谁处理，每一项要做什么？",
    given:
      "这个示例被给了：随附样例项目的两份模型；处理团队的安排，以及人工判定" +
      "（是否穿过、洞口情况、两侧模型是否对齐），由示例设定。",
  },
  "recheck-requirement-relaxed": {
    step: "第二步",
    question: "同一份记录复检之后：两侧模型都没有重新发布，却有判断变了。变的是哪一项，为什么？",
    given: "这个示例被给了：一条被引用的检查要求放宽了；交出方和接收方的模型版本都没有变。",
  },
};

// Which example rechecks the record of which. A statement about two adapter
// scenarios that the page cannot check from one envelope; a test holds it
// against the adapter (the recheck's prior digest is the first record's).
export const FOLLOW_UP = {
  "member-evidence": "recheck-requirement-relaxed",
};

export const EXAMPLE_NOTE =
  "示例说明由搭建示例的人提供，只说这个示例被给了什么；它不是检查得出的结论。" +
  "检查得出了什么，只看结果页。";

// The first screen: who this is for, what it answers, what it can do today —
// and, in the same breath, what it cannot.
export const HOME = {
  title: "查看模型交接中仍需处理的事项",
  lede:
    "帮助 BIM 经理了解：一次交接前检查发现了什么；复检之后，哪些判断变了、" +
    "哪些事项仍需处理、每一项涉及哪些构件、依据是什么、下一步做什么。",
  status: "当前为示例预览：Revit 文件本身（.rvt）不能导入，也不提供整体合规或可施工结论。",
  // Said instead of `status` when the server was started with a workspace:
  // the home then offers a real check beside the examples.
  statusWithWorkspace:
    "当前同时提供两样：启动服务器时指定的工作区里一次已经跑完的真实检查，以及模拟示例。" +
    "工作区里的检查不能在页面上选择或更换模型；Revit 文件本身不能导入，也不提供整体合规或可施工结论。",
  // Said instead of `status` when the server could not be asked whether it was
  // started with a workspace: neither "examples only" nor "a real check" is known.
  statusWorkspaceUnknown:
    "未能确认服务器是否指定了工作区，所以这里没有真实检查的入口；这不等于没有工作区，错误原文在下面。" +
    "模拟示例照常可看。Revit 文件本身不能导入，也不提供整体合规或可施工结论。",
  example: {
    title: "看一个模拟示例",
    body:
      "从一次首次检查出发：找到需要处理的事项，看清涉及的构件、要做什么、由谁处理、" +
      "完成后拿什么复检；然后再看同一事项复检后的变化。示例里模拟的内容，页面上逐处标明。",
    action: "选择模拟示例",
  },
  attempt: {
    title: "查看随附项目的检查尝试",
    body:
      "仓库随附一个样例项目。对它的检查尝试没有开始评估；这里说明原因。" +
      "这个入口不是导入入口：只看这个样例项目，不能换成别的模型。",
    action: "查看这次检查尝试",
  },
  cannot: [
    "导入 Revit 文件本身（.rvt），或在示例和工作区入口里选择、更换模型",
    "给出整体合规、可施工或“可以交付”的结论",
    "写回模型、上传到云端，或在 Revit 里打开构件",
  ],
  canHeading: "现在可以做什么",
  cannotHeading: "现在还不能做什么",
  cannotNote: "这些功能没有实现，所以页面上没有对应的入口。",
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
    short: "真实检查输出",
    long: "未带模拟标记的检查结果引用：来自真实的检查运行，是真实 IFC 模型按真实规则检查的产物。",
  },
  "finding-fixture": {
    key: "fixture",
    short: "模拟的检查结果",
    long:
      `带模拟标记（以 ${FIXTURE_MARKER} 开头）的检查结果引用：由示例生成，` +
      "不是任何真实检查运行的输出。",
  },
  "determination-fixture": {
    key: "fixture",
    short: "模拟的人工判定",
    long: "带模拟标记的判定引用：由示例提供，没有任何协调评审真的发生过。",
  },
  "determination-unmarked": {
    key: "unmarked",
    short: "来源未标注的判定",
    long:
      "未带模拟标记的判定引用：判定不是检查运行的输出，本界面也没有可核依据说明它来自哪里，" +
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
  "本页每条引用旁的来源标注按该条引用自身判定（是否带模拟标记），不按整页或整份记录推断：";

// The policy row is not a citation and carries no marker, so nothing in the
// envelope says whose decision it was. The row states what the record carries
// and says the source is not in it — true of every row, which is what the
// per-row rule requires.
export const POLICY_SOURCE_NOTE =
  "这条登记的来源没有随记录返回：它是记录携带的项目设定，不能据此判断它是项目的决定还是示例的设定。";

// Shown at the head of every example page, whichever record it shows — so it
// says which kinds a conclusion's evidence may be, never which this page has.
export const DEMO_NOTICE =
  "模拟示例：示例中的项目设定，包括处理团队安排、证据方法的接受等，是演示用设定，不代表真实项目决定；" +
  "一个结论的证据可能是真实检查的结果、模拟的检查结果或模拟的人工判定，" +
  "具体是哪一种，看每个结论旁的“依据”一行（按逐条引用标明）。不能用于正式项目决定，也不能导出正式检查记录。";

// The short line at the head of every example page; DEMO_NOTICE above is what
// it opens to. `lead` is true of every example. `cites` names the kinds of
// evidence **this record** cites, one per kind actually found among its
// citations (each decided from that citation alone), so it never says "all
// real" or "all simulated" of a record that mixes them. Which kind one
// conclusion rests on stays on the "依据" line beside that conclusion.
export const SOURCE_SUMMARY = {
  lead: "随附的模拟示例，不是你的模型；团队等项目设定为演示用，不能用于正式项目决定。",
  cites: "这份记录的结论引用了：{kinds}，逐条标在结论旁的“依据”一行。",
  citesNone: "这份记录的结论没有引用证据。",
  noRecord: "结论引用的证据是真实的还是模拟的，逐条标在结论旁的“依据”一行。",
  kinds: {
    "finding-real": "真实检查输出",
    "finding-fixture": "模拟的检查结果",
    "determination-fixture": "模拟的人工判定",
    "determination-unmarked": "来源未标注的判定",
  },
  join: "、",
  lastJoin: "、",
  more: "来源说明",
};

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
    text: "仍在本次检查范围内；判断与条件另看",
    next: "看下面记录给出的当前情况：现在的判断、下一步和处理角色都以它为准。",
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
      "记录没有为这一对构件给出下一步。请核对让它不再被配对的那份依据（见“记录给出的原因”）" +
      "是不是你认可的结论；原来的问题没有被证明已修复。",
  },
  "outside-declared-scope": {
    text: "本次未声明该范围，不等于问题解除",
    next: "这个构件本次没有被重新检查。需要结论时，要重新发起一次包含它的复检；本预览不能发起。",
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
    text: "不可比较：对应的构件不完整",
    plain:
      "无法对原复检条件下结论：原来的构件有的已经不在本次记录里，条件没有完整的对象可以检查。" +
      "这不代表条件已满足。",
  },
  "no-recheck-condition": {
    text: "原记录没有复检条件",
    plain: "原记录没有复检条件：原来的判断没有留下待办。",
    // Any prior verdict but READY: the record gives no condition, and that
    // is all it says. Nothing is left outstanding only after a READY.
    plainNotReady: "原记录没有给出复检条件。",
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
    "验证运行里有对应的检查结果，但本次记录没有引用它。",
  "sealed-citation-has-no-comparison-basis":
    "原记录封存时没有保存这条引用的比较依据（旧版本的记录）。本页不会用当前规则去补造，" +
    "所以只能如实显示无法比较。",
  "comparison-basis-version-unknown": "原记录保存的比较依据，是本系统不认识的版本。",
  "subject-not-present":
    "这条证据所针对的构件，在本次记录里已经不在（去向见“记录给出的原因”）。构件不在不等于已修复。",
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
    "检查要求没有变，检查结果内容变了。这一行不记录结果是变好还是变差，请看当前判断。",
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
      "交出方重新发布可能改变了穿越关系或涉及的构件范围，不能据此说接收方的工作（例如开洞）已经做好。",
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
  "构件不在了、或找不到对应证据，不代表问题已修复。",
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

// The sealed verdict beside the current one, as the record gives both. Three
// groups and their counts; no group is an overall status and none says a member
// was resolved. "Changed" is a fact about two recorded verdicts, not a judgement
// about why.
export const VERDICT_GROUPS = {
  changed: {
    label: "判断变了的",
    none: "没有判断变了的项。",
    notes: {
      none:
        "两侧模型都没有重新发布，这些项的判断却变了：变化不来自模型改动。" +
        "每一项的旧证据写明变了的是什么。",
      reissued:
        "模型重新发布过。判断变了，不说明原来的问题怎样了；" +
        "每一项的旧证据写明变了的是什么。",
      unrecognised: "判断变了，不说明原来的问题怎样了；每一项的旧证据写明变了的是什么。",
    },
  },
  unplaced: {
    label: "记录没有给出当前情况的",
    none: "每一项记录都给出了当前情况。",
    note: "这些项现在是什么判断，记录没有说。构件不在了不代表问题已修复。",
  },
  unchanged: {
    label: "判断没有变的",
    none: "没有判断保持不变的项。",
    note: "判断没有变，不代表证据没有变；旧证据的情况见每一项。",
  },
};

// Which items the record gives a next step for. The split is the presence of a
// next action on the place the record itself named for the item — nothing is
// read off the verdict word, and no group is an overall status. The unit is the
// item: an element, or a pair, under one activity of the receiving side.
export const ACTION_GROUPS = {
  open: {
    label: "需要处理的事项",
    summary: "记录给出了处理动作",
    none: "记录没有为任何一个事项给出处理动作。",
    note: "每个事项的页面写明涉及的构件、要做什么、由谁处理、完成后拿什么复检。",
  },
  unplaced: {
    label: "需要人工核对的事项",
    summary: "记录没有给出当前情况，需要人工核对",
    none: "每个事项记录都给出了当前情况。",
    note: "这些事项现在是什么判断，记录没有说。构件不在了不代表问题已修复。",
  },
  none: {
    label: "记录没有给出后续处理动作的事项",
    summary: "记录没有给出后续处理动作",
    none: "没有这样的事项。",
    note: "记录没有为下面这些事项给出后续处理动作。每一行的结论各自成立，范围写在它旁边。",
  },
};

export const ITEM_UNIT =
  "一个事项是一个构件（或被放在一起评估的一对构件）在接收方的一项工作上的结论。" +
  "同一个构件可以出现在几个事项里，所以事项数不是缺陷数。";

// The record's verdict words as a manager says them. A label is never shown on
// its own: it always sits beside the work and the item it is about, and
// "可以开始" in particular is never said of a handover as a whole. A word not
// listed is shown as it came and is not folded into one of these three.
export const VERDICT_LABELS = {
  READY: "可以开始",
  BLOCKED: "受阻",
  UNKNOWN: "无法判断",
};

// What stays beside a conclusion, each only where it applies.
export const BESIDE = {
  // A READY: what it covers, and that it is not the handover.
  readyScope: "只对这一个事项、这项工作、所列的模型版本成立；不代表整次交接完成。",
  // An UNKNOWN: not a clean bill, and not a fault of the program.
  unknown: "“无法判断”说的是这项工作能否开始无法判断：不等于这个构件没有问题，也不是系统出错。",
  // The asset-identity problem types.
  assetIdentity: "资产标识的取值从哪里来、对应哪个 Revit 参数，记录未提供。",
  // An assignment is a row in the record, not a dispatch.
  team: "处理团队是记录里的安排，不代表已经派发。",
  simulatedTeam: "示例处理团队",
  noTeam: "记录未提供",
  defaultRole: "默认处理角色（规则给出的默认，不是指派）",
  unchanged: "复检前后未变",
};

// Beside a READY of one particular activity: what its evidence did and did not
// establish. Keyed by activity; an activity not listed adds nothing.
export const READY_NOTES = {
  "ceiling-and-bulkhead-geometry": [
    "规则只证明构件有楼层或空间归属，没有验证接收方模型有对应楼层。",
    "这个结论靠的是两侧模型的对齐确认，不是共享定位标记通过。",
  ],
};

// Where a verdict's evidence came from, said beside the verdict. The tags are
// decided per citation from its own marker; these are the words around them.
export const BASIS_WORDS = {
  simulated: "这个结论建立在模拟证据上：",
  real: "这个结论的依据：",
  sharedSimulated: "同组事项共用的依据，其中有模拟证据：",
  sharedReal: "同组事项共用的依据：",
  none: "这个结论没有引用任何证据。",
  gaps: {
    "no-finding": "没有任何检查结果（真实的缺席）",
    "no-determination": "还没有判定（真实的缺席）",
    "not-applicable-finding": "有检查结果，但检查不适用，没有覆盖到它",
  },
};

// The action and recheck sentences, one pair per problem type: the BIM
// reviewer's table and, for the uncovered asset identity, the product's ruling.
// They were written for one Pack at one version and hold for nothing else: a
// record under any other Pack id or version has no sentence, says so, and keeps
// the Pack's own words in the source fold. vocabulary-en.js holds the same
// obligations in English; the record's route words are never shown as what to do.
// No sentence names a Revit parameter or an export mapping — the Pack says
// those are project-specific and does not name them either.

export const ACTION_PACK = { id: "interdisciplinary-coordination-readiness", version: "0.1.0" };

export const ACTIONS = {
  "missing-project-asset-identity": {
    action: "在源模型里给这个构件补上本项目约定的资产标识属性（见所列属性集和属性名），重新导出",
    recheck: "重新发布的模型上，这个构件在所列每条要求下都通过",
  },
  "asset-identity-not-evaluated": {
    action:
      "现有资产标识规则没有覆盖到这个构件，所以它有没有资产标识还没有被评估，不能判断是否缺少；" +
      "这项工作能否开始也因此无法判断。先确认项目约定是否要求它具备资产标识，" +
      "以及规则该不该覆盖到它。在确认之前，这不表示它必须具备资产标识。",
    recheck: "范围内每个构件在所绑定的要求下都有评估结果",
  },
  "in-model-position-not-evaluated": {
    action:
      "这不是已知的模型缺陷。它的空间归属目前还没有评估：空间归属的检查规则没有覆盖到这个构件。" +
      "这一步是扩展规则的适用范围，让检查覆盖到它，而不是改模型；覆盖并运行之后，才知道要不要改模型",
    recheck: "范围内每个构件在所绑定的要求下都有检查结果",
  },
  "penetration-not-determined": {
    action:
      "这不是已知的模型缺陷。还没有协调评审判定它是否穿过接收方的构件；" +
      "需要开一次评审，记录“不穿过”或写明穿过哪些构件",
    recheck: "针对所列模型版本，有一份评审判定记录",
  },
  "missing-corresponding-opening": {
    action:
      "在接收方模型里、被穿过的构件上建出洞口或竖井，不要做成交出方模型里的空洞。穿过几个构件就要几个洞口",
    recheck: "这一对的开洞核查结果为“洞口已建且已关联”。只建洞不够",
  },
  "cross-model-alignment-not-confirmed": {
    action: "这不是已知的错位。还没有人按项目接受的方法确认两侧模型对齐；需要针对所列模型版本做一次并记录",
    recheck: "对齐确认已做，结果为已对齐，写明模型版本",
  },
  "mep-element-not-spatially-assigned": {
    action: "在源模型里把构件放到正确的标高上（项目要求空间归属时，再放进对应的空间），重新导出",
    recheck: "重新发布的模型上，这个构件的空间归属要求通过",
  },
  "cross-model-misalignment": {
    action:
      "重新获取项目共用的坐标基准，按共用原点重新导出（不靠移动几何），再按项目接受的方法重做对齐确认",
    recheck: "针对新版本重做对齐确认，结果为已对齐",
  },
  "opening-not-verifiably-linked": {
    action: "在接收方模型里，给洞口补上指回穿过它的那个构件的关联。一个洞口供几个构件穿过，每个各要一条",
    recheck: "这一对的关联核查结果为已关联",
  },
  "opening-status-not-determined": {
    action: "这不是已知的缺洞。开洞情况的评审没完成：洞口是否已建、是否已关联",
    recheck: "核查给出明确结果（已关联／已建未关联／未建）",
  },
};

// What a cited check result required and found comes only from the returned
// data's `finding_details`, which copies eight fields out of the validation run
// the citing record names. The page shows them as they came. It reads no rule
// file, and states no required value, Revit parameter or export mapping — the
// run holds none of them. A citation with no entry has none, and says so.
//
// The rule's own sentences (`expected`, `reason`, `citation`) are English and
// are shown as the rule wrote them. A reason this preview has words for is
// glossed beside the original by exact match; any other is shown alone.
export const DETAILS_WORDS = {
  heading: "具体缺什么",
  absent: "记录未提供：返回数据里没有这条引用的要求明细。",
  determinations:
    "这个结论引用的是人工判定，不是检查结果；判定没有要求明细。缺的是什么，见上面的结论和“要做什么”。",
  nothingCited: "这个结论没有引用任何检查结果，所以没有要求明细可以显示。",
  requirement: "不满足的要求",
  requirementMet: "要求",
  rule: "规则编号",
  status: "那次检查的结果",
  reason: "原因",
  actual: "那次检查观察到的值",
  noActual: "那次检查没有观察到值",
  hasActual: "那次检查观察到了值；本页不显示取值",
  expected: "规则的原话（英文）",
  source: "规则给出的出处（英文原文）：",
  projectAssumption: "这是本项目假定的要求（ProjectAssumption），不是通用要求。",
  gap: "要填什么值、对应哪个 Revit 参数，记录未提供。",
  // On a recheck row: whose words these are, and what they do not establish.
  prior:
    "复检前那次评估时，这条证据的要求和结果如下。有这段说明不等于这一行可以比较；这一行的状态以上面写的为准。",
  currentAbsent: "本次记录引用的对应证据：要求明细记录未提供。",
};

// The label a requirement carries when the project, and not a standard, asks
// for it. Read off the entry's own `labels`; the page does not assert it.
export const PROJECT_ASSUMPTION = "ProjectAssumption";

// A check's own three results. On the workspace pages these are the only
// result words: no handover assessment was made there, so no verdict is said.
export const FINDING_STATUS = {
  FAIL: "不通过",
  PASS: "通过",
  "N/A": "不适用",
};

export const REASON_GLOSSES = {
  "The required property set does not exist":
    "所要求的属性集不存在（要让导出写出这个属性集以及其中所要求的属性，不是给已有属性填值）",
  "Requirement satisfied.": "要求已满足",
  'The predefined type "NOTDEFINED" does not meet the required type':
    "预定义类型“NOTDEFINED”不属于要求的取值",
  "No applicable elements exist in this model.": "这个模型里没有这条要求适用的构件",
};

// What each verdict word means, said once in "how to read this page" and not
// beside every item.
//
// A verdict is a statement about one activity of the receiving side, in an
// assessed scope, against a named model version (Checkpoint B section 1, "The
// four verdicts, defined once"). Each sentence therefore says what the verdict
// means for that work — can start, is prevented, cannot be decided — and not
// only what became of the evidence: "a check passed" is not what READY says.
export const VERDICT_WORDS = {
  READY:
    "必要的证据齐全且满足验收条件，没有未解决的阻碍，也没有证据缺口：在本次评估范围内，这项工作可以开始",
  BLOCKED: "有一项已知未满足的要求，阻止这项工作",
  UNKNOWN: "回答这个问题所需的证据没有产生，这项工作能否开始无法决定：既不能放行，也不能拒绝",
};

export const VERDICT_SCOPE =
  "每个判断只针对接收方的一项工作、本次评估范围内的这一项，以及所列的模型版本；它不是“模型好不好”的总评，也不是“某项检查通过了”。";

// Said beside the verdict word, not only among the evidence rows, whenever the
// record's carry-over rows for the same sealed group say a requirement was
// edited. It places two recorded facts side by side and draws nothing from them.
export const REQUIREMENT_CHANGED_NOTE =
  "记录同时显示：和这一项放在一起评估的旧证据里，有 {count} 条的检查要求变了；记录不说明是放宽还是收紧。" +
  "读这个结论时要一并看，逐条见“复检前的证据”。";

// The result a verdict rests on: the outcome the record gives at the end of the
// path, keyed `<evidence requirement>/<outcome>` — the Pack's own two
// vocabularies. A READY reached through "penetrates nothing" says so: it is not
// a statement that an opening is in order. The storey sentences say what the
// bound rules check — containment in a storey or a space — and no more: they do
// not check that the receiving model has the same storey.
export const LEAF_READINGS = {
  "asset-identity/satisfied": "适用于它的项目资产标识要求评为通过，并且它确实被评估到",
  "asset-identity/unmet": "项目资产标识的要求没有满足",
  "asset-identity/not-yet-evaluated": "资产标识的规则没有覆盖到它",
  "in-model-position/satisfied": "它有楼层或空间归属",
  "in-model-position/unmet": "它没有楼层或空间归属",
  "in-model-position/not-yet-evaluated": "楼层或空间归属的检查没有覆盖到它",
  "cross-model-alignment/confirmed":
    "已有记录确认两侧模型对齐到共同的基准（按项目接受的方法，针对所列模型版本）",
  "cross-model-alignment/misaligned": "对齐确认的结果是两侧模型没有对齐",
  "cross-model-alignment/not-yet-confirmed": "还没有对齐确认",
  "penetration-determination/no-penetration":
    "已有协调评审判定：它不穿过接收方模型里的任何构件。不穿过就不需要开洞，所以开洞情况没有被评估——这不是“开洞没问题”",
  "penetration-determination/penetration-confirmed": "已有协调评审判定：它穿过接收方模型里的构件",
  "penetration-determination/not-yet-determined": "还没有协调评审判定它是否穿过接收方模型里的构件",
  "opening-status/cross-referenced": "这一对：洞口已建在被穿过的构件上，并且已关联到穿过它的这个构件",
  "opening-status/modelled-not-cross-referenced":
    "这一对：洞口已建在被穿过的构件上，但没有关联到穿过它的这个构件",
  "opening-status/not-modelled": "这一对：被穿过的构件上没有建出洞口",
  "opening-status/not-yet-determined": "这一对：开洞情况的评审还没有完成",
};

export const LEAF_READING_WORDS = {
  label: "这个结论依据的结果",
  notCarried: "记录没有给出这一项现在依据的结果",
  unglossed: "本界面没有这个结果的中文说明，见追溯信息",
};

// Which side of the handover a model is on, looked up from the record's own
// comparison. A side is not a discipline, and nothing here names one.
export const HANDOVER_SIDES = {
  producing: "本次交接中交出方的模型",
  consuming: "本次交接中接收方的模型",
};

// What can truthfully be said about one element from the five fields the
// preview is handed (name, IFC class, storey, GlobalId, model). Discipline is
// not among them, and a model identifier is not a discipline statement.
export const ELEMENT_WORDS = {
  unnamed: "模型中没有填写名称",
  noFacts: "记录没有返回这个构件的可读信息",
  noStorey: "模型中没有楼层归属",
  noDiscipline: "记录未提供专业信息；本界面不从模型标识推断专业",
  modelIsNotDiscipline: "这是模型标识，不是专业声明",
  noClassName: "本界面没有这个类别的中文名",
  naming:
    "名称取自模型文件本身，可能为空，也可能与别的构件重名；要在模型里定位，请用 GlobalId。",
};

// Chinese names for the IFC classes this preview has words for. The IFC class
// stays beside the name; a class not listed is shown as it came.
export const IFC_CLASS_NAMES = {
  IfcAirTerminal: "风口",
  IfcChimney: "烟囱",
  IfcDuctSegment: "风管段",
  IfcRoof: "屋顶",
  IfcSlab: "楼板",
  IfcWall: "墙",
};

// The receiving side's work a verdict is about, in this preview's Chinese. The
// name follows the Pack's `label`; `needs` restates what Checkpoint B section 1
// ("What Architecture does next with it") says that work needs from the
// handover. One not listed is shown as it came.
export const ACTIVITY_NAMES = {
  "builders-work-openings": {
    name: "土建预留开洞",
    needs: "要知道交出方的构件在哪里穿过墙、楼板和屋顶，才能在这些构件上开洞。",
  },
  "ceiling-and-bulkhead-geometry": {
    name: "吊顶平面与包封布置",
    needs: "要知道交出方的设备在哪一层、在什么位置，才能围着它画吊顶分区和包封。",
  },
  "schedules-and-room-data-sheets": {
    name: "房间数据表与设备明细表",
    needs: "要每件设备都带有项目的资产标识，明细表才能按它编排。",
  },
};

// The Pack's ten resolution kinds as a short name for the problem. A BLOCKED
// kind is a known defect in a source model; an UNKNOWN kind opens by saying it
// is not a *known* one — the Pack's words are "not a known defect", which is
// less than "not a defect".
export const RESOLUTION_KINDS = {
  "missing-project-asset-identity": "缺少本项目约定的资产标识",
  "asset-identity-not-evaluated": "不是已知的模型缺陷：现有资产标识规则没有覆盖到这个构件",
  "mep-element-not-spatially-assigned": "它没有楼层或空间归属",
  "in-model-position-not-evaluated": "不是已知的模型缺陷：楼层或空间归属的检查没有覆盖到它",
  "cross-model-misalignment": "两侧模型没有对齐到共同的基准",
  "cross-model-alignment-not-confirmed": "不是已知的错位：还没有人确认两侧模型对齐",
  "penetration-not-determined": "不是已知的模型缺陷：还没有协调评审判定它是否穿过接收方的构件",
  "opening-not-verifiably-linked": "洞口已建，但没有关联到穿过它的这个构件",
  "missing-corresponding-opening": "它穿过的构件上没有建出对应的洞口",
  "opening-status-not-determined": "不是已知的缺洞：开洞情况的评审还没有完成",
};

// What a non-READY verdict costs the receiving side's work, as the Pack's route
// names it. Shown beside the code; one not listed is shown as it came.
export const CONSEQUENCE_KINDS = {
  "work-cannot-start": "这项工作不能开始",
  "work-suspended": "这项工作暂缓，等有结论再定",
  "rework-risk": "有返工风险",
  // Not a re-issue of the model: Checkpoint B's consequence is that rows keyed
  // to a placeholder have to be re-identified and the documents quoting them
  // re-issued. "重新发布" is kept for a model and is not used here; a document
  // is "重新出具", the source's word, not merely updated.
  "re-identification-and-reissue-risk": "有重新标识的风险：引用这些标识的文件届时也须重新出具",
};

// Why a check attempt did not start, by refusal code, and what would have to
// be true for one to start. A refusal is the system's answer to the request's
// conditions — not a fault of the program, which is shown on a different screen
// and never as one of these.
//
// The guidance stops at what this refusal named. It does not tell anyone to
// edit the shipped sample: that project is a public sample with nobody to take
// its staffing decisions, and for it the refusal is the correct end. Later
// gates this refusal did not test are not listed as part of this diagnosis.
export const REFUSAL_REASONS = {
  "team-mapping-decision-basis-illustrative": {
    title: "项目条件未满足：由谁处理的安排不是项目作出的决定",
    text:
      "这次请求所用的项目设定里，“哪个角色由哪个团队担任”的安排只是演示用的占位内容，不是项目作出的决定。" +
      "系统因此不生成评估结果：否则结果里的处理团队会被当成项目的真实安排。",
    action: [
      "在一个真实项目上，要让检查能够开始：需要项目负责人实际决定系统原文（折叠在下面）点名的每个角色由谁担任，然后如实记录。" +
        "这是一个人员决定，不是改一个标签。",
      "如果这次请求用的是随附的公开样例：它没有项目负责人。对它而言，这次拒绝就是正确的结果，不需要、也不应该去改它的设定。",
    ],
  },
};

export const REFUSAL_UNGLOSSED = {
  title: "系统拒绝了这次请求",
  text: "本界面没有这个原因的中文说明，请展开下面系统返回的原文。",
  action: [],
};

export const FAULT_WORDS = {
  fault: "程序故障：没有拿到检查数据",
  unavailable: "检查程序不可用",
  note: "这是程序自身的问题，不是对任何项目或模型的判断；没有任何检查结果可以显示。",
};

// What a reader may want once, and does not need beside every item.
export const HOW_TO_READ = "如何阅读这一页";

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

// The rest of the bundled project's refusal screen. The reason itself is in
// REFUSAL_REASONS; the system's own text is shown as it came, in its fold.
export const REFUSAL_PAGE = {
  title: "这次检查尝试没有开始评估",
  lede: "系统在评估开始前拒绝了这次请求，并给出了原因。这是对请求条件的答复：不是程序故障，也不是检查结果。",
  whyHeading: "为什么没有开始",
  needHeading: "要让检查能够开始，需要什么",
  onlyOne: "本次只返回这一个原因，没有其他环节的诊断。",
  noConclusion: "没有任何事项的结论、零问题统计或完成百分比；被拒绝不是“无法判断”，也不是一次没有问题的检查。",
  original: "系统返回的原文（英文）与拒绝码",
  attempt: "检查尝试",
  code: "拒绝码",
  contextMissing: "所提交的请求上下文尚未随拒绝返回。",
};

// ---------------------------------------------------------------------------
// The workspace entry: one real check, and its comparison with an earlier run
// ---------------------------------------------------------------------------
//
// A workspace envelope is a validation run and nothing more. No handover
// assessment was made, so these pages say no verdict, team, work consequence or
// "can start"; the result words are the check's own three (FINDING_STATUS).
//
// Every sentence that compares is about two statuses the adapter put side by
// side. None says a thing was mended, and none is used for a row only one run
// evaluated. Which run is the earlier one is the start-up command's word, and
// the pages say so.

// The home card, shown only when the server was started with a workspace.
export const WORKSPACE_HOME = {
  title: "查看一次真实检查",
  body:
    "启动服务器时指定了一个工作区，里面是一次已经跑完的检查：每个构件在每条要求下的结果。" +
    "若同时指定了前一次运行，还可以看两次的前后对比。这里只有检查结果，没有交接判断。" +
    "页面只查看这次已经跑完的检查，不能在页面上选择或更换模型。",
  action: "查看这次检查",
  unknown: "未能确认服务器是否指定了工作区（不等于没有工作区）。错误原文：",
};

// Short labels and the sentences around them. Every string a workspace page
// shows is here, so the wording can be reviewed — and later translated — in one
// place.
export const WORKSPACE = {
  directoryNote: "工作区只能在启动服务器时指定；这里不能选择、上传或更换模型。",
  directoryNone:
    "服务器启动时没有指定工作区，所以这里没有可以查看的检查。要查看，用下面的命令重新启动服务器：",
  startCommand: "python doctor/serve.py --workspace <工作区目录> [--prior <前一次运行的目录>]",
  openRun: "打开这次检查的结果",
  back: "← 返回首页",
  backToList: "← 返回结果列表",
  contextNoJudgement: "只有检查结果，没有交接判断",
  contextRun: "检查运行",
  resultTitle: "一次真实检查的结果",
  noJudgement:
    "这是一次检查的结果，不是交接判断：页面只说每个构件在每条要求下通过、不通过还是不适用，" +
    "不对任何工作能否开始下结论。",
  summary: { one: "本次结果：共 {count} 条检查结果", other: "本次结果：共 {count} 条检查结果" },
  unit:
    "单位是条：一条是一个构件在一条要求下的结果；模型里没有这条要求适用的构件时，是整个模型的一条。",
  compareLink: "看与前一次运行的对比",
  compareTeaser: "服务器启动时还指定了前一次运行。两次结果的前后对比：",
  checkedHeading: "检查了什么",
  ruleTitle: "要求",
  rulePredicate: "这条规则要求",
  ruleExpected: "规则的原话（英文）",
  ruleOrigin: "出处（返回数据的引文，英文原文）",
  ruleLabels: "返回数据的标签",
  productValidation: "返回数据的标签（ProductValidation）标明：这是一条产品验证规则。",
  noRuleNotes: "本界面没有为这条规则写中文说明；规则以返回数据里的英文原话为准。",
  noRequirement: "返回数据没有这条结果所属要求的说明。",
  listHeading: "逐条结果",
  filterLabel: "按 IFC Tag、名称或 GlobalId 查找",
  filterAll: "全部",
  filterNone: "没有符合筛选条件的结果。",
  filterShown: "显示 {shown} 条，共 {count} 条",
  columns: {
    status: "结果",
    tag: "IFC Tag",
    name: "名称",
    class: "类别",
    storey: "楼层（IFC）",
    model: "模型",
  },
  pickOne: "从结果列表里选一条，在这里看它的详情。",
  detailKicker: "一条真实检查结果",
  wholeModel: "整个模型",
  resultHeading: "结果",
  findHeading: "回到 Revit 找哪个对象",
  actionHeading: "要改什么",
  actionWhat: "改成什么",
  actionReads: "检查器读哪里",
  actionRevise: "在 Revit 里改哪里",
  actionUndecided: "还没有决定的",
  requirementHeading: "具体要求与这次检查的观察",
  reason: "原因（检查结果的原文）",
  actual: "观察值一栏",
  actualEmpty: "检查结果中为空。",
  actualHidden: "检查结果带有观察值；本页不显示取值。",
  recheckHeading: "复检时看什么",
  passHeading: "这条通过证明了什么",
  passProves: "它证明：",
  passDoesNotProve: "它不证明：",
  passNoValue: "通过的检查结果不带它读到的值：只记录了“要求已满足”。",
  passUnwritten:
    "通过只说明这条要求被判为满足；它能证明到哪里，本界面没有为这条规则写说明，请看规则原话。",
  notApplicable: "不适用：这个模型里没有这条要求适用的构件。不适用不是通过。",
  // Beside a failure only, and only when the requirement's own labels mark it a
  // product validation rule.
  failNotDefect:
    "不满足这条产品验证规则，不等于原项目的交付缺陷。这条规则的来源以返回数据的标签（ProductValidation）和出处原文为准。",
  noFinding: "这次检查里没有这一条结果。",
  identityHeading: "追溯信息：这次检查的运行号、规则集版本与模型文件",
  findingTrace: "追溯信息：这条结果的内部键",
  identity: {
    run: "检查运行号",
    ruleset: "规则集",
    asOf: "逻辑日期（运行配置给定，不是运行的时间）",
    checkers: "检查程序",
    models: "模型",
    modelId: "模型",
    declaredDiscipline: "项目清单声明的专业",
    filename: "文件",
    digest: "文件内容摘要（SHA-256）",
    tagSource: "IFC Tag 的来源",
    elementKey: "追溯用内部键",
    findingKey: "检查结果键",
    requirementKey: "要求键",
  },
  element: {
    name: "名称",
    class: "类别",
    storey: "楼层（IFC）",
    model: "所属模型",
    file: "模型文件",
    globalId: "GlobalId",
  },
};

// The IFC Tag, beside every Tag shown, and what is said when there is none.
// Which of the three sources applies is the returned data's `tag_source`; an
// element with no `tag` key under a readable file states no Tag in that file.
export const TAG_WORDS = {
  note:
    "IFC Tag 是导出时写进 IFC 的标记；Revit 导出的通常是构件的 ElementId。" +
    "核对：在 Revit 里用“按 ID 选择”选中这个 ID，看选中对象的名称和类别是否与本页相同；" +
    "相同再按它处理，不同就不要按这个 Tag 去改：在 IFC 查看器里按 GlobalId 定位，读出名称、类型和位置，" +
    "再在 Revit 里按这些找到对象并核对，然后在源模型里修改。",
  // Beside an element with a Tag: find it by that ID, not by storey.
  byIdNotStorey:
    "在 Revit 里按 ID 找对象，不要按楼层找：本页的楼层取自 IFC 文件里的空间归属，" +
    "不一定能和 Revit 明细表里的标高对上。",
  // Beside an element without a Tag: there is no ID on this page to find it by,
  // so only where the storey comes from is said.
  storeyFromIfc:
    "本页的楼层取自 IFC 文件里的空间归属，不一定能和 Revit 明细表里的标高对上，不要只按楼层去找。",
  sources: {
    "model-file": "模型文件里这个构件没有写 Tag。",
    "model-file-not-located": "没有找到这次检查读的那个模型文件，所以读不到 Tag。",
    "model-file-differs": "工作区里的模型文件已经不是这次检查读的那个版本，所以不读取 Tag。",
  },
  sourceNotCarried: "返回数据没有说明这个模型的 Tag 从哪里读，所以没有 Tag。",
  modelLevel: "这条结果针对整个模型，没有具体构件可找。",
  useGlobalId: "在 IFC 里定位用 GlobalId。",
  // The same facts in a table cell; the sentence above is in the detail.
  short: {
    "model-file": "文件里没有 Tag",
    "model-file-not-located": "未找到模型文件",
    "model-file-differs": "模型文件版本不同",
    notCarried: "来源未说明",
    modelLevel: "整个模型",
  },
};

// What the data's own words say, glossed by exact match only. A citation not
// listed is shown alone, as it came.
export const CITATION_GLOSSES = {
  "Product validation rule of this repository; not a project, owner, statutory or buildingSMART requirement. Values from IFC4 ADD2 TC1 IfcAirTerminalTypeEnum.":
    "本仓库的产品验证规则；不是项目、业主、法规或 buildingSMART 的要求。取值来自 IFC4 ADD2 TC1 的 IfcAirTerminalTypeEnum。",
};

// The label a requirement carries when it is a product validation rule. Read
// off the requirement's own `labels`; the page does not assert it.
export const PRODUCT_VALIDATION = "ProductValidation";

// Sentences about one rule, for the one rule set version they were written
// against. A `(ruleset id, version)` pair names exactly one set of rules — the
// rule set's own test refuses an edited rule under a kept version — so under
// any other rule set or version none of these is shown and the rule's English
// stands alone.
//
// Their sources: the rule set's README (what a pass says and does not say,
// where the checker reads the value from, USERDEFINED replaced by its text) and
// the BIM reviewer's selection and value decision (the four things a pass does
// not prove, the evidence still missing). No sentence says what value a pass
// read: a passing check result carries none.
export const RULE_NOTES_FOR = { ruleset: "product-validation", version: "1.0" };

export const RULE_NOTES = {
  "PV-001": {
    title: "风口要声明四种预定义类型之一",
    predicate:
      "每个适用的风口（IfcAirTerminal）都要声明预定义类型，取值是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一。" +
      "IFC4 还允许 USERDEFINED 和 NOTDEFINED；不接受它们是这条规则自己的决定，用它们的模型仍是有效的 IFC4。",
    passProves:
      "检查器按它的读取顺序取到的那一个值（类型上的值优先；类型声明 USERDEFINED 时是它的自由文本；" +
      "类型什么也没说时才读构件实例；没有类型时，实例声明 USERDEFINED 也是它的自由文本），逐字等于 DIFFUSER、GRILLE、LOUVRE、REGISTER 四个值之一。",
    passDoesNotProve: [
      "取值正确：四个值中任何一个都会通过，写成 GRILLE 也会通过。",
      "类型和构件实例的取值一致：类型上是四个值之一时，实例上写的值不参与比较；类型是 LOUVRE、实例是 DIFFUSER，也会通过。",
      "规则不接受的 USERDEFINED 没有出现：类型声明 USERDEFINED 时，检查器比较的是它的自由文本；" +
        "没有类型时，构件实例声明 USERDEFINED 也按它的自由文本比较。比较逐字、区分大小写；" +
        "文本恰好是 LOUVRE 会通过，写成 louvre、Louvre 或前后带空格则不通过。",
      "墙上有对应的洞口。",
      "风口所在的模型与风口所在的墙所属的模型已经对齐。",
      "任何工作可以开始，包括吊顶和开洞工作。",
    ],
    action: {
      what:
        "回到 Revit 源模型，让这个风口导出后的预定义类型是 DIFFUSER、GRILLE、LOUVRE、REGISTER 之一；重新导出 IFC，再检查。" +
        "NOTDEFINED 等于什么都没说。",
      reads:
        "检查器先看导出的 IFC 里它的类型对象：类型上是四个值之一，比较类型上的值；类型声明 USERDEFINED，比较它的自由文本；" +
        "类型什么也没说时，才读构件实例本身的值。这说的是检查器读 IFC 的顺序，不是 Revit 里该改的位置。",
      revise:
        "这个值在 Revit 里从哪里写出（类型还是实例、哪个参数、哪项导出设置），返回数据没有记录，本页不指定。" +
        "改之前先在 Revit 里确认；如果决定在类型上改，会作用于这个类型的全部实例。" +
        "一个 Revit 类型可能对应不止一个 IFC 类型对象，实例数按 Revit 类型算。",
      undecided:
        "取哪一个值、由谁决定和操作，返回数据都没有提供。规则只要求四个值之一，不判断哪一个对。",
    },
    recheck: "用同一规则集版本、同一组模型和同一导出设置重新检查，看这个构件在这条要求下的结果。",
    gaps: [
      "风口所在的墙上的洞口：需要对照风口所在的模型和这面墙所属的模型做协调评审判定；这项检查不比较两个模型的构件。",
      "风口所在的模型与风口所在的墙所属的模型是否对齐：需要一份对齐确认记录。",
      "取值是否选对：分类判断要另行记录；检查通过不能反过来证明分类判断正确。",
    ],
    // Beside a reason whose quoted value is free text rather than one of the
    // enumeration's values: the checker compared a USERDEFINED type's text.
    reasonFreeText:
      "引号里不是预定义类型的枚举值，而是自由文本：类型声明 USERDEFINED 时，检查器拿它的自由文本来比较；" +
      "没有类型时，构件实例声明 USERDEFINED 也是这样。",
  },
};

// The before/after page. The pairing, the rows only one run has and the models
// whose content changed are the adapter's; the page counts and arranges them.
export const WORKSPACE_COMPARE = {
  title: "复检对比：同一项检查，前后两次运行",
  lede: "下面的配对、未再评估和新出现都由返回数据给出，页面只计数和排列。",
  runsHeading: "两次运行",
  prior: "被指定为前一次的运行（启动时用 --prior 指定）",
  current: "本次运行（启动时用 --workspace 指定）",
  order: "哪一次在前，是启动服务器时的指定；返回数据本身不能证明先后。",
  same:
    "两次运行的规则集、各条要求的谓词、检查程序、逻辑日期和模型组都相同；其中任何一项不同，系统都会拒绝对比，" +
    "不给出任何一侧的结果。",
  changedHeading: "一、什么变了",
  differs: { one: "两次结果不同的：{count} 条", other: "两次结果不同的：{count} 条" },
  differsNone: "没有两次结果不同的。",
  unchanged: { one: "两次结果相同的：{count} 条", other: "两次结果相同的：{count} 条" },
  unchangedNone: "没有两次结果相同的。",
  transition: { one: "{prior} → {current}：{count} 条", other: "{prior} → {current}：{count} 条" },
  rows: { one: "{count} 条", other: "{count} 条" },
  notReEvaluated: {
    label: {
      one: "只在前一次有结果的（本次没有再评估）：{count} 条",
      other: "只在前一次有结果的（本次没有再评估）：{count} 条",
    },
    note: "这些只有前一次的结果，本次没有再评估。它们不是通过。",
  },
  newlyAppearing: {
    label: { one: "只在本次有结果的（新出现）：{count} 条", other: "只在本次有结果的（新出现）：{count} 条" },
    note: "这些结果前一次没有。",
  },
  inCurrent: {
    true: "构件还在本次的构件清单里",
    false: "构件不在本次的构件清单里",
    null: "整个模型的一条结果，不针对构件",
  },
  inPrior: {
    true: "构件在前一次的构件清单里",
    false: "构件不在前一次的构件清单里",
    null: "整个模型的一条结果，不针对构件",
  },
  whyHeading: "二、为什么会变：返回数据能说明的部分",
  changedModels: "两次之间内容变了的模型（返回数据列出）：",
  noChangedModels: "返回数据没有列出内容变了的模型：两次读的是同样的模型文件。",
  unchangedModels: "内容未变的模型：",
  why:
    "两次的规则集、要求谓词、检查程序和逻辑日期都相同。在返回数据比较过的这些输入里，两次之间不同的只有上面列出的模型文件内容；" +
    "模型文件里改了哪些地方，返回数据没有逐项列出。",
  notInData: "在 Revit 里改了什么、取值由谁决定、由谁操作，返回数据没有记录。",
  gapsHeading: "三、还缺什么证据",
  passLink: "一条通过证明了什么、没证明什么，见通过那几条的详情。",
  open: "查看",
  detailHeading: "和前一次运行比",
  detailPrior: "前一次的结果",
  detailCurrent: "本次的结果",
  detailNewly: "前一次运行没有这一条结果：它是新出现的。",
  detailNone: "返回数据的对比里没有这一条。",
  priorReason: "前一次的原因（原文）",
  currentReason: "本次的原因（原文）",
  noComparison: "服务器启动时没有指定前一次运行，所以没有对比。要对比，启动时加上 --prior。",
  elementMissing: "返回数据没有这个构件的可读信息",
};

// What is wrong with a workspace envelope's shape. Shown as a fault of the
// program, never as a result or a refusal.
export const ENVELOPE_WORDS = {
  missing: "outcome={outcome} 但缺少 {key}",
  unexpected: "outcome={outcome} 却同时带有 {key}",
};

// Why a comparison was refused, by code. Each is one precondition the adapter
// names; the code and the adapter's own sentence stay on the page beside it.
export const WORKSPACE_REFUSAL = {
  title: "这两次运行不能对比",
  lede:
    "系统拒绝了这次对比，并列出了全部原因。这是对请求条件的答复，不是程序故障，也不是检查结果：" +
    "任何一侧的检查结果都没有返回。",
  reasonsHeading: "为什么不能对比",
  actionHeading: "要能对比，需要什么",
  action: [
    "两次运行要用同一规则集（同一版本、同一内容）、同一组要求、同一检查程序、同一逻辑日期和同一组模型；" +
      "两次之间只能是模型文件的内容不同。",
    "确认启动时用 --prior 指定的确实是同一项检查的前一次运行；或者去掉 --prior 重新启动服务器，只看本次检查的结果。",
  ],
  scope: "处理这些原因之后能否对比，以下一次返回为准。",
  original: "系统返回的原文（英文）与拒绝码",
  code: "拒绝码",
  unglossed: "本界面没有这个原因的中文说明，见下面的原文。",
  noResult: "没有任何结果、零问题统计或完成比例：被拒绝不是一次没有问题的检查。",
};

export const WORKSPACE_REFUSAL_REASONS = {
  "ruleset-id-differs": "两次用的不是同一个规则集。",
  "ruleset-version-differs": "两次用的规则集版本不同。",
  "ruleset-digest-differs": "两次用的规则集内容不同（内容摘要不同）。",
  "requirement-set-differs": "两次评估的不是同一组要求。",
  "requirement-semantics-not-recorded": "有一次运行没有记录某条要求的谓词摘要，无法证明两次是同一个检查。",
  "requirement-semantics-differs": "同一条要求，两次的谓词不同：检查的内容改过。",
  "checker-differs": "两次的检查程序、版本或配置不同。",
  "as-of-differs": "两次运行的逻辑日期不同。",
  "model-set-differs": "两次检查的不是同一组模型。",
};

// ---------------------------------------------------------------------------
// Words that were written inline in the screens, moved here so that a second
// language is a second table and nothing else. Their text is unchanged.
// ---------------------------------------------------------------------------

// Pieces shared by several screens.
export const COMMON = {
  colon: "：",
  aside: "（{text}）",
  emptyList: "（记录中为空列表）",
  unknownMode: "未识别的入口（{mode}）",
  unnamedElement: "未命名构件",
  and: " 与 ",
  oneElement: "一个构件",
  twoElements: "一对构件",
  nElements: { one: "{count} 个构件", other: "{count} 个构件" },
  inModel: " · 模型 ",
};

// The context bar at the head of every screen but the home.
export const CONTEXT = {
  project: "项目 {project}",
  handover: "交接：{from} → {to} · {milestone}",
  workspaceRun: WORKSPACE.contextRun,
  noJudgement: WORKSPACE.contextNoJudgement,
  noResult: "本次没有检查结果",
  home: "返回首页",
};

// The example directory and the shipped project's entry.
export const DIRECTORY = {
  realNote: "仓库随附一个样例项目，下面是对它的一次检查尝试。这个入口只看这个样例，不能换成别的模型；检查自己的 IFC4 文件，用首页的“检查自己的 IFC 模型”。Revit 文件本身不能导入。",
  exampleTitle: "选择一个模拟示例",
  exampleIntro: "每个示例是一份检查记录。",
  empty: "这个入口下目前没有可以查看的内容。",
  exampleTag: "示例说明",
  open: "打开这个示例的结果",
  othersHeading: "其他模拟示例",
  othersNote: "这些示例还没有写说明，复检记录暂时只有编号；本轮没有改到它们。",
};

// The first-check result page.
export const FIRST = {
  back: "← 返回示例目录",
  title: "首次检查结果：需要处理的事项",
  runLine: "{mode}：{run}",
  summary: "本次结果：共 {items} 个事项，其中 {todo} 个需要处理",
  items: { one: "{count} 个事项", other: "{count} 个事项" },
  verdictLine: "：对应的那项工作 ",
  quietLine: "：{summary}（列在本页下方）",
  elementsLine: {
    one: "{unit}这份记录共涉及 {count} 个不同的构件。",
    other: "{unit}这份记录共涉及 {count} 个不同的构件。",
  },
  action: "要做什么",
  problem: "问题",
  openItem: "查看这一项：具体对象、要做什么、由谁处理、拿什么复检",
  // The fold on a first-check card. Closed by default; what it holds is also on
  // the item's own page, where what to do comes first.
  cardDetails: "构件信息和要做什么",
  cardElements: "构件信息",
  // The card's link to the item. The long `openItem` above lists what the item
  // page holds; on a first-check card that list would repeat on every card.
  openCard: "查看这一项",
  openHeading: { one: "{label}，按处理团队（{count} 个事项）", other: "{label}，按处理团队（{count} 个事项）" },
  team: "处理团队 ",
  teamCount: { one: "：{count} 个事项", other: "：{count} 个事项" },
  columns: { problem: "问题", work: "哪项工作：结论", count: "事项数" },
  quietHeading: { one: "{label}（{count} 个事项）", other: "{label}（{count} 个事项）" },
  separator: " ｜ ",
  nextHeading: "然后：看这份记录复检之后的变化",
  nextLink: "打开示例“{run}”",
  nextAfter: "。每个事项的页面里也有直达它复检变化的链接。",
  traceSummary: "追溯信息：记录标识、规则版本、记录原码",
  recordLink: "这份记录的请求范围、版本与来源",
  notRevised: "（该页尚未改版，仍是内部用语）",
  traceItem: "事项",
  traceOrdinal: "内部分组编号",
};

// "How to read this page", folded at the foot of the result and item pages.
export const READING_GUIDE = {
  verdictWords: "三个判断词",
  verdictLine: "{label}：{meaning}。",
  provenance: "证据来源的标注",
  teams: "处理团队与默认处理角色",
  teamsBody:
    "处理团队取自记录里的人员安排；默认处理角色是规则给出的默认，是安排的输入，不是指派。两者分开显示。",
};

// What the router and the envelope check say. A fault is the program's, never
// a statement about a project or a model.
export const APP = {
  loading: "正在读取检查记录…",
  noPage: "没有这个页面：{screen}",
  technical: "技术信息（原文）：",
  up: "返回上一级",
  notInMode: "这个入口下没有 {run}",
  invalid: "返回的数据不符合约定：{problem}。未显示任何结果。",
  unknownOutcome: "未识别的 outcome {outcome}",
  notObject: "返回的数据不是对象",
  modeMismatch: "返回数据的 mode 为 {got}，与所选入口 {want} 不一致",
  missingElements: "返回的数据缺少 elements",
  recordMissing: "outcome=record 但缺少 record",
  digestMissing: "outcome=record 但缺少 assessment_digest",
  recordWithRefusal: "outcome=record 却同时带有 refusal",
  refusalIncomplete: "outcome=refusal 但 refusal 缺少 code 或 text",
  refusalWithRecord: "outcome=refusal 却同时带有 record 或 assessment_digest",
};

// The page itself: its title, the skip link and the context bar's label.
export const PAGE = {
  title: "BIM Doctor 预览",
  skip: "跳到正文",
  contextLabel: "当前模式与上下文",
};

// The copy button beside an identifier.
export const COPY = {
  button: "复制",
  label: "复制 {value}",
  done: "已复制",
  manual: "请手动选择复制",
};

// The first-check item page.
export const ITEM = {
  missing: "记录中没有这一项",
  back: "← 返回事项列表（回到这一项的位置）",
  kicker: "首次检查事项 · {count}",
  conclusion: "一、结论",
  needs: "这项工作需要什么",
  actionHeading: "二、要做什么、由谁处理、完成后拿什么复检",
  followUpHeading: "二、后续",
  noFollowUp: "记录没有为这一项给出后续处理动作、处理团队或默认处理角色。",
  whichOne: "三、是哪个构件",
  whichTwo: "三、是哪两个构件",
  details: "四、{heading}",
  nextHeading: "然后：这一项复检后的变化",
  nextLink: "在示例“{run}”里看这一项",
  nextAfter: "。那是对这同一份记录的一次复检，同样是模拟示例。",
  basisSummary: "依据逐条：这个结论引用的证据",
  context: "背景引用：不是这个结论的依据，逐字显示。",
  traceSummary: "追溯信息：内部键与记录原码",
  keys: "内部键",
  ordinal: "内部分组编号",
  leaf: "终点 outcome",
  memberLink: "在明细页查看完整的证据路径",
};

// What to do, who handles it, what it costs the work, what a recheck must show.
export const ACTION = {
  what: "要做什么",
  team: "处理团队",
  consequence: "对这项工作的后果",
  recheck: "完成后拿什么复检",
  noSentence: "本界面没有为这条记录所用的版本写要做什么。记录所带的来源原文在下面的折叠里，它不是操作指令。",
  original: "来源原文（英文，记录所带）：供追溯，不是操作指令",
};

// One element, as the record describes it.
export const ELEMENT_CARD = {
  traceKey: "追溯用内部键",
  class: "类别",
  storey: "楼层",
  model: "所属模型",
  disciplineRow: "专业",
};

// The old evidence of a recheck, and the pieces around it.
export const EVIDENCE = {
  currentCitation: "本次记录引用的对应证据：",
  reason: "原因：",
  recordCause: "记录给出的原因（原文）：",
  trace: "追溯信息（记录原码与内容指纹）",
  priorDigest: "复检前的内容指纹",
  currentDigest: "本记录的内容指纹",
  none: "复检前的证据路径没有引用任何证据。",
  rows: { one: "（{count} 条）", other: "（{count} 条）" },
  empty: "（空）",
  glossaryCode: "记录里的代码",
  glossarySaid: "本页的说法",
  meaning: "“{label}”是什么意思",
  dispositionNow: "这个事项现在",
  currentMissing: "记录给出了这一项的当前位置（内部编号 #{ordinal}），但在本记录里找不到它；本页不另行对应。",
  memberLink: "在明细页查看和它一起评估的全部构件与证据",
  reissueColumns: {
    side: "交接的哪一侧",
    role: "角色（取自本次请求的交接）",
    model: "模型",
    reissued: "是否重新发布",
  },
  unrecognisedSide: "无法识别，见上",
  reissued: "重新发布了（新版本）",
  notReissued: "没有变（原版本）",
};

// A piece of work and what became of its verdict: unchanged, moved, or not
// given by the record. The placeholders are page pieces, not only text.
export const WORK = {
  unchanged: "{work}：{before} （{note}）",
  changed: "{work}：复检前 {before} → 现在 {now}",
  missing: "{work}：复检前 {before}；现在：记录没有给出",
};

// The recheck result.
export const RECHECK = {
  title: "复检结果",
  notRecheck: "这份记录不是复检记录，没有复检前后的对比可以显示。",
  unknownSuccessor: "这份记录承接了一条已封存的记录，但承接类型不是本页认识的复检：successor.kind = ",
  unknownSuccessorAfter: "。本页不把它当作复检来呈现。",
  resultTitle: "复检结果：需要处理的事项",
  summary: { one: "本次结果：共 {count} 个事项", other: "本次结果：共 {count} 个事项" },
  groupLine: { one: "{count} 个事项", other: "{count} 个事项" },
  groupSummary: "：{summary}",
  models: "模型：{headline}。",
  moved: { one: "{count} 个事项的结论和复检前不同：", other: "{count} 个事项的结论和复检前不同：" },
  requirementChanged: "复检前引用的 {count} 条旧证据里，有 {edited} 条的检查要求变了。",
  groupHeading: { one: "{label}（{count} 个事项）", other: "{label}（{count} 个事项）" },
  cannotHeading: "本预览做不了的事",
  cannotNote: "这些动作没有实现，所以页面上没有对应的按钮。",
  limitsHeading: "读复检结果时",
  sideModel: "{side}模型",
  detailsSummary: "复检前后的比较明细：模型、事项、旧证据",
  modelsHeading: "模型",
  itemsHeading: { one: "复检前记录里的事项（{count} 个），现在的情况", other: "复检前记录里的事项（{count} 个），现在的情况" },
  evidenceHeading: {
    one: "复检前引用的旧证据（{count} 条），和本次记录比较的结果",
    other: "复检前引用的旧证据（{count} 条），和本次记录比较的结果",
  },
  kindsNote: "检查结果和人工判定是两种证据，分开计数，不相加。",
  traceSummary: "追溯信息：记录标识、模型版本指纹、记录原码对照",
  priorDigest: "复检前记录的指纹（assessment digest）",
  currentDigest: "本记录的指纹（assessment digest）",
  noChange: "（记录中为空列表：没有模型变化）",
  versionColumns: { side: "", prior: "复检前记录", current: "本记录" },
  versionNote: "版本以内容指纹表示，不以文件名当版本。哪一侧变了取自记录的 changed_models，本页不比较指纹。",
  glossaryDispositions: "事项现在的情况：记录原码",
  glossaryConditions: "复检前留下的条件：状态原码（没有“整句条件已满足”）",
  glossaryStates: "旧证据比较：状态原码",
  glossaryReasons: "旧证据比较：原因原码",
  glossaryAspects: "变化方面：原码",
};

// One recheck item.
export const RECHECK_ITEM = {
  missing: "复检记录中没有这一项",
  back: "← 返回复检事项列表（回到这一项的位置）",
  kicker: "复检事项 · {count}",
  pairNote:
    "这两个构件已不再被配成一对检查：穿透判定现为“不穿透”（见下方记录给出的原因）。" +
    "这不等于开洞已建成，也不等于开洞缺陷已修复。",
  model: "模型",
  actionHeading: "二、要做什么、由谁处理、完成后拿什么复检",
  whichOne: "三、是哪个构件",
  whichTwo: "三、是哪两个构件",
  noCurrent:
    "记录没有给出这一项的当前情况，所以本页没有处理动作、处理团队或默认处理角色可以显示。" +
    "复检前记录里的这些信息也没有随复检记录返回。",
  conditionHeading: "四、复检前留下的结束条件，这次达到了吗",
  priorCondition: "复检前留下的结束条件：{text}。",
  end: "。",
  conditionNote: "这里只说复检前留下的结束条件被证明到了什么程度，与现在的结论分开读：结论变了，不等于原条件已满足。",
  originalSummary: "来源原文（英文）与记录原码：供追溯，不是操作指令",
  conditionBasis: "condition_basis（原文）",
  evidenceHeading: "五、复检前的证据",
  evidenceCount: { one: "和这一项放在一起评估的旧证据共 {count} 条", other: "和这一项放在一起评估的旧证据共 {count} 条" },
  requirementChanged: { one: "，其中 {count} 条的检查要求变了", other: "，其中 {count} 条的检查要求变了" },
  priorSources: "复检前引用的证据，来源：",
  currentSources: "本次记录引用的对应证据，来源：",
  rowsSummary: "逐条查看旧证据和比较结果",
  shared: {
    one: "记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 {count} 个事项共用下面这些行。",
    other: "记录把放在一起评估的一组构件的旧证据存在一处，不按构件拆开：这一组的 {count} 个事项共用下面这些行。",
  },
  noEvidence: "复检前这一组的证据路径没有引用任何证据。",
  priorOrdinal: "复检前的内部分组编号",
  currentLine: "现在的内部分组编号、verdict 与终点 outcome",
};

// The sentences recheck-model.js assembles from the tables above.
export const RECHECK_MODEL = {
  producing: "交出方",
  consuming: "接收方",
  listSeparator: "、",
  aspectsChanged: "{list}变了",
  aspectsSame: "，{list}未变",
  end: "。",
  unrecognisedAspect: "“{code}”（{unrecognised}）",
  unrecognisedKey: "key_changed = “{value}”（{unrecognised}）",
  onlyRekeyed: "{rekeyed}：证据内容和比较依据都没有变。",
};
