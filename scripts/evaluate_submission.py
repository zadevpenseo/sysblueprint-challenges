#!/usr/bin/env python3
"""
SysBlueprint Architecture Challenges - Automated Rubric Evaluator
Mengevaluasi pengajuan solusi arsitektur sistem berdasarkan rubrik objektif (Skor 0-100).
"""

import sys
import os
import re
import json
import sqlite3
import argparse
from pathlib import Path


def evaluate_sql_schema(schema_file: Path) -> tuple[int, list[str]]:
    """Evaluasi kualitas DDL SQL dan batasan integritas (Maksimal 35 Poin)."""
    score = 0
    feedback = []
    
    if not schema_file.exists():
        feedback.append("GAGAL: Berkas schema.sql tidak ditemukan.")
        return 0, feedback
        
    sql_text = schema_file.read_text(encoding="utf-8")
    
    # 1. Syntax & Execution check via SQLite memory engine
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Clean dialect specific tokens for in-memory testing if needed
        sqlite_compatible_sql = re.sub(r'TIMESTAMPTZ', 'TIMESTAMP', sql_text, flags=re.IGNORECASE)
        sqlite_compatible_sql = re.sub(r'TIMESTAMP WITH TIME ZONE', 'TIMESTAMP', sqlite_compatible_sql, flags=re.IGNORECASE)
        
        conn.executescript(sqlite_compatible_sql)
        score += 10
        feedback.append("LULUS (10/10): DDL SQL tervalidasi dan berhasil dieksekusi.")
    except Exception as exc:
        feedback.append(f"PERINGATAN (4/10): Galat eksekusi basis data: {exc}")
        score += 4

    # 2. Check for Foreign Key Relationships (DAG)
    fk_count = len(re.findall(r'FOREIGN\s+KEY', sql_text, re.IGNORECASE)) + len(re.findall(r'REFERENCES\s+\w+', sql_text, re.IGNORECASE))
    if fk_count >= 2:
        score += 10
        feedback.append(f"LULUS (10/10): Integritas relasional terdeteksi ({fk_count} relasi kunci asing).")
    elif fk_count == 1:
        score += 5
        feedback.append("PERINGATAN (5/10): Relasi kunci asing terdeteksi minimal.")
    else:
        feedback.append("GAGAL (0/10): Ketiadaan relasi foreign key pada skema.")

    # 3. Check for Stock Protection Constraints
    has_check = bool(re.search(r'CHECK\s*\(', sql_text, re.IGNORECASE))
    has_protection = bool(re.search(r'(physical|allocated|reserved|quantity|stock)', sql_text, re.IGNORECASE))
    if has_check and has_protection:
        score += 10
        feedback.append("LULUS (10/10): Constraint proteksi kuota stok terdefinisi secara eksplisit.")
    elif has_check:
        score += 6
        feedback.append("PERINGATAN (6/10): Ditemukan check constraint namun belum spesifik melindungi stok.")
    else:
        feedback.append("GAGAL (0/10): Tidak ditemukan check constraint proteksi stok.")

    # 4. Check for Performance Indexes
    index_count = len(re.findall(r'CREATE\s+INDEX', sql_text, re.IGNORECASE))
    if index_count >= 2:
        score += 5
        feedback.append(f"LULUS (5/5): Ditemukan {index_count} indeks komposit penunjang kueri performa.")
    elif index_count == 1:
        score += 3
        feedback.append("PERINGATAN (3/5): Hanya ditemukan 1 indeks performa.")
    else:
        feedback.append("GAGAL (0/5): Tidak ditemukan indeks kueri performa.")

    return score, feedback


def evaluate_concurrency_model(schema_file: Path) -> tuple[int, list[str]]:
    """Evaluasi penanganan konkurensi dan audit trail (Maksimal 30 Poin)."""
    score = 0
    feedback = []
    
    if not schema_file.exists():
        return 0, ["GAGAL: Berkas schema.sql tidak ditemukan."]
        
    sql_text = schema_file.read_text(encoding="utf-8")

    # 1. State machine columns
    has_status = bool(re.search(r'status\s+VARCHAR', sql_text, re.IGNORECASE))
    if has_status:
        score += 10
        feedback.append("LULUS (10/10): Status machine terdeteksi untuk transisi status pesanan/reservasi.")
    else:
        feedback.append("GAGAL (0/10): Kolom status transaksi tidak terdeteksi.")

    # 2. Time-bound expiry mechanism
    has_expires = bool(re.search(r'(expires_at|expiry|expired_at)', sql_text, re.IGNORECASE))
    if has_expires:
        score += 10
        feedback.append("LULUS (10/10): Mekanisme penanda kedaluwarsa waktu (expires_at) terdefinisi.")
    else:
        feedback.append("GAGAL (0/10): Tidak ada atribut penanda kedaluwarsa waktu reservasi.")

    # 3. Immutable audit ledger
    has_ledger = bool(re.search(r'(mutation|ledger|log|history)', sql_text, re.IGNORECASE))
    if has_ledger:
        score += 10
        feedback.append("LULUS (10/10): Tabel buku besar mutasi inventaris terdeteksi.")
    else:
        feedback.append("GAGAL (0/10): Ketiadaan tabel audit trail mutasi stok.")

    return score, feedback


def evaluate_documentation(erd_file: Path, dict_file: Path) -> tuple[int, list[str]]:
    """Evaluasi diagram ERD dan kamus data (Maksimal 15 Poin)."""
    score = 0
    feedback = []

    # ERD Check (8 Poin)
    if erd_file.exists():
        erd_content = erd_file.read_text(encoding="utf-8")
        if "erDiagram" in erd_content and len(erd_content.splitlines()) >= 10:
            score += 8
            feedback.append("LULUS (8/8): Diagram Mermaid ERD valid dan komprehensif.")
        elif "erDiagram" in erd_content:
            score += 4
            feedback.append("PERINGATAN (4/8): Diagram Mermaid ERD masih terlalu ringkas.")
        else:
            feedback.append("GAGAL (0/8): Berkas ERD.md tidak memuat sintaks Mermaid erDiagram.")
    else:
        feedback.append("GAGAL (0/8): Berkas ERD.md tidak ditemukan.")

    # Data Dictionary Check (7 Poin)
    if dict_file.exists():
        dict_content = dict_file.read_text(encoding="utf-8")
        table_count = dict_content.count("|")
        if table_count >= 15:
            score += 7
            feedback.append("LULUS (7/7): Kamus data lengkap dengan tabulasi atribut dan nullability.")
        elif table_count >= 5:
            score += 4
            feedback.append("PERINGATAN (4/7): Kamus data terdeteksi namun atribut belum lengkap.")
        else:
            feedback.append("GAGAL (0/7): Kamus data tidak memiliki format tabel terstruktur.")
    else:
        feedback.append("GAGAL (0/7): Berkas DATA_DICTIONARY.md tidak ditemukan.")

    return score, feedback


def evaluate_adr(target_dir: Path) -> tuple[int, list[str]]:
    """Evaluasi Architecture Decision Record (Maksimal 20 Poin)."""
    score = 0
    feedback = []

    adr_files = list(target_dir.glob("ADR*.md"))
    if not adr_files:
        feedback.append("GAGAL (0/20): Dokumen ADR tidak ditemukan.")
        return 0, feedback

    adr_text = adr_files[0].read_text(encoding="utf-8")

    # Context analysis (5 Poin)
    if "konteks" in adr_text.lower() or "context" in adr_text.lower():
        score += 5
        feedback.append("LULUS (5/5): Konteks dan latar belakang permasalahan terurai jelas.")
    else:
        feedback.append("GAGAL (0/5): Bagian konteks masalah tidak teridentifikasi.")

    # Alternatives comparison (10 Poin)
    has_alternatives = bool(re.search(r'(opsi|alternatif|option|pessimistic|optimistic)', adr_text, re.IGNORECASE))
    has_comparison = len(re.findall(r'(kelebihan|kekurangan|pro|con|trade-off)', adr_text, re.IGNORECASE)) >= 2
    if has_alternatives and has_comparison:
        score += 10
        feedback.append("LULUS (10/10): Terdapat perbandingan mendalam antarpilihan arsitektur dan trade-off.")
    elif has_alternatives:
        score += 5
        feedback.append("PERINGATAN (5/10): Pilihan alternatif dicantumkan namun evaluasi trade-off minim.")
    else:
        feedback.append("GAGAL (0/10): Tidak ada perbandingan alternatif solusi arsitektur.")

    # Decision justification (5 Poin)
    if "keputusan" in adr_text.lower() or "decision" in adr_text.lower():
        score += 5
        feedback.append("LULUS (5/5): Justifikasi keputusan arsitektur dinyatakan secara tegas.")
    else:
        feedback.append("GAGAL (0/5): Bagian keputusan arsitektur tidak ditemukan.")

    return score, feedback


def run_evaluation(target_dir: Path) -> dict:
    """Menjalankan seluruh pipa evaluasi rubrik."""
    schema_path = target_dir / "schema.sql"
    erd_path = target_dir / "ERD.md"
    dict_path = target_dir / "DATA_DICTIONARY.md"

    sql_score, sql_fb = evaluate_sql_schema(schema_path)
    conc_score, conc_fb = evaluate_concurrency_model(schema_path)
    doc_score, doc_fb = evaluate_documentation(erd_path, dict_path)
    adr_score, adr_fb = evaluate_adr(target_dir)

    total_score = sql_score + conc_score + doc_score + adr_score

    if total_score >= 90:
        predicate = "Distinction"
    elif total_score >= 75:
        predicate = "Merit"
    elif total_score >= 60:
        predicate = "Pass"
    else:
        predicate = "Needs Revision"

    return {
        "target_directory": str(target_dir),
        "total_score": total_score,
        "predicate": predicate,
        "breakdown": {
            "ddl_and_integrity": {"score": sql_score, "max": 35, "feedback": sql_fb},
            "concurrency_and_audit": {"score": conc_score, "max": 30, "feedback": conc_fb},
            "documentation": {"score": doc_score, "max": 15, "feedback": doc_fb},
            "adr_analysis": {"score": adr_score, "max": 20, "feedback": adr_fb},
        }
    }


def main():
    parser = argparse.ArgumentParser(description="SysBlueprint Automated Rubric Evaluator")
    parser.add_argument("target", type=str, help="Path ke folder solusi yang dievaluasi")
    parser.add_argument("--json", action="store_true", help="Keluarkan hasil dalam format JSON")
    args = parser.parse_args()

    target_path = Path(args.target).resolve()
    if not target_path.exists():
        print(f"Error: Direktori target '{target_path}' tidak ditemukan.", file=sys.stderr)
        sys.exit(1)

    result = run_evaluation(target_path)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print(f" HASIL EVALUASI TANTANGAN ARSITEKTUR: {result['predicate'].upper()} ")
        print(f" Skor Akhir: {result['total_score']} / 100")
        print("=" * 60)
        for category, data in result["breakdown"].items():
            print(f"\n[{category.upper()}] - {data['score']} / {data['max']} Poin:")
            for item in data["feedback"]:
                print(f"  • {item}")
        print("\n" + "=" * 60)

    if result["total_score"] < 60:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
