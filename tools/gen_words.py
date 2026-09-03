#!/usr/bin/env python3
"""Generate Spelling, Definitions and Synonyms cards for the new word set.

Each entry supplies every field needed by all three decks, keeping the
three card formats consistent with the existing ones.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS = ROOT / "cards"

# word -> (ipa, pos, spelling-tip, spelling-hint, letter-count, def, example,
#          synonyms(list), syn-hint, syn-example)
# letter-count is filled from len(word) if not given (0 -> auto)
WORDS = [
    ("achieve",  "/əˈtʃiːv/",  "verb",      "a-chieve — the common 'ie' after c is the trap", "", 0,
     "To successfully reach a desired aim or result by effort.",
     "She worked hard to achieve her goals.",
     ["attain", "accomplish", "reach", "realize", "fulfil"], "verb",
     "Achieve / attain / reach your goals — all are formal IELTS verbs."),
    ("alternative", "/ɔːlˈtɜː.nə.tɪv/", "adjective/noun", "alt-ern-ative — keep the 'ern' in the middle", "", 0,
     "One of two or more available possibilities; a different option.",
     "We considered an alternative plan.",
     ["option", "choice", "substitute", "other", "fallback"], "noun",
     "Offer an alternative or an option when presenting solutions in an essay."),
    ("analyze", "/ˈæn.əl.aɪz/", "verb", "an-a-lyze — 'a-na-ly-ze', three syllables", "", 0,
     "To examine something in detail in order to understand or explain it.",
     "We analyzed the data carefully.",
     ["examine", "inspect", "study", "evaluate", "investigate"], "verb",
     "Analyze, examine or investigate a problem in your task 2 body."),
    ("apparent", "/əˈpær.ənt/", "adjective", "ap-parent — one p, then 'arent'", "", 0,
     "Clearly visible or understood; obvious.",
     "It became apparent that we were lost.",
     ["obvious", "evident", "clear", "visible", "plain"], "adjective",
     "It was apparent / evident / obvious that costs were rising."),
    ("aspect", "/ˈæs.pekt/", "noun", "a-spect — no 'e' before the final t", "", 0,
     "A particular feature or part of something.",
     "We looked at every aspect of the problem.",
     ["feature", "facet", "side", "dimension", "element"], "noun",
     "Discuss every aspect / facet / dimension of the issue."),
    ("assumption", "/əˈsʌmp.ʃən/", "noun", "as-sump-tion — double s, then 'ump'", "", 0,
     "Something accepted as true without proof.",
     "That was based on a false assumption.",
     ["belief", "supposition", "premise", "hypothesis", "presumption"], "noun",
     "Challenge a common assumption / belief / premise in your essay."),
    ("benefit", "/ˈben.ɪ.fɪt/", "noun/verb", "bene-fit — no double letters", "", 0,
     "An advantage or profit gained from something; to gain from it.",
     "The plan offers clear benefits to everyone.",
     ["advantage", "gain", "profit", "plus", "upside"], "noun",
     "List the benefits / advantages / pluses of a policy."),
    ("comprehensive", "/ˌkɒm.prɪˈhen.sɪv/", "adjective", "com-pre-hen-sive — note the 'hen'", "", 0,
     "Including everything or nearly everything; complete and thorough.",
     "The report gives a comprehensive overview.",
     ["thorough", "complete", "extensive", "full", "all-inclusive"], "adjective",
     "A comprehensive / thorough / extensive study of the topic."),
    ("consequence", "/ˈkɒn.sɪ.kwəns/", "noun", "con-se-quence — the 'ue' before 'nce'", "", 0,
     "A result or effect of an action or condition.",
     "Pollution has serious consequences for health.",
     ["result", "outcome", "effect", "repercussion", "impact"], "noun",
     "Weigh the consequences / repercussions / outcomes of a decision."),
    ("constitute", "/ˈkɒn.stɪ.tjuːt/", "verb", "con-sti-tute — 'sti', not 'stit'", "", 0,
     "To be or form part of something; to make up.",
     "Women constitute the majority of the workforce.",
     ["form", "make up", "comprise", "represent", "account for"], "verb",
     "Students constitute / form / make up a large share of users."),
    ("contemporary", "/kənˈtem.pər.ər.i/", "adjective", "con-tem-por-ary — keep the 'por'", "", 0,
     "Living or occurring at the same time; modern or current.",
     "Contemporary art challenges traditional ideas.",
     ["modern", "current", "present-day", "recent", "up-to-date"], "adjective",
     "Modern / contemporary / present-day society faces new problems."),
    ("contribute", "/kənˈtrɪb.juːt/", "verb", "con-tri-bute — the stressed 'trɪ'", "", 0,
     "To give something (money, effort, ideas) to help achieve something.",
     "Everyone contributed to the discussion.",
     ["donate", "add", "help", "play a part", "chip in"], "verb",
     "Several factors contribute / add to the rising cost."),
    ("controversial", "/ˌkɒn.trəˈvɜː.ʃəl/", "adjective", "con-tro-vers-ial — the 'ro' then 'vers'", "", 0,
     "Causing disagreement or discussion.",
     "The policy proved highly controversial.",
     ["debatable", "disputed", "contentious", "arguable", "divisive"], "adjective",
     "A controversial / contentious / debated topic in the news."),
    ("crucial", "/ˈkruː.ʃəl/", "adjective", "cru-cial — 'cru', then 'cial'", "", 0,
     "Extremely important; critical to the success of something.",
     "Timing is crucial to the project.",
     ["vital", "essential", "critical", "key", "necessary"], "adjective",
     "It is crucial / vital / essential to plan ahead."),
    ("demonstrate", "/ˈdem.ən.streɪt/", "verb", "de-mon-strate — 'mon', then 'strate'", "", 0,
     "To show clearly; to prove by giving evidence or examples.",
     "The study demonstrates a clear link.",
     ["show", "prove", "illustrate", "evidence", "exhibit"], "verb",
     "Demonstrate / show / illustrate a point with examples."),
    ("diminish", "/dɪˈmɪn.ɪʃ/", "verb", "di-min-ish — 'min', then 'ish'", "", 0,
     "To make or become smaller or weaker.",
     "Demand for the product is diminishing.",
     ["decrease", "reduce", "decline", "lessen", "weaken"], "verb",
     "Costs diminish / decline / decrease over time."),
    ("emphasize", "/ˈem.fə.saɪz/", "verb", "em-pha-size — the 'pha' after 'em'", "", 0,
     "To give special importance or attention to something.",
     "The report emphasizes the need for change.",
     ["stress", "highlight", "underline", "accentuate", "spotlight"], "verb",
     "Emphasize / stress / highlight the main point."),
    ("enhance", "/ɪnˈhɑːns/", "verb", "en-hance — the 'h' is part of the word", "", 0,
     "To improve the quality, value or extent of something.",
     "Technology can enhance the learning experience.",
     ["improve", "boost", "strengthen", "augment", "heighten"], "verb",
     "Enhance / boost / improve performance at work."),
    ("essential", "/ɪˈsen.ʃəl/", "adjective", "es-sen-tial — double s, then 'en'", "", 0,
     "Absolutely necessary; extremely important.",
     "Water is essential for life.",
     ["vital", "crucial", "indispensable", "necessary", "required"], "adjective",
     "Essential / vital / indispensable skills for study."),
    ("establish", "/ɪˈstæb.lɪʃ/", "verb", "es-tab-lish — 'tab', then 'lish'", "", 0,
     "To start or set up something lasting; to prove or confirm.",
     "The company was established in 1990.",
     ["set up", "found", "create", "institute", "launch"], "verb",
     "Establish / set up / found an organization."),
    ("evaluate", "/ɪˈvæl.ju.eɪt/", "verb", "e-val-u-ate — 'val', then 'u-ate'", "", 0,
     "To judge or assess the value, quality or importance of something.",
     "We need to evaluate the results carefully.",
     ["assess", "appraise", "judge", "review", "examine"], "verb",
     "Evaluate / assess / judge the evidence."),
    ("evident", "/ˈev.ɪ.dənt/", "adjective", "e-vi-dent — 'vi', then 'dent'", "", 0,
     "Clearly seen or understood; obvious.",
     "It was evident that she was tired.",
     ["obvious", "apparent", "clear", "plain", "noticeable"], "adjective",
     "It was evident / apparent / obvious from the data."),
    ("facilitate", "/fəˈsɪl.ɪ.teɪt/", "verb", "fa-cil-i-tate — 'cil', then 'i-tate'", "", 0,
     "To make an action or process easier.",
     "The new software facilitates communication.",
     ["ease", "enable", "assist", "help", "streamline"], "verb",
     "This facilitates / eases / enables faster decision-making."),
    ("fundamental", "/ˌfʌn.dəˈmen.təl/", "adjective", "fun-da-men-tal — 'da', then 'mental'", "", 0,
     "Forming a necessary base or core; of central importance.",
     "Trust is fundamental to any relationship.",
     ["basic", "essential", "core", "primary", "foundational"], "adjective",
     "A fundamental / basic / core issue to address."),
    ("generate", "/ˈdʒen.ər.eɪt/", "verb", "gen-er-ate — 'er' in the middle", "", 0,
     "To produce or create something, such as energy or ideas.",
     "Solar panels generate electricity.",
     ["produce", "create", "yield", "cause", "give rise to"], "verb",
     "The scheme generates / produces / creates many jobs."),
    ("hypothesis", "/haɪˈpɒθ.ə.sɪs/", "noun", "hy-poth-e-sis — 'poth', then 'e-sis'", "", 0,
     "A proposed explanation based on limited evidence, to be tested.",
     "The results support our hypothesis.",
     ["theory", "premise", "supposition", "assumption", "proposition"], "noun",
     "Test a hypothesis / theory / assumption."),
    ("immediate", "/ɪˈmiː.di.ət/", "adjective", "im-me-di-ate — double m, then 'di'", "", 0,
     "Happening now or without delay; direct and close.",
     "We need an immediate response.",
     ["instant", "prompt", "swift", "direct", "urgent"], "adjective",
     "An immediate / instant / prompt reaction."),
    ("indicate", "/ˈɪn.dɪ.keɪt/", "verb", "in-di-cate — 'di', then 'cate'", "", 0,
     "To point out or show; to be a sign of something.",
     "The results indicate a clear improvement.",
     ["show", "suggest", "signal", "point to", "demonstrate"], "verb",
     "The data indicates / suggests / shows a trend."),
    ("integral", "/ˈɪn.tɪ.ɡrəl/", "adjective", "in-te-gral — 'te', then 'gral'", "", 0,
     "Necessary to make something complete; essential.",
     "Teamwork is integral to the project.",
     ["essential", "vital", "intrinsic", "indispensable", "key"], "adjective",
     "R&D is integral / essential / key to growth."),
    ("interpret", "/ɪnˈtɜː.prɪt/", "verb", "in-ter-pret — 'ter', then 'pret'", "", 0,
     "To explain the meaning of something; to translate.",
     "How should we interpret these findings?",
     ["explain", "read", "decode", "understand", "translate"], "verb",
     "Interpret / read / explain the data carefully."),
    ("investigate", "/ɪnˈves.tɪ.ɡeɪt/", "verb", "in-ves-ti-gate — 'ves', then 'ti-gate'", "", 0,
     "To carry out a systematic inquiry into something.",
     "Police are investigating the incident.",
     ["examine", "probe", "explore", "study", "look into"], "verb",
     "Investigate / examine / probe the causes."),
    ("justify", "/ˈdʒʌs.tɪ.faɪ/", "verb", "just-ify — 'just', then 'ify'", "", 0,
     "To give a good reason for an action or decision.",
     "He tried to justify his decision.",
     ["explain", "defend", "argue", "account for", "rationalize"], "verb",
     "Justify / defend / argue your position."),
    ("maintain", "/meɪnˈteɪn/", "verb", "main-tain — the 'ai' and 'ai'", "", 0,
     "To keep something in a particular state; to continue or preserve.",
     "We must maintain high standards.",
     ["keep", "preserve", "uphold", "sustain", "retain"], "verb",
     "Maintain / sustain / preserve the current level."),
    ("negotiate", "/nɪˈɡəʊ.ʃi.eɪt/", "verb", "ne-go-ti-ate — 'go', then 'ti-ate'", "", 0,
     "To discuss something formally to reach an agreement.",
     "They negotiated a new contract.",
     ["bargain", "discuss", "arrange", "mediate", "settle"], "verb",
     "Negotiate / bargain / settle a deal."),
    ("notion", "/ˈnəʊ.ʃən/", "noun", "no-tion — 'no', then 'tion'", "", 0,
     "An idea or belief about something.",
     "She rejected the notion that change is easy.",
     ["idea", "concept", "belief", "impression", "view"], "noun",
     "Challenge the notion / idea / concept that..." ),
    ("objective", "/əbˈdʒek.tɪv/", "noun/adjective", "ob-jec-tive — 'ject', then 'ive'", "", 0,
     "A goal or aim; also, based on facts rather than feelings.",
     "Our main objective is to cut costs.",
     ["goal", "aim", "target", "purpose", "intention"], "noun",
     "Set a clear objective / goal / target."),
    ("prioritize", "/praɪˈɒr.ɪ.taɪz/", "verb", "pri-or-i-tize — 'or', then 'i-tize'", "", 0,
     "To treat something as more important than others.",
     "We must prioritize safety.",
     ["rank", "favour", "emphasize", "put first", "prefer"], "verb",
     "Prioritize / rank / put first the key tasks."),
    ("pursue", "/pəˈsjuː/", "verb", "pur-sue — the 'ue' at the end", "", 0,
     "To follow or chase; to aim to achieve something.",
     "She decided to pursue a career in science.",
     ["chase", "seek", "follow", "strive for", "aim for"], "verb",
     "Pursue / seek / strive for excellence."),
    ("quarantine", "/ˈkwɒr.ən.tiːn/", "noun/verb", "quar-an-tine — 'quar', then 'an-tine'", "", 0,
     "A period of isolation to prevent the spread of disease.",
     "The patient was placed in quarantine.",
     ["isolation", "seclusion", "lockdown", "detention", "confinement"], "noun",
     "A period of quarantine / isolation / lockdown."),
    ("recommend", "/ˌrek.əˈmend/", "verb", "rec-om-mend — double m at the end", "", 0,
     "To suggest something as suitable or good.",
     "I recommend trying the local food.",
     ["suggest", "advise", "propose", "counsel", "endorse"], "verb",
     "Recommend / suggest / advise a change."),
    ("regulate", "/ˈreɡ.jʊ.leɪt/", "verb", "reg-u-late — 'reg', then 'u-late'", "", 0,
     "To control or maintain something by rules or laws.",
     "The government regulates the market.",
     ["control", "govern", "monitor", "manage", "oversee"], "verb",
     "Regulate / control / govern the sector."),
    ("relevant", "/ˈrel.ə.vənt/", "adjective", "rel-e-vant — 'e-va', keep all vowels", "", 0,
     "Closely connected to the matter at hand; applicable.",
     "Please share all relevant information.",
     ["pertinent", "applicable", "related", "germane", "apt"], "adjective",
     "Include all relevant / pertinent / applicable details."),
    ("research", "/rɪˈsɜːtʃ/", "noun/verb", "re-search — the prefix re-", "", 0,
     "Systematic investigation to discover or establish facts.",
     "She is doing research on climate change.",
     ["study", "inquiry", "investigation", "analysis", "exploration"], "noun",
     "Conduct research / a study / an inquiry."),
    ("strategy", "/ˈstræt.ə.dʒi/", "noun", "strat-egy — 'at', then 'egy'", "", 0,
     "A plan of action designed to achieve a long-term goal.",
     "We agreed on a new strategy.",
     ["plan", "approach", "tactic", "scheme", "method"], "noun",
     "Develop a strategy / plan / approach."),
    ("sufficient", "/səˈfɪʃ.ənt/", "adjective", "suf-fi-cient — double f, then 'icient'", "", 0,
     "Enough; adequate for a purpose.",
     "We have sufficient funds to proceed.",
     ["enough", "adequate", "ample", "plenty", "satisfactory"], "adjective",
     "Provide sufficient / enough / adequate evidence."),
    ("transform", "/trænsˈfɔːm/", "verb", "trans-form — the prefix 'trans'", "", 0,
     "To change something completely, usually for the better.",
     "Technology has transformed the industry.",
     ["change", "convert", "alter", "renovate", "reshape"], "verb",
     "Technology has transformed / reshaped / revolutionised work."),
    ("transmit", "/trænzˈmɪt/", "verb", "trans-mit — the prefix 'trans', double t at end", "", 0,
     "To send or pass on something from one place or person to another.",
     "The signal is transmitted over long distances.",
     ["send", "pass on", "convey", "transfer", "broadcast"], "verb",
     "Transmit / convey / pass on information."),
    ("vast", "/vɑːst/", "adjective", "vast — short word, one 'a'", "", 0,
     "Of very great extent or size; immense.",
     "The desert is a vast area.",
     ["huge", "immense", "enormous", "extensive", "massive"], "adjective",
     "A vast / huge / immense amount of data."),
    ("widespread", "/ˈwaɪd.spred/", "adjective", "wide-spread — two words joined", "", 0,
     "Existing or happening over a large area or among many people.",
     "There is widespread support for the plan.",
     ["prevalent", "common", "extensive", "universal", "rampant"], "adjective",
     "Widespread / prevalent / common concern."),
    ("limited", "/ˈlɪm.ɪ.tɪd/", "adjective", "lim-it-ed — 'lim', then 'it-ed'", "", 0,
     "Small in amount, number or extent; restricted.",
     "Resources are limited this year.",
     ["restricted", "narrow", "scarce", "finite", "constrained"], "adjective",
     "Limited / scarce / narrow resources."),
    ("accurate", "/ˈæk.jər.ət/", "adjective", "ac-cu-rate — double c, then 'cu-rate'", "", 0,
     "Correct in all details; exact and free from error.",
     "The figures were accurate.",
     ["exact", "precise", "correct", "faithful", "true"], "adjective",
     "An accurate / precise / exact measurement."),
    ("liability", "/ˌlaɪ.əˈbɪl.ə.ti/", "noun", "li-a-bil-ity — 'a-bil', then 'ity'", "", 0,
     "Legal or financial responsibility for something; a debt or a disadvantage.",
     "The company faces huge liabilities from the lawsuit.",
     ["responsibility", "obligation", "debt", "burden", "accountability"], "noun",
     "A company must disclose its liabilities / debts / obligations."),
    ("severance", "/ˈsev.ər.əns/", "noun", "sev-er-ance — 'er', then 'ance'", "", 0,
     "The ending of a contract or employment; compensation paid on dismissal.",
     "He received a large severance package.",
     ["termination", "dismissal", "redundancy", "separation", "compensation"], "noun",
     "Discuss severance / redundancy / termination pay in corporate contexts."),
    ("intricate", "/ˈɪn.trɪ.kət/", "adjective", "in-tri-cate — 'tri', then 'cate'", "", 0,
     "Very complicated or detailed; made up of many interconnected parts.",
     "The watch has an intricate mechanism.",
     ["complex", "elaborate", "complicated", "detailed", "convoluted"], "adjective",
     "An intricate / elaborate / complex design."),
    ("intact", "/ɪnˈtækt/", "adjective", "in-tact — the 'tac' in the middle", "", 0,
     "Not damaged, broken or altered; complete and whole.",
     "Despite the crash, the cargo survived intact.",
     ["whole", "undamaged", "complete", "unbroken", "pristine"], "adjective",
     "The evidence must remain intact / whole / undamaged."),
    ("imminent", "/ˈɪm.ɪ.nənt/", "adjective", "im-mi-nent — double m, then 'inent'", "", 0,
     "About to happen very soon; impending.",
     "The company warned of imminent job losses.",
     ["impending", "approaching", "looming", "forthcoming", "near"], "adjective",
     "Warn of imminent / impending / looming changes."),
    ("plausible", "/ˈplɔː.zə.bəl/", "adjective", "plau-si-ble — 'plau', then 'sible'", "", 0,
     "Seeming reasonable or likely to be true.",
     "She offered a plausible explanation.",
     ["credible", "believable", "reasonable", "convincing", "likely"], "adjective",
     "A plausible / credible / convincing explanation."),
    ("obsolete", "/ˈɒb.sə.liːt/", "adjective", "ob-so-lete — 'so', then 'lete'", "", 0,
     "No longer used or needed; out of date.",
     "Many skills have become obsolete.",
     ["outdated", "outmoded", "antiquated", "archaic", "superseded"], "adjective",
     "Outdated / obsolete / antiquated technology."),
    ("meticulous", "/məˈtɪk.jə.ləs/", "adjective", "me-tic-u-lous — 'tic', then 'u-lous'", "", 0,
     "Extremely careful and precise about details.",
     "He kept meticulous records of the project.",
     ["careful", "thorough", "precise", "painstaking", "scrupulous"], "adjective",
     "A meticulous / thorough / scrupulous examination."),
    ("empirical", "/ɪmˈpɪr.ɪ.kəl/", "adjective", "em-pir-i-cal — the 'pir' in the middle", "", 0,
     "Based on evidence, observation or experience rather than theory.",
     "The theory lacks empirical support.",
     ["evidence-based", "observed", "experimental", "practical", "factual"], "adjective",
     "Back a claim with empirical / observed / factual evidence."),
    ("consensus", "/kənˈsen.səs/", "noun", "con-sen-sus — 'sen', then 'sus'", "", 0,
     "A general agreement among a group of people.",
     "The committee reached a consensus.",
     ["agreement", "accord", "unanimity", "consent", "harmony"], "noun",
     "Reach a consensus / agreement / accord."),
    ("disparity", "/dɪˈspær.ə.ti/", "noun", "dis-par-ity — 'par', then 'ity'", "", 0,
     "A great difference or inequality between things.",
     "There is a wide disparity in income.",
     ["inequality", "gap", "difference", "imbalance", "discrepancy"], "noun",
     "Highlight the disparity / gap / imbalance between groups."),
    ("arbitrary", "/ˈɑː.bɪ.trər.i/", "adjective", "ar-bi-trary — 'bi', then 'trary'", "", 0,
     "Based on random choice rather than reason or system.",
     "The decision seemed completely arbitrary.",
     ["random", "capricious", "whimsical", "unreasonable", "subjective"], "adjective",
     "An arbitrary / random / capricious decision."),
    ("eloquent", "/ˈel.ə.kwənt/", "adjective", "el-o-quent — 'o', then 'quent'", "", 0,
     "Fluent, forceful and persuasive in speaking or writing.",
     "She gave an eloquent speech.",
     ["articulate", "expressive", "persuasive", "fluent", "forceful"], "adjective",
     "An eloquent / articulate / persuasive argument."),
    ("futile", "/ˈfjuː.taɪl/", "adjective", "fu-tile — 'tile' at the end", "", 0,
     "Pointless or useless; incapable of producing a result.",
     "Further negotiation proved futile.",
     ["pointless", "useless", "vain", "hopeless", "ineffective"], "adjective",
     "A futile / pointless / vain attempt."),
    ("implicit", "/ɪmˈplɪs.ɪt/", "adjective", "im-pli-cit — 'pli', then 'cit'", "", 0,
     "Suggested or understood without being stated directly.",
     "There is an implicit assumption in the argument.",
     ["implied", "unspoken", "inherent", "understood", "tacit"], "adjective",
     "An implicit / implied / unspoken agreement."),
    ("ambiguous", "/æmˈbɪɡ.ju.əs/", "adjective", "am-bi-gu-ous — 'igu', then 'ous'", "", 0,
     "Open to more than one interpretation; unclear in meaning.",
     "The wording was highly ambiguous.",
     ["unclear", "vague", "equivocal", "uncertain", "indistinct"], "adjective",
     "Ambiguous / vague / unclear instructions."),
    ("formidable", "/fəˈmɪd.ə.bəl/", "adjective", "for-mi-da-ble — 'mid', then 'able'", "", 0,
     "Inspiring respect or fear through size, strength or ability; difficult to deal with.",
     "They face a formidable challenge.",
     ["intimidating", "daunting", "awe-inspiring", "imposing", "challenging"], "adjective",
     "A formidable / daunting / imposing obstacle."),
    ("holistic", "/həʊˈlɪs.tɪk/", "adjective", "ho-lis-tic — 'lis', then 'tic'", "", 0,
     "Considering the whole of something rather than just its parts.",
     "We need a holistic approach to health.",
     ["whole", "comprehensive", "integrated", "all-round", "overall"], "adjective",
     "A holistic / integrated / comprehensive approach."),
    ("imperative", "/ɪmˈper.ə.tɪv/", "adjective/noun", "im-per-a-tive — 'per', then 'a-tive'", "", 0,
     "Absolutely necessary; vitally important.",
     "It is imperative that we act now.",
     ["essential", "vital", "crucial", "mandatory", "required"], "adjective",
     "It is imperative / essential / crucial to respond."),
    ("impartial", "/ɪmˈpɑː.ʃəl/", "adjective", "im-par-tial — 'par', then 'tial'", "", 0,
     "Fair and neutral; not favouring one side.",
     "The judge must remain impartial.",
     ["neutral", "unbiased", "objective", "fair", "even-handed"], "adjective",
     "An impartial / unbiased / objective assessment."),
]


def hint(word, pos, extra=""):
    return f"{len(word)} letters &middot; starts with <b>{word[0].upper()}</b> &middot; {pos}"


def make_def(w):
    wid, ipa, pos, tip, _, _lc, definition, example, *_ = w
    return f"""---
id: {wid}
dependencies: []
---

# Front

<div class="w">{wid}</div>
<div class="phon">{ipa}</div>

---

# Back

<div class="pos">{pos}</div>

<p>{definition}</p>

<span class="ex">{example}</span>
"""


def make_spell(w):
    wid, ipa, pos, tip, hinttext, _lc, definition, example, *_ = w
    h = hinttext if hinttext else hint(wid, pos)
    return f"""---
id: {wid}
dependencies: []
---

# Front

<span class="def">{definition}</span>

<div class="hint">{h}</div>

---

# Type

{wid}

---

# Back

<div class="w">{wid}</div>
<div class="phon">{ipa}</div>
<div class="pos">{pos}</div>

<p>Spelling tip: {tip}.</p>

<span class="ex">{example}</span>
"""


def make_syn(w):
    wid, ipa, pos, tip, hinttext, _lc, definition, example, syns, synpos, synex = w
    ans = ", ".join(syns)
    display = " &middot; ".join(f"<b>{s}</b>" for s in syns)
    return f"""---
id: syn-{wid}
dependencies: []
---

# Front

<div class="w">{wid} <span class="pos">{synpos}</span></div>

<div class="hint">Type one or more <b>{synpos}</b> synonyms — any accepted answer counts.</div>

---

# Type

{ans}

---

# Back

<div class="pos">{synpos}</div>

<p>{display}</p>

<span class="ex">{synex}</span>
"""


def main():
    for w in WORDS:
        wid = w[0]
        (CARDS / "Definitions").mkdir(parents=True, exist_ok=True)
        (CARDS / "Spelling").mkdir(parents=True, exist_ok=True)
        (CARDS / "Synonyms").mkdir(parents=True, exist_ok=True)
        (CARDS / "Definitions" / f"{wid}.md").write_text(make_def(w))
        (CARDS / "Spelling" / f"{wid}.md").write_text(make_spell(w))
        (CARDS / "Synonyms" / f"syn-{wid}.md").write_text(make_syn(w))
    print(f"Generated cards for {len(WORDS)} words")
    print("Definitions:", len(WORDS), "| Spelling:", len(WORDS), "| Synonyms:", len(WORDS))


if __name__ == "__main__":
    main()
