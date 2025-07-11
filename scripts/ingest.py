#!/usr/bin/env python3
import os
from watcher.chains.embeddings import index_log_chunks
from watcher.chains.summarizer import chunk_logs

# Directory containing your log files (relative to project root or absolute)
LOG_DIR = "logs/"

def main():
    # 1) Debug: show where we are and what files we'll process
    print("Working directory:", os.getcwd())
    if not os.path.isdir(LOG_DIR):
        print(f"❌ LOG_DIR not found: {LOG_DIR}")
        return

    files = os.listdir(LOG_DIR)
    print(f"Contents of '{LOG_DIR}':", files)
    if not files:
        print(f"❌ No files found in {LOG_DIR}")
        return

    # 2) Process each file
    for fname in files:
        path = os.path.join(LOG_DIR, fname)
        if not os.path.isfile(path):
            print(f"⏭️ Skipping {fname}: not a regular file")
            continue

        # 3) Read with fallback for encoding issues
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except UnicodeDecodeError:
            print(f"⚠️  Unicode error in {fname}, retrying with replacement…")
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()

        # 4) Chunk + ingest
        chunks, metas = chunk_logs(text, source_file=fname)
        index_log_chunks(chunks, metas)
        print(f"✅ Ingested {len(chunks)} chunks from {fname}")

if __name__ == "__main__":
    main()
