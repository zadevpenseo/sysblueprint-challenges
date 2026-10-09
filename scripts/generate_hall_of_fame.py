#!/usr/bin/env python3
"""
SysBlueprint Challenges - Automated Hall of Fame Generator
Memindai pengajuan solusi, mengevaluasi rubrik, dan menghasilkan data/hall_of_fame.json
untuk pengajuan berpredikat 'Distinction' (Skor >= 90).
"""

import os
import sys
import json
from pathlib import Path

# Impor evaluator lokal
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))
from evaluate_submission import run_evaluation


def build_hall_of_fame():
    repo_root = SCRIPT_DIR.parent
    submissions_dir = repo_root / "submissions"
    data_dir = repo_root / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_file = data_dir / "hall_of_fame.json"

    if not submissions_dir.exists():
        print(f"Direktori submissions {submissions_dir} belum ada. Menulis berkas kosong.")
        output_file.write_text("[]\n", encoding="utf-8")
        return

    verified_talents = []

    for sub_dir in sorted(submissions_dir.iterdir()):
        if not sub_dir.is_dir() or sub_dir.name.upper() == "TEMPLATE":
            continue

        meta_file = sub_dir / "metadata.json"
        if not meta_file.exists():
            print(f"Lewati {sub_dir.name}: Berkas metadata.json tidak ditemukan.")
            continue

        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception as exc:
            print(f"Galat membaca metadata {sub_dir.name}: {exc}")
            continue

        eval_result = run_evaluation(sub_dir)
        total_score = eval_result["total_score"]
        predicate = eval_result["predicate"]

        print(f"Evaluasi {sub_dir.name}: Skor {total_score}/100 ({predicate})")

        # Syarat masuk Hall of Fame: Predikat Distinction (Skor >= 90)
        if total_score >= 90:
            username = meta.get("github_username", sub_dir.name)
            challenge_id = meta.get("challenge_id", "CHALLENGE-01")
            
            highlights = [
                f"{total_score}/100 Skor Rubrik Otomatis",
                "Verified Architecture Solution",
                "Deterministic CI Passed"
            ]

            entry = {
                "id": f"sub_{username.replace('-', '_')}_{challenge_id.lower().replace('-', '_')}",
                "author": meta.get("author_name", username),
                "githubUsername": username,
                "avatarUrl": meta.get("avatar_url", f"https://avatars.githubusercontent.com/{username}?v=4"),
                "bio": meta.get("bio", "Software Engineer & System Architect"),
                "challengeId": challenge_id,
                "challengeTitle": meta.get("challenge_title", "Architecture Challenge"),
                "score": total_score,
                "predicate": predicate,
                "submissionDate": meta.get("created_at", "2026-10-09"),
                "submissionUrl": f"https://github.com/zadevpenseo/sysblueprint-challenges/tree/main/submissions/{sub_dir.name}",
                "linkedinUrl": meta.get("linkedin_url", f"https://github.com/{username}"),
                "summary": meta.get("summary", "Solusi arsitektur terverifikasi memenuhi standar integritas data dan konkurensi."),
                "presetKey": meta.get("preset_key", "ecommerce_flashsale"),
                "keyHighlights": highlights
            }
            verified_talents.append(entry)

    # Urutkan berdasarkan skor tertinggi, lalu nama
    verified_talents.sort(key=lambda x: x["score"], reverse=True)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(verified_talents, f, indent=2, ensure_ascii=False)

    print("=" * 60)
    print(f"HALL OF FAME SELESAI DIBUAT: {len(verified_talents)} Talenta Terdaftar")
    print(f"Berkas Disimpan: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    build_hall_of_fame()
