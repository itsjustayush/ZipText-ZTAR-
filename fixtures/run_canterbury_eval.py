from ziptext.benchmarks.four_tier_eval import FourTierEvaluator

evaluator = FourTierEvaluator(output_dir='reports/v0/v0.2.0/canterbury')
rows = evaluator.evaluate_directory('fixtures/canterbury', category='Canterbury Corpus')

header = f"{'File':<14} | {'Rep A (Orig)':<12} | {'Rep B (Comp)':<12} | {'Rep C (B85)':<12} | {'Rep D (ZTXT)':<12} | {'Rep D (ZBIN)':<12} | {'Best Codec':<10} | {'Match'}"
print(header)
print("-" * len(header))
for r in rows:
    print(f"{r.file_name:<14} | {r.original_size_bytes:<12,} | {r.compressed_binary_bytes:<12,} | {r.compressed_text_bytes:<12,} | {r.complete_ztxt_container_bytes:<12,} | {r.complete_zbin_container_bytes:<12,} | {r.best_codec:<10} | {r.exact_match}")
