import csv
import json
import os
from pathlib import Path


WORKSPACE = Path('/Users/kristina.abdullina/IdeaProjects/whisper-comparing')


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_words_csv(target_csv: Path, rows: list[tuple[str, float, float]]) -> None:
    ensure_dir(target_csv.parent)
    with target_csv.open('w', newline='') as f:
        writer = csv.writer(f)
        # As requested: three columns only — word,start,end
        for word, start, end in rows:
            writer.writerow([word, f"{start}", f"{end}"])


def parse_whisper_timestamped(src_root: Path, out_root: Path) -> None:
    # Each subdirectory contains files; we want the *.words.csv
    for sub in sorted(src_root.iterdir()):
        if not sub.is_dir():
            continue
        words_csvs = list(sub.glob('*.words.csv'))
        if not words_csvs:
            continue
        # Typically there is exactly one words.csv per run
        for words_csv in words_csvs:
            rows: list[tuple[str, float, float]] = []
            with words_csv.open() as f:
                reader = csv.reader(f)
                for row in reader:
                    if not row or len(row) < 3:
                        continue
                    word, start, end = row[0], row[1], row[2]
                    # Some files might have headers; skip if cannot parse floats
                    try:
                        start_f = float(start)
                        end_f = float(end)
                    except ValueError:
                        continue
                    rows.append((word, start_f, end_f))

            target_rel = sub.name  # e.g., Song_large-v3
            target_csv = out_root / 'whisper_timestamped' / f"{target_rel}.csv"
            write_words_csv(target_csv, rows)


def parse_whisper_openai(src_root: Path, out_root: Path) -> None:
    # Files are JSON with segments; use segment-level timings (text,start,end)
    for jf in sorted(src_root.glob('*.json')):
        try:
            data = json.loads(jf.read_text())
        except Exception:
            continue

        rows: list[tuple[str, float, float]] = []
        segments = data.get('segments') or []
        for seg in segments:
            text = seg.get('text')
            start = seg.get('start')
            end = seg.get('end')
            if text is None or start is None or end is None:
                continue
            text_str = str(text).strip()
            if not text_str:
                continue
            try:
                rows.append((text_str, float(start), float(end)))
            except (TypeError, ValueError):
                continue

        # Fallback: if no words, try to split segment text into tokens without timings (skip since we need timings)
        target_csv = out_root / 'whisper_openai' / (jf.stem + '.csv')
        write_words_csv(target_csv, rows)


def parse_whisperx(src_root: Path, out_root: Path) -> None:
    # Each song/run is a directory containing a primary JSON (same basename as dir or audio)
    for sub in sorted(src_root.iterdir()):
        if not sub.is_dir():
            continue
        # Find a json file inside
        json_files = list(sub.glob('*.json'))
        if not json_files:
            continue
        jf = json_files[0]
        try:
            data = json.loads(jf.read_text())
        except Exception:
            continue

        rows: list[tuple[str, float, float]] = []
        # Prefer a flat list if available
        word_segments = data.get('word_segments')
        if isinstance(word_segments, list) and word_segments:
            for w in word_segments:
                word = w.get('word')
                start = w.get('start')
                end = w.get('end')
                if word is None or start is None or end is None:
                    continue
                try:
                    rows.append((str(word), float(start), float(end)))
                except (TypeError, ValueError):
                    continue
        else:
            # Otherwise, collect from segments[].words[]
            segments = data.get('segments') or []
            for seg in segments:
                for w in seg.get('words') or []:
                    word = w.get('word') or w.get('text')
                    start = w.get('start')
                    end = w.get('end')
                    if word is None or start is None or end is None:
                        continue
                    try:
                        rows.append((str(word), float(start), float(end)))
                    except (TypeError, ValueError):
                        continue

        target_csv = out_root / 'whisperx' / f"{sub.name}.csv"
        write_words_csv(target_csv, rows)


def main() -> None:
    out_root = WORKSPACE / 'aggregated_words'
    ensure_dir(out_root)

    parse_whisper_timestamped(
        WORKSPACE / 'whisper_timestamped_result', out_root
    )
    parse_whisper_openai(
        WORKSPACE / 'whisper_openai_result', out_root
    )
    # whisperx may be optional/untracked; handle if present
    whisperx_dir = WORKSPACE / 'whisperx_result'
    if whisperx_dir.exists():
        parse_whisperx(whisperx_dir, out_root)

    # Build one combined table: song,source,text,start,end
    combined_path = out_root / 'all_results.csv'
    with combined_path.open('w', newline='') as f_out:
        writer = csv.writer(f_out)
        # No header to keep consistent with per-source files
        for source in ('whisper_timestamped', 'whisper_openai', 'whisperx'):
            src_dir = out_root / source
            if not src_dir.exists():
                continue
            for csv_file in sorted(src_dir.glob('*.csv')):
                song = csv_file.stem
                with csv_file.open() as f_in:
                    reader = csv.reader(f_in)
                    for row in reader:
                        if len(row) < 3:
                            continue
                        text, start, end = row[0], row[1], row[2]
                        writer.writerow([song, source, text, start, end])


if __name__ == '__main__':
    main()


