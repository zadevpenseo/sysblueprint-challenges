# SysBlueprint Architecture Challenges

Tantangan rekayasa arsitektur sistem dan perancangan basis data terstandar dari [SysBlueprint Studio](https://sysblueprint.blogspot.com/). Repositori ini memuat *Problem Briefs*, rubrik penilaian objektif, dan alur evaluasi otomatis (*Automated Rubric Grader*) untuk menguji kompetensi teknis pembelajar dan praktisi.

---

## Mekanisme Tantangan Arsitektur

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  PILIH TANTANGAN│  ───> │ FORK & KERJAKAN │  ───> │ KIRIMKAN PR     │  ───> │ EVALUASI OTOMATIS│
│  Baca Brief &   │       │ Susun DDL, ERD, │       │ Ajukan solusi   │       │ Bot menguji     │
│  Batasan Sistem │       │ Kamus Data, ADR │       │ via GitHub PR   │       │ skor 0-100      │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

1. **Pilih Tantangan**: Telusuri folder `challenges/` dan baca dokumen `PROBLEM_BRIEF.md` serta `RUBRIC.md`.
2. **Fork & Kerjakan**: Fork repositori ini atau gunakan template studi kasus [sysblueprint-cases](https://github.com/zadevpenseo/sysblueprint-cases).
3. **Kirimkan Solusi**: Ajukan Pull Request ke repositori ini dengan melampirkan berkas DDL SQL, diagram relasi, dan analisis keputusan arsitektur (ADR).
4. **Evaluasi Otomatis & Showcase**: Bot GitHub Actions akan memeriksa kelengkapan sintaks dan kepatuhan rubrik. Solusi dengan predikat **Distinction (Nilai 90+)** akan ditampilkan di [Showcase SysBlueprint Studio](https://sysblueprint.blogspot.com/p/showcase.html).

---

## Tingkat Predikat Penilaian

| Rentang Skor | Predikat | Kriteria Kelulusan |
|:---:|:---:|:---|
| **90 s.d. 100** | **Distinction** | DDL valid, 100% kepatuhan PK/FK terurut topologis, kamus data lengkap, ADR komprehensif, dan lolos uji kasus batas (*edge cases*). |
| **75 s.d. 89** | **Merit** | DDL valid, relasi lengkap, kamus data terisi, dan terdapat analisis arsitektur dasar. |
| **60 s.d. 74** | **Pass** | DDL dapat dieksekusi, struktur tabel utama terpenuhi, namun dokumentasi masih minimal. |
| **< 60** | **Needs Revision** | Terdapat galat sintaks SQL, relasi siklik yang merusak, atau berkas wajib tidak ditemukan. |

---

## Lisensi

Materi tantangan dilisensikan di bawah [MIT License](LICENSE).
