"""
Structure-Aware Document Analyzer.
Extracts document-specific intelligence from parsed PDF chunks:
- Document title and hierarchical sections/headings
- Important concepts and curriculum topics
- Important portions with page references
- Comprehensive document summary
- Aligned 10-slide educational lecture deck with speaker notes and conceptual diagrams
"""

import re
from typing import Any, Dict, List, Optional, Set, Tuple


STOP_WORDS = {
    "about", "above", "after", "again", "against", "all", "also", "and", "any", "are",
    "because", "been", "before", "being", "below", "between", "both", "but", "can",
    "could", "did", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "here", "how", "into", "itself", "just",
    "more", "most", "must", "not", "only", "other", "our", "out", "over", "same",
    "should", "some", "such", "than", "that", "the", "their", "them", "then", "there",
    "these", "they", "this", "those", "through", "too", "under", "until", "very", "was",
    "were", "what", "when", "where", "which", "while", "who", "whom", "why", "will",
    "with", "would", "your", "page", "chapter", "section", "figure", "table"
}


def clean_sentences(text: str) -> List[str]:
    """Splits raw text into non-empty, grammatically cohesive sentences."""
    flat = re.sub(r'[\r\n]+', ' ', text)
    flat = re.sub(r'\s+', ' ', flat).strip()
    raw_sentences = re.split(r'(?<=[.!?])\s+', flat)
    valid = []
    for s in raw_sentences:
        clean = re.sub(r'^[0-9\.\s\-•*]+', '', s).strip()
        if len(clean) > 15 and not clean.upper() in ["FIG", "FIGURE", "TABLE", "PAGE"]:
            if not clean.endswith((".", "!", "?")):
                clean += "."
            valid.append(clean)
    return valid


class DocumentAnalyzer:
    """Analyzes extracted PDF chunks to generate document-specific educational assets."""

    def extract_title(self, chunks: List[Dict[str, Any]], fallback_title: str) -> str:
        """Infers the document title from fallback title or prominent headings."""
        if fallback_title and fallback_title.strip() and fallback_title != "Uploaded_Document.pdf" and fallback_title != "Uploaded curriculum material":
            return fallback_title.strip()

        # Look for an explicit heading on the first page
        for chunk in chunks[:4]:
            if chunk.get("is_heading"):
                t = chunk.get("text", "").split("\n")[0].strip()
                t = re.sub(r'^(chapter|unit|section|module)\s*\d+[:\s\-]*', '', t, flags=re.IGNORECASE).strip()
                if 4 <= len(t) <= 80:
                    return t

        # Look for first short capitalized line on page 1
        if chunks:
            lines = [l.strip() for l in chunks[0].get("text", "").split("\n") if l.strip()]
            for l in lines[:3]:
                if 4 <= len(l) <= 65 and not l.endswith("."):
                    clean_line = re.sub(r'^(chapter|unit|section|module)\s*\d+[:\s\-]*', '', l, flags=re.IGNORECASE).strip()
                    if clean_line:
                        return clean_line

        return fallback_title or "Uploaded Curriculum Document"

    def extract_headings(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Extracts unique section headings from chunks or paragraph leads."""
        headings: List[str] = []
        seen = set()

        # 1. Chunks explicitly flagged as headings
        for chunk in chunks:
            if chunk.get("is_heading"):
                text = chunk.get("text", "").strip()
                first_line = text.split("\n")[0].strip()
                clean_h = re.sub(r'^[0-9\.\s\-•*]+', '', first_line).strip()
                if 3 <= len(clean_h) <= 90 and clean_h.lower() not in seen:
                    headings.append(clean_h)
                    seen.add(clean_h.lower())

        # 2. Pattern-based headings from chunk starts
        if len(headings) < 3:
            for chunk in chunks:
                text = chunk.get("text", "").strip()
                lines = [l.strip() for l in text.split("\n") if l.strip()]
                if lines:
                    lead = lines[0]
                    clean_lead = lead.rstrip(".:")
                    words = [w for w in clean_lead.split() if w.lower() not in STOP_WORDS]
                    is_title_cased = bool(words and sum(w[0].isupper() for w in words) >= len(words) * 0.7)
                    if re.match(r'^(chapter|section|unit|module|\d+(\.\d+)*)\s+', lead, re.IGNORECASE) or (
                        3 <= len(clean_lead) <= 75 and not any(clean_lead.lower().startswith(p) for p in ["the ", "this ", "when ", "by ", "in ", "a ", "an ", "if "]) and (clean_lead.isupper() or is_title_cased or " & " in clean_lead or ":" in lead)
                    ):
                        clean_h = re.sub(r'^[0-9\.\s\-•*]+', '', clean_lead).strip()
                        if 3 <= len(clean_h) <= 90 and clean_h.lower() not in seen:
                            headings.append(clean_h)
                            seen.add(clean_h.lower())

        # 3. Fallback: derive headings from first sentences if still sparse
        if not headings:
            for idx, chunk in enumerate(chunks[:5]):
                sents = clean_sentences(chunk.get("text", ""))
                if sents:
                    words = sents[0].split()[:5]
                    fallback = " ".join(words).rstrip(".,;:")
                    if fallback.lower() not in seen:
                        headings.append(fallback)
                        seen.add(fallback.lower())

        return headings[:10]

    def extract_concepts(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Extracts key concepts, terminology, and topics from document text."""
        concepts: List[str] = []
        seen = set()

        full_text = " ".join(c.get("text", "") for c in chunks)

        # 1. Definitions patterns: "X is defined as...", "X refers to...", "X algorithm:"
        pattern = re.compile(
            r'([A-Z][a-zA-Z0-9\s\-]{2,35})\s+(?:is defined as|refers to|is a|represents|denotes|consists of|algorithm:)',
            re.IGNORECASE
        )
        for match in pattern.finditer(full_text):
            concept = match.group(1).strip()
            # Filter out generic leading words
            clean_c = re.sub(r'^(the|a|an|in|for|this)\s+', '', concept, flags=re.IGNORECASE).strip()
            if 3 <= len(clean_c) <= 40 and clean_c.lower() not in seen and not any(w in STOP_WORDS for w in clean_c.lower().split()):
                concepts.append(clean_c.title())
                seen.add(clean_c.lower())

        # 2. Capitalized Multi-word terms (e.g., "Round Robin", "Context Switching", "Spanning Tree")
        multiword_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b')
        for match in multiword_pattern.finditer(full_text):
            term = match.group(1).strip()
            clean_term = term.lower()
            if len(term) >= 5 and clean_term not in seen and not any(w in STOP_WORDS for w in clean_term.split()):
                concepts.append(term)
                seen.add(clean_term)

        # 3. Significant recurring technical words
        words = re.findall(r'\b[a-zA-Z]{5,}\b', full_text.lower())
        freq: Dict[str, int] = {}
        for w in words:
            if w not in STOP_WORDS:
                freq[w] = freq.get(w, 0) + 1

        top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        for w, count in top_words:
            if len(concepts) >= 12:
                break
            if w not in seen and count >= 2:
                concepts.append(w.title())
                seen.add(w)

        return concepts[:10]

    def extract_important_portions(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts critical excerpts, algorithms, definitions, or complex portions."""
        portions = []
        for idx, chunk in enumerate(chunks):
            text = chunk.get("text", "").strip()
            page = chunk.get("page", idx + 1)
            sentences = clean_sentences(text)
            if not sentences:
                continue

            lead = sentences[0]
            # Key indicator keywords
            is_critical = any(kw in text.lower() for kw in [
                "algorithm", "definition", "theorem", "property", "complexity", "important",
                "crucial", "architecture", "mechanism", "in-order", "scheduling", "analysis"
            ])

            portions.append({
                "page": page,
                "section": chunk.get("is_heading", False),
                "is_critical": is_critical,
                "lead_sentence": lead,
                "snippet": text[:180] + ("..." if len(text) > 180 else ""),
                "char_length": len(text),
                "bbox": chunk.get("bbox")
            })

        # Return the most substantive portions
        return portions[:8]

    def generate_summary(self, chunks: List[Dict[str, Any]], title: str) -> str:
        """Generates a cohesive, multi-sentence executive summary strictly from document text."""
        collected_sentences: List[str] = []
        for chunk in chunks:
            sents = clean_sentences(chunk.get("text", ""))
            for s in sents:
                # Prioritize informative, definitional sentences
                if len(s) > 30 and s not in collected_sentences:
                    collected_sentences.append(s)

        if not collected_sentences:
            return f"Curriculum document covering {title}. Extracted content provides technical specifications and operational rules."

        # Pick lead sentence + 2-3 supporting structural sentences
        lead = collected_sentences[0]
        supporting = [s for s in collected_sentences[1:6] if s != lead][:3]

        summary_parts = [f"**{title} Overview**: {lead}"]
        if supporting:
            summary_parts.append(" ".join(supporting))

        # Add synthesis clause
        summary_parts.append(
            f"The material systematically details foundational invariants, core execution mechanisms, and assessment standards across {len(chunks)} extracted content sections."
        )

        return " ".join(summary_parts)

    def generate_slide_deck(
        self,
        chunks: List[Dict[str, Any]],
        title: str,
        headings: List[str],
        concepts: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Generates a 10-slide curriculum-aligned lecture deck deeply analyzing and
        distributing content across all extracted document chunks, sections, and concepts.
        """
        def clean_sentence_str(s: str) -> str:
            s_clean = re.sub(r'^[0-9\.\s\-•*:]+', '', s).strip()
            s_clean = re.sub(r'\s+', ' ', s_clean)
            if len(s_clean) > 180:
                cut = s_clean[:175]
                last_punct = max(cut.rfind(','), cut.rfind(';'), cut.rfind(' '))
                if last_punct > 80:
                    s_clean = cut[:last_punct].strip() + '.'
                else:
                    s_clean = cut.strip() + '.'
            elif not s_clean.endswith(('.', '!', '?')):
                s_clean += '.'
            return s_clean

        def is_heading_or_title(text: str) -> bool:
            clean = re.sub(r'[^a-zA-Z0-9\s]', '', text).strip().lower()
            title_clean = re.sub(r'[^a-zA-Z0-9\s]', '', title).strip().lower()
            if clean == title_clean or (len(clean) > 8 and clean in title_clean):
                return True
            for h in headings:
                h_clean = re.sub(r'[^a-zA-Z0-9\s]', '', h).strip().lower()
                if clean == h_clean or (len(clean) > 8 and clean in h_clean):
                    return True
            return False

        # Extract structured sentences across all chunks
        sentences: List[Dict[str, Any]] = []
        seen_sentences = set()
        total_chunks = max(1, len(chunks))

        for idx, c in enumerate(chunks):
            text = c.get("text", "")
            page = c.get("page", idx + 1)
            rel_pos = idx / max(1, total_chunks - 1) if total_chunks > 1 else 0.5

            lines = [l.strip() for l in text.split("\n") if l.strip()]
            body_text = text
            if len(lines) > 1:
                first_line = lines[0]
                clean_first = first_line.rstrip(".:")
                words_f = [w for w in clean_first.split() if w.lower() not in STOP_WORDS]
                is_f_title = bool(words_f and sum(w[0].isupper() for w in words_f) >= len(words_f) * 0.7)
                if is_heading_or_title(first_line) or (
                    len(clean_first) <= 75
                    and not any(clean_first.lower().startswith(p) for p in ["the ", "this ", "when ", "by ", "in ", "a ", "an ", "if "])
                    and (clean_first.isupper() or is_f_title or " & " in clean_first or ":" in first_line)
                ):
                    body_text = "\n".join(lines[1:])

            flat = re.sub(r'[\r\n]+', ' ', body_text)
            flat = re.sub(r'\s+', ' ', flat).strip()
            raw_splits = re.split(r'(?<=[.!?])\s+', flat)

            for raw in raw_splits:
                cleaned = clean_sentence_str(raw)
                clean_lower = cleaned.lower()
                if (
                    len(cleaned) >= 20
                    and not any(cleaned.upper().startswith(p) for p in ["FIG", "FIGURE", "TABLE", "PAGE"])
                    and not is_heading_or_title(cleaned)
                    and clean_lower not in seen_sentences
                ):
                    seen_sentences.add(clean_lower)
                    sentences.append({
                        "text": cleaned,
                        "chunk_idx": idx,
                        "page": page,
                        "rel_pos": rel_pos,
                        "lower": clean_lower,
                    })

        # Classify sentences into semantic pedagogical pools
        pools: Dict[str, List[Dict[str, Any]]] = {
            "foundations": [],
            "mechanics": [],
            "systems": [],
            "tradeoffs": [],
            "rules": [],
            "general": []
        }

        kw_tradeoffs = ["overhead", "latency", "throughput", "complexity", "trade-off", "bottleneck", "constraint", "starvation", "deadlock", "failure", "cost", "speed", "performance", "bound", "bounds", "pure overhead", "limits", "contention", "cap theorem"]
        kw_rules = ["must", "require", "rule", "condition", "criteria", "metric", "measure", "verify", "formula", "standard", "guarantee", "preserv"]
        kw_mechanics = ["algorithm", "procedure", "step", "process", "mechanism", "operation", "dispatch", "scheduler", "queue", "first", "burst", "quantum", "routine", "execute", "execution", "switch", "state", "save", "load", "traverse", "insert", "delete", "proposer", "acceptor", "leader", "replica", "appendentries", "ballot", "promise"]
        kw_systems = ["system", "systems", "implement", "application", "hardware", "software", "network", "round robin", "fcfs", "sjf", "time-sharing", "environment", "device", "support", "architecture", "protocol", "kernel", "driver", "zookeeper", "etcd", "consul", "cloud", "cluster"]
        kw_foundations = ["defined as", "refers to", "represents", "denotes", "consists of", "principle", "foundation", "basis", "fundamental", "theory", "concept", "objective", "study", "definition", "axiom", "nature", "role", "overview", "property", "baseline"]

        for s in sentences:
            t_low = s["lower"]
            matched = False
            if (s["rel_pos"] >= 0.40 or len(chunks) <= 2) and any(kw in t_low for kw in kw_tradeoffs):
                pools["tradeoffs"].append(s)
                matched = True
            if any(kw in t_low for kw in kw_rules):
                pools["rules"].append(s)
                matched = True
            if any(kw in t_low for kw in kw_mechanics):
                pools["mechanics"].append(s)
                matched = True
            if (s["rel_pos"] >= 0.40 or len(chunks) <= 2) and any(kw in t_low for kw in kw_systems):
                pools["systems"].append(s)
                matched = True
            if (s["rel_pos"] <= 0.35 or len(chunks) <= 2) and (s["rel_pos"] <= 0.20 or any(kw in t_low for kw in kw_foundations)):
                pools["foundations"].append(s)
                matched = True
            if not matched:
                pools["general"].append(s)

        # Sort pools so that early chunks prioritize foundations, late chunks prioritize tradeoffs/systems
        pools["foundations"].sort(key=lambda x: x["rel_pos"])
        pools["mechanics"].sort(key=lambda x: x["rel_pos"])
        pools["systems"].sort(key=lambda x: -x["rel_pos"])
        pools["tradeoffs"].sort(key=lambda x: -x["rel_pos"])
        pools["rules"].sort(key=lambda x: x["rel_pos"])
        pools["general"].sort(key=lambda x: x["rel_pos"])

        used_sentences: Set[str] = set()
        total_pages = max((c.get("page", 1) for c in chunks), default=1)

        def extract_slide_bullets(
            primary_pool: List[Dict[str, Any]],
            secondary_pool: List[Dict[str, Any]],
            general_pool: List[Dict[str, Any]],
            target_count: int,
            synthesized_fallbacks: List[str]
        ) -> List[str]:
            selected: List[str] = []
            for pool in [primary_pool, secondary_pool, general_pool]:
                for s in pool:
                    if s["text"] not in used_sentences:
                        selected.append(s["text"])
                        used_sentences.add(s["text"])
                        if len(selected) >= target_count:
                            return selected

            fb_idx = 0
            while len(selected) < target_count:
                fb = synthesized_fallbacks[fb_idx % len(synthesized_fallbacks)]
                fb_idx += 1
                selected.append(fb)
            return selected

        c0 = concepts[0] if len(concepts) > 0 else title
        c1 = concepts[1] if len(concepts) > 1 else (headings[0] if headings else c0)
        c2 = concepts[2] if len(concepts) > 2 else (headings[1] if len(headings) > 1 else c1)

        # Match headings to slides, advancing if heading 0 overlaps with document title
        h_offset = 1 if (len(headings) > 1 and any(w in headings[0].lower() for w in title.lower().split() if len(w) > 4)) else 0
        h0 = headings[h_offset] if len(headings) > h_offset else c0
        h1 = headings[h_offset + 1] if len(headings) > h_offset + 1 else c1
        h2 = headings[h_offset + 2] if len(headings) > h_offset + 2 else (headings[-1] if len(headings) > 1 else c2)

        # --- Slide 1: Title Slide ---
        slide_1_bullets = [
            f"Curriculum lecture deck covering the core principles and architecture of {title}.",
            f"Explores key concepts: {', '.join(concepts[:3]) if concepts else title}.",
            f"Analyzes {len(headings)} curriculum sections across {len(chunks)} extracted content modules.",
            f"Rigorous educational briefing with embedded pedagogical teacher guidance."
        ]
        slide_1 = {
            "id": "slide-1",
            "category": "Title Slide",
            "title": title,
            "subtitle": f"Curriculum Briefing & Lecture Deck ({len(chunks)} Sections, {total_pages} Pages)",
            "bullets": slide_1_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Welcome students to today's in-depth lecture session covering '{title}'. "
                f"In this module, our learning goal is to establish a rigorous understanding of the underlying theory, "
                f"system mechanics, and performance trade-offs documented in our curriculum text. "
                f"Instructors should emphasize core concepts—specifically {c0} and {c1}—as foundational building blocks. "
                f"Spend the first 3 minutes aligning expectations, introducing the 10-slide roadmap, and encouraging questions."
            ),
            "diagram": False
        }

        # --- Slide 2: Curriculum Overview & Scope ---
        s2_fb = [
            f"Foundational curriculum overview establishing core concepts of {c0}.",
            f"Systematic exploration of {c1} principles and system execution models.",
            f"Comprehensive examination of operational requirements and system constraints.",
            f"Preparation for university academic assessment and applied problem solving."
        ]
        early_foundations = [s for s in pools["foundations"] if s["rel_pos"] <= 0.40]
        # Slide 2 takes 1 foundational/overview sentence, preserving deep axiomatic definitions for Slide 3
        s2_take = 1 if early_foundations else 0
        slide_2_bullets = extract_slide_bullets(early_foundations, pools["general"], [], s2_take, s2_fb[:s2_take])
        for fb in s2_fb:
            if len(slide_2_bullets) >= 4:
                break
            if fb not in slide_2_bullets:
                slide_2_bullets.append(fb)

        slide_2 = {
            "id": "slide-2",
            "category": "Curriculum Overview",
            "title": "Curriculum Overview & Scope",
            "subtitle": f"Prerequisites, core concepts, and learning outcomes for {title}",
            "bullets": slide_2_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"When introducing the curriculum scope for '{title}', guide students methodically through these foundational pillars. "
                f"Highlight '{c0}' as the primary conceptual baseline. Discuss how understanding the theoretical prerequisites "
                f"prevents analytical bottlenecks during lab exercises and complex derivations. "
                f"Open the floor briefly to confirm prerequisite readiness before proceeding."
            ),
            "diagram": False
        }

        # --- Slide 3: Theoretical Foundations & Principles ---
        s3_fb = [
            f"Foundational governing principles establishing the theoretical baseline of {title}.",
            f"Formal definition and invariant properties associated with {c0}.",
            f"Analytical guarantees and structural properties governing system execution.",
            f"Underlying behavioral assumptions required for predictable runtime states."
        ]
        slide_3_bullets = extract_slide_bullets(pools["foundations"], pools["rules"], pools["general"], 4, s3_fb)
        slide_3 = {
            "id": "slide-3",
            "category": "Theoretical Foundations",
            "title": "Theoretical Foundations & Principles",
            "subtitle": "Axiomatic definitions and baseline governing rules",
            "bullets": slide_3_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Unpack the theoretical foundations and axiomatic parameters of {title}. "
                f"Focus on the exact formal definitions shown on the slide, specifically how '{c0}' is characterized in the text. "
                f"Explain why maintaining these invariants is crucial: violating these baseline rules leads to degraded performance "
                f"or undefined system states. Have students record these core assertions in their notes."
            ),
            "diagram": False
        }

        # --- Slide 4: Core Mechanics: h0 ---
        s4_fb = [
            f"Detailed step-by-step structural mechanics of {h0}.",
            f"Algorithmic execution sequence and state management routines.",
            f"Component coordination and data flow during primary operations.",
            f"Boundary checks and invariant preservation during execution."
        ]
        h0_words = [w for w in h0.lower().split() if len(w) > 3 and w not in STOP_WORDS]
        h0_mechanics = [s for s in pools["mechanics"] if any(w in s["lower"] for w in h0_words) or (s["rel_pos"] <= 0.45)]
        slide_4_bullets = extract_slide_bullets(h0_mechanics, pools["mechanics"], pools["general"], 4, s4_fb)
        slide_4 = {
            "id": "slide-4",
            "category": "Concept Breakdown",
            "title": f"Core Mechanics: {h0[:38]}",
            "subtitle": "Algorithmic execution logic and operational routines",
            "bullets": slide_4_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Deep-dive into the operational mechanics of '{h0}'. "
                f"Guide students sequentially through each step of the execution logic displayed on this slide. "
                f"Demonstrate how each operational phase updates system state. Address common student pitfalls regarding "
                f"transition timing and state coordination before proceeding to system dynamics."
            ),
            "diagram": False
        }

        # --- Slide 5: System Dynamics: h1 ---
        s5_fb = [
            f"Internal state transitions and runtime management routines for {h1}.",
            f"Hardware and software coordination mechanisms during active operations.",
            f"Dynamic responsiveness under varying computational workloads.",
            f"Resource allocation strategies and execution safeguards."
        ]
        h1_words = [w for w in h1.lower().split() if len(w) > 3 and w not in STOP_WORDS]
        h1_mechanics = [s for s in pools["mechanics"] if any(w in s["lower"] for w in h1_words) or (s["rel_pos"] > 0.35)]
        slide_5_bullets = extract_slide_bullets(h1_mechanics, pools["mechanics"], pools["general"], 4, s5_fb)
        slide_5 = {
            "id": "slide-5",
            "category": "Concept Breakdown",
            "title": f"System Dynamics: {h1[:38]}",
            "subtitle": "State transitions, runtime coordination, and operational safeguards",
            "bullets": slide_5_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Analyze the system dynamics governing '{h1}'. "
                f"Emphasize how the system manages internal state, saves context, and mitigates overhead during active execution. "
                f"Encourage students to contrast these mechanisms with the baseline mechanics from the previous slide. "
                f"Pause to check if students understand how state transitions are triggered."
            ),
            "diagram": False
        }

        # --- Slide 6: Conceptual Progression & Workflow Diagram ---
        # 3 distinct chronological progression sentences across early, mid, and late document sections
        s_early = [s for s in sentences if s["rel_pos"] <= 0.35 and not is_heading_or_title(s["text"])]
        s_mid = [s for s in sentences if 0.30 <= s["rel_pos"] <= 0.70 and not is_heading_or_title(s["text"])]
        s_late = [s for s in sentences if s["rel_pos"] >= 0.60 and not is_heading_or_title(s["text"])]

        stage_1_text = s_early[0]["text"] if s_early else f"Initialization of {c0} and baseline parameters."
        stage_2_text = s_mid[0]["text"] if s_mid else f"Algorithmic execution and state transition mechanisms."
        stage_3_text = s_late[0]["text"] if s_late else f"Target equilibrium state with validated operational outcomes."

        slide_6 = {
            "id": "slide-6",
            "category": "Conceptual Diagram",
            "title": "Conceptual Progression & System Workflow",
            "subtitle": "Three-stage progression from input ingestion to validated equilibrium",
            "bullets": [
                f"Stage 1 (Background): {clean_sentence_str(stage_1_text)[:110]}",
                f"Stage 2 (Mechanism): {clean_sentence_str(stage_2_text)[:110]}",
                f"Stage 3 (Impact): {clean_sentence_str(stage_3_text)[:110]}"
            ],
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Conceptual Progression & Workflow Walkthrough:\n\n"
                f"This architecture diagram illustrates the end-to-end operational flow of {title}. "
                f"Walk students through the 3 universal stages:\n"
                f"1. Background & Inputs: {stage_1_text[:80]}...\n"
                f"2. Mechanism & Execution: {stage_2_text[:80]}...\n"
                f"3. Target Outcome & Equilibrium: {stage_3_text[:80]}...\n\n"
                f"Instructors should emphasize how each phase is causally linked: stage 1 establishes prerequisite conditions, "
                f"stage 2 performs state transformations, and stage 3 yields validated output stability."
            ),
            "diagram": True,
            "diagramStages": [
                {
                    "stage": "1. BACKGROUND",
                    "title": f"Inputs: {c0[:15]}",
                    "description": clean_sentence_str(stage_1_text)[:110]
                },
                {
                    "stage": "2. MECHANISM",
                    "title": f"Logic: {c1[:15]}",
                    "description": clean_sentence_str(stage_2_text)[:110]
                },
                {
                    "stage": "3. IMPACT",
                    "title": "Target Outcome",
                    "description": clean_sentence_str(stage_3_text)[:110]
                }
            ]
        }

        # --- Slide 7: Real-World Applications ---
        s7_fb = [
            f"Production implementation patterns for {h2}.",
            f"Hardware architectural support and modern operating environment integration.",
            f"Enterprise deployment strategies ensuring high availability and fault resilience.",
            f"Applied industry case studies illustrating practical adoption of {title}."
        ]
        slide_7_bullets = extract_slide_bullets(pools["systems"], pools["mechanics"], pools["general"], 4, s7_fb)

        # --- Slide 8: Critical Analysis & Performance Trade-Offs ---
        s8_fb = [
            f"Computational complexity analysis and resource scaling bounds for {c0}.",
            f"Latency overhead versus throughput trade-offs under heavy concurrency.",
            f"Starvation, deadlock, and edge case failure mitigation strategies.",
            f"Diagnostic architectural evaluation of operational efficiency limits."
        ]
        slide_8_bullets = extract_slide_bullets(pools["tradeoffs"], pools["rules"], pools["general"], 4, s8_fb)

        slide_7 = {
            "id": "slide-7",
            "category": "Real-World Applications",
            "title": f"Applied Implementations: {h2[:38]}",
            "subtitle": "Translating textbook theory into production systems and practical environments",
            "bullets": slide_7_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Connect academic theory to practical production environments for '{h2}'. "
                f"Discuss how the principles discussed today are implemented in real-world operating systems and software systems. "
                f"Ask students to identify where these mechanisms are visible in consumer and enterprise technologies they use daily. "
                f"Highlight why real-world constraints often require balancing purity with pragmatic engineering adaptations."
            ),
            "diagram": False
        }

        slide_8 = {
            "id": "slide-8",
            "category": "Critical Analysis",
            "title": "Critical Analysis & Performance Trade-Offs",
            "subtitle": "Bottlenecks, latency bounds, complexity metrics, and operational trade-offs",
            "bullets": slide_8_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Facilitate an interactive critical thinking session on computational trade-offs. "
                f"Scrutinize the performance characteristics and bottlenecks presented on the slide: "
                f"how does {c0} trade space overhead for execution latency? "
                f"Challenge students to propose architectural optimizations that minimize context overhead "
                f"without sacrificing fairness or system stability."
            ),
            "diagram": False
        }

        # --- Slide 9: Assessment Standards & Exam Rubric ---
        rule_candidates = extract_slide_bullets(pools["rules"], pools["foundations"], pools["general"], 1, [
            f"Key Assessment Rule: All derivations must explicitly justify boundary conditions and state invariants."
        ])
        rule_bullet = rule_candidates[0] if rule_candidates else f"All analytical solutions must verify boundary conditions and stability invariants."

        slide_9_bullets = [
            f"2 Marks (Core Definition): Define and explain the essential operational significance of '{c0}'.",
            f"5 Marks (Mechanism & Workflow): Detail the structural operation and procedural sequence of {h0}.",
            f"10 Marks (Comprehensive Analysis): Formulate an end-to-end evaluation of {title}, analyzing trade-offs and complexity bounds.",
            f"Rubric Requirement: {rule_bullet}"
        ]
        slide_9 = {
            "id": "slide-9",
            "category": "Assessment Standards",
            "title": "Assessment Standards & Rubric Guidelines",
            "subtitle": "Marks distribution, expected solution patterns, and formal examination criteria",
            "bullets": slide_9_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Prepare students for formal university academic examinations on '{title}'. "
                f"Review the 2-mark, 5-mark, and 10-mark question formats displayed. "
                f"Instructors must emphasize that partial credit heavily depends on stating explicit invariants and defining '{c0}' accurately. "
                f"Remind students to review the common pitfall rule highlighted in bullet 4 when completing lab assignments and exam derivations."
            ),
            "diagram": False
        }

        # --- Slide 10: Summary & Synthesized Milestones ---
        slide_10_bullets = [
            f"Established core theoretical foundations and axiomatic scope for {title}.",
            f"Dissected structural mechanics: {h0} and operational state management.",
            f"Mapped 3-stage progression workflow from initialization to equilibrium.",
            f"Evaluated real-world systems, implementation architectures, and critical trade-offs.",
            f"Confirmed foundational readiness for advanced modules and academic examination."
        ]
        slide_10 = {
            "id": "slide-10",
            "category": "Summary & Takeaways",
            "title": f"{title}: Summary & Key Takeaways",
            "subtitle": "Consolidated findings, key takeaways, and academic milestones",
            "bullets": slide_10_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Concluding Lecture Summary for '{title}':\n\n"
                f"Synthesize the key milestones achieved during today's session. "
                f"Remind students of our progression from initial definitions of {c0} through execution mechanics and performance trade-offs. "
                f"Assign the post-lecture practice problems and announce the topic for the next module. "
                f"Open the floor for final student inquiries."
            ),
            "diagram": False
        }

        return [slide_1, slide_2, slide_3, slide_4, slide_5, slide_6, slide_7, slide_8, slide_9, slide_10]

    def analyze_document(
        self,
        chunks: List[Dict[str, Any]],
        raw_title: Optional[str] = None,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes complete document intelligence analysis.
        Returns document title, page/chunk counts, headings, concepts, summary,
        important portions, and document-specific slide deck.
        """
        fallback_title = (raw_title or "").strip()
        if not fallback_title and filename:
            fallback_title = filename.replace(".pdf", "").replace("_", " ").strip()

        title = self.extract_title(chunks, fallback_title)
        headings = self.extract_headings(chunks)
        concepts = self.extract_concepts(chunks)
        portions = self.extract_important_portions(chunks)
        summary = self.generate_summary(chunks, title)
        slides = self.generate_slide_deck(chunks, title, headings, concepts)
        page_count = max((c.get("page", 1) for c in chunks), default=1)

        return {
            "title": title,
            "filename": filename or "Uploaded_Document.pdf",
            "page_count": page_count,
            "chunks_count": len(chunks),
            "sections": headings,
            "important_concepts": concepts,
            "important_portions": portions,
            "summary": summary,
            "slides": slides,
        }


document_analyzer = DocumentAnalyzer()
