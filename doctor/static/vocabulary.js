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
  "recheck-comparison": "复检对比（夹具）",
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

export const DISPOSITIONS = {
  present: "当前仍有对应成员；裁决与条件另看",
  "element-deleted-in-reissued-model": "在重发模型中删除，不等于修复",
  "element-out-of-subject-class": "已不属于此活动对象类别，不等于修复",
  "pairing-no-longer-derived": "当前不再推导该成员对，不等于开洞已补",
  "outside-declared-scope": "本次未声明该范围，不等于问题解除",
};

export const CONDITION_STATES = {
  "named-outcome-observed": "仅命名结果已观察到；条件其余部分未检查",
  "named-outcome-not-observed": "未观察到命名结果",
  "no-machine-checkable-part": "条件没有可机检部分，需要人阅读",
  "not-comparable": "不可比较：对应成员集合不完整",
  "no-recheck-condition": "原记录没有复检条件",
};

export const CARRY_OVER = {
  carried: "仍被引用，且内容摘要相同",
  "determination-content-changed-under-the-same-reference":
    "同一引用下的判定内容已改变，原判定未被延续",
  "determination-not-attributable-to-this-context":
    "模型版本已变化，原判定无法归属当前上下文（不是证据不存在，也不是原判定错误）",
  "determination-not-cited-by-this-record": "本记录未再引用该判定",
  "finding-absent-from-the-cited-run": "该 finding 不在本记录依据的验证运行中",
};

function glossed(table, value) {
  if (Object.hasOwn(table, value)) return { known: true, text: table[value] };
  return { known: false, text: "未识别的值，按原值显示" };
}

export const absence = (value) => glossed(ABSENCES, value);
export const disposition = (value) => glossed(DISPOSITIONS, value);
export const conditionState = (value) => glossed(CONDITION_STATES, value);
export const carryOver = (value) => glossed(CARRY_OVER, value);

// The one refusal whose known-limitations table this slice may show, and only
// for a real run: the condition is the envelope's mode and the refusal code,
// never the project name.
export const BASELINE_REFUSAL_CODE = "team-mapping-decision-basis-illustrative";

export const BASELINE_LIMITATIONS = [
  ["团队映射", "本次实际拒绝，以上方拒绝文本为准"],
  [
    "证据方法",
    "同一示例政策同样拒绝；须先越过前闸门且确实消费判定才会触发，不能标成已检查或通过",
  ],
  [
    "风险授权",
    "同一政策在政策解析层同样拒绝；今天无运行时消费者，E2 尚未实现，不是可通过的下一步",
  ],
];
