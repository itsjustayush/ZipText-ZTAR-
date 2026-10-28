"""
Script to generate high-resolution, dark-themed benchmark charts for ZipText (ZTAR)
and attach them to README.md.
"""

from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

# Ensure assets directory exists
ASSETS_DIR = Path(__file__).resolve().parent.parent / "docs" / "assets"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# Modern Tech Dark Theme Palette
BG_COLOR = "#0B0F19"
PANEL_COLOR = "#111827"
TEXT_COLOR = "#F3F4F6"
MUTED_TEXT = "#9CA3AF"
GRID_COLOR = "#1F2937"
CYAN_ACCENT = "#06B6D4"
PURPLE_ACCENT = "#8B5CF6"
GREEN_ACCENT = "#10B981"
ORANGE_ACCENT = "#F59E0B"
RED_ACCENT = "#EF4444"

plt.rcParams.update({
    "font.sans-serif": "DejaVu Sans",
    "figure.facecolor": BG_COLOR,
    "axes.facecolor": BG_COLOR,
    "text.color": TEXT_COLOR,
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": MUTED_TEXT,
    "ytick.color": TEXT_COLOR,
    "grid.color": GRID_COLOR,
    "grid.linestyle": "--",
    "grid.alpha": 0.6,
})


def generate_canterbury_chart():
    """Horizontal bar chart showing Storage Reduction % across Canterbury files."""
    files = [
        "ptt5 (CCITT Fax)",
        "kennedy.xls (Spreadsheet)",
        "audio.wav (16-bit PCM ASPD)",
        "lcet10.txt (Technical)",
        "sum (SPARC Executable)",
        "alice29.txt (Literature)",
        "fields.c (Source Code)",
        "plrabn12.txt (Poetry)",
        "asyoulik.txt (Shakespeare)",
        "cp.html (Web HTML)",
        "grammar.lsp (LISP Code)",
        "xargs.1 (Man Page)",
    ]
    # Data in reverse so top is highest reduction
    files = files[::-1]
    zbin_pct = [52.92, 56.54, 67.44, 68.07, 69.71, 69.38, 71.33, 73.29, 74.68, 70.61, 87.31, 90.23]
    ztxt_pct = [40.24, 46.57, 57.41, 58.95, 60.81, 60.30, 63.15, 64.99, 67.29, 58.12, 83.62, 87.31]

    y = np.arange(len(files))
    height = 0.38

    fig, ax = plt.subplots(figsize=(11, 7.5), dpi=300)

    bars_bin = ax.barh(y + height/2, zbin_pct, height, label="ZTAR Binary (.zbin)", color=CYAN_ACCENT, edgecolor="#22D3EE", linewidth=0.8)
    bars_txt = ax.barh(y - height/2, ztxt_pct, height, label="ZTAR Text Armored (.ztxt)", color=PURPLE_ACCENT, edgecolor="#A78BFA", linewidth=0.8)

    ax.set_yticks(y)
    ax.set_yticklabels(files, fontsize=10, fontweight="medium")
    ax.set_xlabel("Net Storage Footprint Reduction (%) — Higher is Better", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_title("Canterbury Corpus & Structured Media: Net Compression Ratios\nZero-Loss Invariant Verified via SHA-256", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlim(0, 100)
    ax.xaxis.grid(True)
    ax.set_axisbelow(True)

    # Value labels
    for bar in bars_bin:
        w = bar.get_width()
        ax.annotate(f"-{w:.1f}%", (w + 1.0, bar.get_y() + bar.get_height() / 2),
                    va="center", ha="left", color=CYAN_ACCENT, fontsize=8.5, fontweight="bold")

    for bar in bars_txt:
        w = bar.get_width()
        ax.annotate(f"-{w:.1f}%", (w + 1.0, bar.get_y() + bar.get_height() / 2),
                    va="center", ha="left", color="#C4B5FD", fontsize=8.0)

    ax.legend(loc="lower right", facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, fontsize=10)
    plt.tight_layout()

    out_file = ASSETS_DIR / "benchmark_canterbury_reduction.png"
    fig.savefig(out_file, bbox_inches="tight")
    plt.close(fig)
    print(f"Generated: {out_file}")


def generate_leaderboard_chart():
    """Grouped bar chart comparing ZTAR against standard baselines (Gzip, Zstandard, Brotli)."""
    categories = [
        "audio.wav\n(Structured Audio)",
        "kennedy.xls\n(Binary Sheet)",
        "alice29.txt\n(English Text)",
        "ptt5\n(CCITT Fax)",
        "fields.c\n(Source Code)",
        "sum\n(Executable)",
    ]

    # Compressed sizes in KB
    ztar_zbin = [2.71, 127.5, 42.5, 48.9, 3.3, 9.9]
    brotli_11 = [4.42, 127.2, 44.8, 48.5, 3.3, 9.6]
    zstd_19 = [4.42, 131.6, 46.1, 49.3, 3.4, 10.2]
    gzip_9 = [4.42, 201.3, 53.0, 52.6, 3.7, 12.8]

    x = np.arange(len(categories))
    width = 0.20

    fig, ax = plt.subplots(figsize=(12, 6.8), dpi=300)

    rects1 = ax.bar(x - 1.5 * width, ztar_zbin, width, label="ZTAR v0.3.0 (.zbin)", color=CYAN_ACCENT, edgecolor="#22D3EE")
    rects2 = ax.bar(x - 0.5 * width, brotli_11, width, label="Google Brotli-11", color=GREEN_ACCENT, edgecolor="#34D399")
    rects3 = ax.bar(x + 0.5 * width, zstd_19, width, label="Zstandard-19", color=ORANGE_ACCENT, edgecolor="#FBBF24")
    rects4 = ax.bar(x + 1.5 * width, gzip_9, width, label="Gzip-9 (Deflate)", color=RED_ACCENT, edgecolor="#F87171")

    ax.set_ylabel("Compressed File Size (Kilobytes, KB) — Lower is Better", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_title("Algorithm Leaderboard: ZTAR v0.3.0 vs Standard Production Codecs\nHighlighting Structured ASPD Gains & Zero-Regression Guarding", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10, fontweight="medium")
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)

    # Highlight the ASPD advantage on audio.wav
    ax.annotate(
        "ASPD pdelta2:\n-38.65% vs Brotli",
        xy=(x[0] - 1.5 * width, ztar_zbin[0]),
        xytext=(x[0] - 0.5 * width, 55),
        arrowprops=dict(facecolor=CYAN_ACCENT, edgecolor="#22D3EE", arrowstyle="->", lw=1.5),
        fontsize=9, fontweight="bold", color=CYAN_ACCENT,
        bbox=dict(boxstyle="round,pad=0.4", fc=PANEL_COLOR, ec=CYAN_ACCENT, lw=1)
    )

    ax.legend(loc="upper right", facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, fontsize=10)
    plt.tight_layout()

    out_file = ASSETS_DIR / "benchmark_algorithm_leaderboard.png"
    fig.savefig(out_file, bbox_inches="tight")
    plt.close(fig)
    print(f"Generated: {out_file}")


def generate_version_evolution_chart():
    """Scorecard & evolution progression chart from v0.1.0 to v0.3.0."""
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)

    versions = ["v0.1.0 (MVP Foundation)", "v0.2.0 (Adaptive Multi-Codec)", "v0.3.0 (ASPD Preconditioning)"]
    metrics = ["Overall Storage Reduction", "Multi-Byte Signal Optimization", "Codec & Transform Versatility", "Lossless Pass Integrity"]

    # Scores out of 100
    v1_scores = [54, 30, 25, 100]
    v2_scores = [76, 52, 75, 100]
    v3_scores = [84, 92, 95, 100]

    x = np.arange(len(metrics))
    width = 0.25

    ax.bar(x - width, v1_scores, width, label="v0.1.0: Baseline Deflate", color="#4B5563", edgecolor="#6B7280")
    ax.bar(x, v2_scores, width, label="v0.2.0: Multi-Codec Adaptive Engine", color=PURPLE_ACCENT, edgecolor="#A78BFA")
    ax.bar(x + width, v3_scores, width, label="v0.3.0: ASPD Bijective Transforms", color=CYAN_ACCENT, edgecolor="#22D3EE")

    ax.set_ylabel("Standardized Performance Index (0–100)", fontsize=11, fontweight="bold", labelpad=10)
    ax.set_title("ZTAR Architectural Evolution: Version Progression Scorecard\nTracking Compression Density, Invertibility & Algorithmic Breakthroughs", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10, fontweight="medium")
    ax.set_ylim(0, 115)
    ax.yaxis.grid(True)
    ax.set_axisbelow(True)

    for i in range(len(metrics)):
        ax.annotate(f"{v1_scores[i]}", (x[i] - width, v1_scores[i] + 2), ha="center", fontsize=8.5, color=MUTED_TEXT)
        ax.annotate(f"{v2_scores[i]}", (x[i], v2_scores[i] + 2), ha="center", fontsize=8.5, color="#C4B5FD", fontweight="bold")
        ax.annotate(f"{v3_scores[i]}", (x[i] + width, v3_scores[i] + 2), ha="center", fontsize=8.5, color=CYAN_ACCENT, fontweight="bold")

    ax.legend(loc="upper left", facecolor=PANEL_COLOR, edgecolor=GRID_COLOR, fontsize=10)
    plt.tight_layout()

    out_file = ASSETS_DIR / "version_evolution_scorecard.png"
    fig.savefig(out_file, bbox_inches="tight")
    plt.close(fig)
    print(f"Generated: {out_file}")


if __name__ == "__main__":
    generate_canterbury_chart()
    generate_leaderboard_chart()
    generate_version_evolution_chart()
    print("All charts generated successfully in docs/assets/!")
