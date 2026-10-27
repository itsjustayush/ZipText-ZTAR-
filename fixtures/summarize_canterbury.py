import json

data = json.load(open('reports/v0/v0.2.0/canterbury/four_tier_canterbury_corpus.json', encoding='utf-8'))
header = f"{'File':<13} | {'Raw':<10} | {'GZIP':<8} | {'Zstd':<8} | {'LZ4':<8} | {'Brotli':<8} | {'LZMA':<8} | {'ZIP':<8} | {'ZTAR-ZBIN':<9} | {'ZTAR-ZTXT'}"
print(header)
print("-" * len(header))
for r in data['results']:
    b = r['baselines']
    print(f"{r['file_name']:<13} | {r['original_size_bytes']:<10,} | {b['zlib_bytes']:<8,} | {b['zstd_bytes']:<8,} | {b['lz4_bytes']:<8,} | {b['brotli_bytes']:<8,} | {b['lzma_bytes']:<8,} | {b['zip_bytes']:<8,} | {r['complete_zbin_container_bytes']:<9,} | {r['complete_ztxt_container_bytes']:,}")
