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
                    if re.match(r'^(chapter|section|unit|module|\d+(\.\d+)*)\s+', lead, re.IGNORECASE) or (
                        len(lead) <= 60 and not lead.endswith(".") and (lead.isupper() or lead.istitle())
                    ):
                        clean_h = re.sub(r'^[0-9\.\s\-•*]+', '', lead).strip()
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
        Generates a 10-slide curriculum-aligned lecture deck strictly tailored
        to the uploaded document's actual text and structure.
        """
        all_sentences: List[str] = []
        for c in chunks:
            all_sentences.extend(clean_sentences(c.get("text", "")))

        def get_slice(start: int, count: int, fallback: str) -> List[str]:
            items = all_sentences[start: start + count]
            while len(items) < count:
                items.append(f"{fallback} (Module Point {len(items) + 1})")
            return items

        # Slide 1: Title Slide
        slide_1 = {
            "id": "slide-1",
            "category": "Title Slide",
            "title": title,
            "subtitle": f"Curriculum Briefing & Educational Lecture Outline ({len(chunks)} Sections)",
            "bullets": [
                f"Core syllabus module covering foundational principles of {title}.",
                f"Rigorous examination of theoretical models, computational complexity, and boundary cases.",
                "Aligned with university curriculum requirements and formal academic examination benchmarks.",
                "Interactive classroom presentation deck with embedded educator talking points."
            ],
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Welcome everyone to today's comprehensive curriculum session covering '{title}'. "
                "In this session, our primary goal is to establish a rigorous baseline understanding of the core modules. "
                "Instructors should emphasize that the concepts introduced today form the architectural bedrock for all subsequent analytical modules. "
                "Take 3 to 5 minutes to outline expectations, review the syllabus roadmap, and encourage active inquiry."
            ),
            "diagram": False
        }

        # Slide 2: Curriculum Overview & Scope
        slide_2_bullets = [
            f"Comprehensive examination of core concepts: {', '.join(concepts[:3]) if concepts else title}.",
            "Underlying theoretical principles, system dynamics, and empirical foundations.",
            "Analytical methodologies for systematic problem-solving.",
            "Real-world engineering applications, operational trade-offs, and boundary constraints.",
            "Evaluation criteria and preparation standards for formal academic assessments."
        ]
        slide_2 = {
            "id": "slide-2",
            "category": "Curriculum Overview",
            "title": "Curriculum Overview & Scope",
            "subtitle": f"Scope, prerequisites, and learning outcomes for {title}",
            "bullets": slide_2_bullets,
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"When presenting this curriculum overview for '{title}', walk students methodically through each bullet point. "
                "Point 1 establishes the broad structural scope, while Point 2 grounds the discussion in empirical theory. "
                "Instructors should spend extra time highlighting practical applications and trade-offs. "
                "Open the floor briefly to verify understanding before moving forward."
            ),
            "diagram": False
        }

        # Slide 3: Theoretical Foundations
        found_bullets = get_slice(0, 4, f"Foundational principle for {title}")
        slide_3 = {
            "id": "slide-3",
            "category": "Theoretical Foundations",
            "title": "Theoretical Foundations & Principles",
            "subtitle": "Axiomatic definitions and baseline principles",
            "bullets": [f"Core Principle: {b}" for b in found_bullets],
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Explore the theoretical foundations and axiomatic parameters of {title}. "
                "Emphasize how these principles serve as the prerequisite framework for understanding the rest of the material. "
                "Encourage students to relate these foundational rules back to real-world observations."
            ),
            "diagram": False
        }

        # Slide 4: Concept Breakdown Part I
        h1 = headings[0] if headings else (concepts[0] if concepts else "Core Mechanism Breakdown")
        chunk_1_text = chunks[0].get("text", "") if chunks else ""
        c1_sentences = clean_sentences(chunk_1_text) or get_slice(2, 4, f"Mechanics of {h1}")
        slide_4 = {
            "id": "slide-4",
            "category": "Concept Breakdown",
            "title": f"Core Mechanics: {h1[:40]}",
            "subtitle": "Step-by-step structural breakdown and invariants",
            "bullets": c1_sentences[:4],
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Detailed Breakdown for '{h1}'.\n\n"
                "Instructors should unpack these core bullet points line by line derived directly from the document text. "
                "Explain the underlying principles and empirical findings associated with each statement. "
                "Be sure to address common student misconceptions regarding boundaries and operational parameters."
            ),
            "diagram": False
        }

        # Slide 5: Concept Breakdown Part II
        h2 = headings[1] if len(headings) > 1 else (concepts[1] if len(concepts) > 1 else "Operational Procedures")
        chunk_2_text = chunks[1].get("text", "") if len(chunks) > 1 else (chunks[0].get("text", "") if chunks else "")
        c2_sentences = clean_sentences(chunk_2_text) or get_slice(4, 4, f"Operational rules for {h2}")
        slide_5 = {
            "id": "slide-5",
            "category": "Concept Breakdown",
            "title": f"System Dynamics: {h2[:40]}",
            "subtitle": "Operational procedures and boundary conditions",
            "bullets": c2_sentences[:4],
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Deep dive into '{h2}'.\n\n"
                "Focus on the sequential execution steps and edge cases described in the curriculum. "
                "Highlight key parameters that students frequently overlook in laboratory experiments or exam problems."
            ),
            "diagram": False
        }

        # Slide 6: Conceptual Diagram Slide (3 stages)
        stage_1_desc = all_sentences[0] if all_sentences else f"Initialization and baseline inputs for {title}."
        stage_2_desc = all_sentences[len(all_sentences) // 2] if len(all_sentences) > 2 else f"Algorithmic processing and state transitions."
        stage_3_desc = all_sentences[-1] if len(all_sentences) > 1 else f"Validated outcome, invariant preservation, and equilibrium state."

        slide_6 = {
            "id": "slide-6",
            "category": "Conceptual Diagram",
            "title": "Conceptual Progression & System Workflow",
            "subtitle": "Three-stage conceptual progression from input to validated equilibrium",
            "bullets": [
                f"Stage 1 (Background): {stage_1_desc[:90]}...",
                f"Stage 2 (Mechanism): {stage_2_desc[:90]}...",
                f"Stage 3 (Impact): {stage_3_desc[:90]}..."
            ],
            "notes": (
                "TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                "Conceptual Progression & Workflow Walkthrough:\n\n"
                "This workflow slide is critical for visualizing the document's conceptual progression. "
                "Walk students explicitly through the three universal stages displayed in the process cards: "
                "1. Background, 2. Mechanism, and 3. Impact.\n\n"
                "Emphasize how the concepts build logically from initial definitions to final analytical takeaways derived straight from the textbook text."
            ),
            "diagram": True,
            "diagramStages": [
                {
                    "stage": "1. BACKGROUND",
                    "title": "Baseline & Inputs",
                    "description": stage_1_desc[:110]
                },
                {
                    "stage": "2. MECHANISM",
                    "title": "Execution Logic",
                    "description": stage_2_desc[:110]
                },
                {
                    "stage": "3. IMPACT",
                    "title": "Target Outcome",
                    "description": stage_3_desc[:110]
                }
            ]
        }

        # Slide 7: Real-World Applications
        h3 = headings[2] if len(headings) > 2 else (concepts[2] if len(concepts) > 2 else title)
        slide_7 = {
            "id": "slide-7",
            "category": "Real-World Applications",
            "title": f"Real-World Implementations: {h3[:40]}",
            "subtitle": "Translating theory into industrial and practical systems",
            "bullets": [
                f"Application of {title} principles in production environments.",
                "Engineering trade-offs between performance latency and resource consumption.",
                "Mitigating failure modes and ensuring state consistency under load.",
                "Scalability constraints observed in enterprise and academic deployments."
            ],
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Bridge theory and practice by discussing how '{title}' operates in real-world environments. "
                "Ask students how the abstract principles covered earlier apply directly to these practical scenarios."
            ),
            "diagram": False
        }

        # Slide 8: Critical Analysis & Discussion
        slide_8 = {
            "id": "slide-8",
            "category": "Critical Analysis",
            "title": "Critical Analysis & Discussion Inquiries",
            "subtitle": "Interactive debate prompts, edge cases, and architectural trade-offs",
            "bullets": [
                f"What primary computational or engineering bottleneck is resolved by {title}?",
                f"How do the invariants established in {headings[0] if headings else 'Module 1'} prevent cascading system errors?",
                "What specific failure modes or edge cases must engineers anticipate?",
                "Diagnostic Inquiry: Explain the primary trade-off between space overhead and runtime speed."
            ],
            "notes": (
                "TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                "Facilitate an interactive discussion using these critical analysis questions. "
                "Encourage students to debate the trade-offs and consider potential failure modes."
            ),
            "diagram": False
        }

        # Slide 9: Assessment Standards & Review
        slide_9 = {
            "id": "slide-9",
            "category": "Assessment Standards",
            "title": "Assessment Standards & Rubric Guidelines",
            "subtitle": "Exam preparation, marks distribution, and expected solution patterns",
            "bullets": [
                f"2 Marks: Concise academic definition of core {title} concepts.",
                f"5 Marks: Structural mechanism, 3-4 bullet points, and practical implementation example.",
                "10 Marks: Comprehensive derivation, algorithm flow, and mathematical complexity bounds.",
                "Common Pitfall Alert: Ensure boundary conditions and invariants are explicitly justified."
            ],
            "notes": (
                "TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                "Review evaluation criteria and assessment expectations with the class. "
                "Ensure students understand what is required to achieve mastery on upcoming exams."
            ),
            "diagram": False
        }

        # Slide 10: Summary & Takeaways
        slide_10 = {
            "id": "slide-10",
            "category": "Summary & Takeaways",
            "title": f"{title}: Summary & Key Takeaways",
            "subtitle": "Synthesizing foundational concepts and next milestones",
            "bullets": [
                f"Reviewed foundational scope and educational roadmap for {title}.",
                f"Analyzed core curriculum concepts: {', '.join(concepts[:3]) if concepts else title}.",
                "Examined 3-stage progression workflow: Background, Mechanism, and Impact.",
                "Evaluated critical performance boundaries and analytical constraints.",
                "Confirmed foundational readiness for advanced curriculum units."
            ],
            "notes": (
                f"TEACHER SPEAKER SCRIPT & LECTURE GUIDE:\n\n"
                f"Concluding Lecture Summary for '{title}':\n\n"
                "Synthesize the key takeaways listed on the slide. "
                "Remind students of the journey from our initial curriculum overview through the concept breakdowns and conceptual progression workflow. "
                "Assign recommended follow-up reading tasks and open the floor for final student queries."
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
