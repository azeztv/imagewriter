"""Benchmark: 30 plain-language queries against the indexed library; top-1 and top-5 for keywords, CLAP and hybrids.

Run: uv run --no-project --python 3.12 --with numpy --with scipy --with librosa --with soundfile --with pyloudnorm
     --with psutil --with torch --with transformers python eval.py
A query is a hit when a result's path contains one of its fragments. "impact" queries are the short-hit subset.
"""
import sys
from pathlib import Path

import numpy

sys.path.insert(0, str(Path(__file__).parent))
import sound_library as library

# (query, path fragments that count as right, is a short impact)
QUERIES = [
    ("a heavy wooden door shut hard", ["door-slam"], True),
    ("someone walking on loose small stones", ["footsteps-gravel"], False),
    ("a car tyre suddenly exploding", ["tire-burst", "tyre-burst"], True),
    ("a window pane smashing into pieces", ["glass-break", "glass-shatter"], True),
    ("a person tapping on a computer keyboard", ["keyboard"], False),
    ("a fighter plane passing overhead fast", ["jet-flyby", "sonic-boom"], False),
    ("hospital machine that beeps with a heartbeat", ["monitor-beep", "flatline"], False),
    ("crowd of people screaming in panic", ["scream-crowd", "crowd-panic", "crowd-shout"], False),
    ("a campfire popping and crackling", ["fire-crackle", "wildfire"], False),
    ("water running from a kitchen faucet", ["tap-running", "tap-trickle"], False),
    ("a tree trunk breaking and crashing down", ["tree-crack-fall", "wood-snap"], True),
    ("distant rolling thunder in a storm", ["thunder"], False),
    ("metal object dropped onto a wooden floor", ["metal-drop-wood", "tool-drop"], True),
    ("a small coin spinning on a table", ["coin"], False),
    ("the click of a light switch", ["switch"], True),
    ("soft knocking on a wooden table", ["knock", "woodblock"], True),
    ("a fast swish of air", ["whoosh", "cloth-swish"], False),
    ("a clock ticking", ["clock"], False),
    ("bubbling thick mud", ["mud-bubbles", "lava-bubble", "mud-squelch"], False),
    ("loud electrical sparks and buzzing", ["electric-arc", "sparks", "transformer-burst", "electric-hum"], False),
    ("a brick hitting the ground", ["brick-drop", "brick-thunk"], True),
    ("a body falling heavily onto the floor", ["body-fall-floor", "body-impact", "body-thud"], True),
    ("a sharp crack of a breaking bone", ["bone-crack"], True),
    ("a pipe struck with a loud bang", ["pipe-bang", "water-hammer"], True),
    ("a sheet of frozen water splitting", ["ice-crack"], True),
    ("a heavy metallic clank", ["metal-clank", "manhole-clank", "lever-clunk"], True),
    ("something heavy landing with a dull thump", ["thud", "wood-thud", "header-thud"], True),
    ("one wet footstep", ["step-wet"], True),
    ("a deep explosion boom", ["boom", "explosion-distant", "sub-boom"], True),
    ("a lavatory being flushed", ["toilet-flush"], False),
]


def first_hit_rank(order, records, fragments):
    for rank, row in enumerate(order, start=1):
        path = records[row]["path"].lower()
        if any(fragment in path for fragment in fragments):
            return rank
    return None


def summarize(ranks_by_query):
    def counts(selected):
        ranks = [ranks_by_query[index] for index in selected]
        return (sum(1 for rank in ranks if rank == 1), sum(1 for rank in ranks if rank is not None and rank <= 5), len(ranks))
    everything = range(len(QUERIES))
    impacts = [i for i in everything if QUERIES[i][2]]
    return counts(everything), counts(impacts)


def main():
    library.lower_priority()
    records, vectors = library.load_index()
    clap = library.ClapBundle()
    plain = [clap.query_vector(query, library.QUERY_TEMPLATES_PLAIN) for query, _, _ in QUERIES]
    ensemble = [clap.query_vector(query, library.QUERY_TEMPLATES_ENSEMBLE) for query, _, _ in QUERIES]
    clap.release()
    keywords = [library.bm25_scores(records, query) for query, _, _ in QUERIES]

    def run(label, query_vectors, keyword_weight, impact_strength, keywords_only=False):
        ranks = []
        for index, (query, fragments, _) in enumerate(QUERIES):
            if keywords_only:
                scores = keywords[index]
                order = numpy.argsort(-scores, kind="stable")
                ranks.append(None if scores.max() == 0 else first_hit_rank(order, records, fragments))
                continue
            similarity = vectors @ query_vectors[index]
            prior = library.impact_prior(records, query, impact_strength)
            scores = library.hybrid_scores(similarity, keywords[index], prior, keyword_weight)
            ranks.append(first_hit_rank(numpy.argsort(-scores, kind="stable"), records, fragments))
        return label, ranks

    filename_ranks = []
    for query, fragments, _ in QUERIES:
        words = set(library.query_words(query))
        overlap = numpy.array([len(words & set(library.split_words(Path(record["path"]).stem))) for record in records])
        order = numpy.argsort(-overlap, kind="stable")
        filename_ranks.append(None if overlap.max() == 0 else first_hit_rank(order, records, fragments))

    configurations = [
        ("filename words only (old baseline)", filename_ranks),
        run("keywords only (BM25 on tags+titles)", None, 0, 0, keywords_only=True),
        run("CLAP, plain query", plain, 0, 0),
        run("CLAP, 4-phrasing average", ensemble, 0, 0),
        run("hybrid kw 1.0", ensemble, 1.0, 0),
        run("hybrid kw 2.0", ensemble, 2.0, 0),
        run("hybrid kw 3.0", ensemble, 3.0, 0),
        run("hybrid kw 1.0 + impact prior 0.5", ensemble, 1.0, 0.5),
        run("hybrid kw 2.0 + impact prior 0.5", ensemble, 2.0, 0.5),
        run("hybrid kw 2.0 + impact prior 1.0", ensemble, 2.0, 1.0),
        run("hybrid kw 3.0 + impact prior 0.5", ensemble, 3.0, 0.5),
        run("CLAP 4-phrasing + impact prior 0.5", ensemble, 0, 0.5),
    ]
    print(f"{len(records)} files indexed, {len(QUERIES)} queries ({sum(1 for q in QUERIES if q[2])} impact)\n")
    print(f"{'configuration':40} {'top-1':>7} {'top-5':>7} | {'impact top-1':>12} {'impact top-5':>12}")
    for label, ranks in configurations:
        (top1, top5, total), (impact1, impact5, impact_total) = summarize(ranks)
        print(f"{label:40} {top1:>4}/{total:<2} {top5:>4}/{total:<2} | {impact1:>9}/{impact_total:<2} {impact5:>9}/{impact_total:<2}")

    print("\nper-query rank of the first right file (hybrid kw 2.0 + impact prior 0.5; '-' = absent):")
    ranks = configurations[8][1]
    plain_ranks = configurations[2][1]
    for (query, _, is_impact), rank, plain_rank in zip(QUERIES, ranks, plain_ranks):
        print(f"  {'*' if is_impact else ' '} {query[:48]:48} plain CLAP {plain_rank or '-':>4}   tuned {rank or '-':>4}")


if __name__ == "__main__":
    main()
