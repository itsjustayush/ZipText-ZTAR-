import json
from pathlib import Path

txt_data = json.loads(Path('reports/v0/v0.2.0/matrix_results.json').read_text(encoding='utf-8'))
bin_data = json.loads(Path('reports/v0/v0.2.0/matrix_results_binary.json').read_text(encoding='utf-8'))

def get_best(data):
    best = {}
    for r in data['results']:
        fn = r['file_name']
        if fn not in best or r['encoded_size_bytes'] < best[fn]['encoded_size_bytes']:
            best[fn] = r
    return best

t_best = get_best(txt_data)
b_best = get_best(bin_data)

header = f"{'File Name':<16} | {'Orig Size':<10} | {'Best .ztxt':<10} {'%':<8} | {'Best .zbin':<10} {'%':<8} | {'Best Codec':<10} | {'Format Verified'}"
print(header)
print("-" * len(header))
for fn in sorted(t_best.keys()):
    tb = t_best[fn]
    bb = b_best[fn]
    print(f"{fn:<16} | {tb['original_size_bytes']:<10,} | {tb['encoded_size_bytes']:<10,} {tb['size_change_pct']:+6.1f}% | {bb['encoded_size_bytes']:<10,} {bb['size_change_pct']:+6.1f}% | {bb['codecs_used']:<10} | {tb['media_format']}")
