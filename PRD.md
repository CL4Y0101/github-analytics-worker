# Product Requirements Document
## GitHub Analytics Worker

**Version:** 1.0  
**Status:** Draft  
**Platform:** GitHub + GitHub Actions  
**Language:** Python 3.12+  
**Output:** JSON, CSV, Markdown Dashboard

---

## 1. Product Overview

GitHub Analytics Worker adalah automated data-processing system yang berjalan secara terjadwal menggunakan GitHub Actions.

Setiap hari, worker menjalankan **50–100 analytics jobs** untuk menghasilkan dataset terstruktur mengenai aktivitas dan metadata repository.

Hasil pemrosesan disimpan dalam format:

- JSON
- CSV
- Markdown dashboard

Worker kemudian melakukan commit terhadap artifact yang berubah dan melakukan push ke repository.

### High-Level Flow

```text
GitHub Actions
      ↓
Python Worker
      ↓
50–100 Analytics Jobs
      ↓
Data Processing
      ↓
JSON + CSV
      ↓
Dashboard Generator
      ↓
Git Commit
      ↓
GitHub Repository
```

---

# 2. Goals

### Primary Goals

1. Membuat automated analytics worker berbasis Python.
2. Menjalankan 50–100 analytics jobs setiap hari.
3. Menghasilkan dataset yang reproducible dan terstruktur.
4. Menyimpan hasil dalam JSON dan CSV.
5. Menghasilkan dashboard Markdown otomatis.
6. Menjalankan worker secara otomatis menggunakan GitHub Actions.
7. Menyediakan manual workflow trigger untuk testing.
8. Menjaga struktur repository sederhana dan mudah dikembangkan.

### Secondary Goals

- Memiliki logging yang jelas.
- Memiliki error handling.
- Memiliki statistik performa worker.
- Menghindari dependency eksternal sebanyak mungkin.
- Memastikan workflow idempotent untuk tanggal yang sama.

---

# 3. Non-Goals

Project ini **tidak bertujuan** untuk:

- membuat artificial GitHub contribution activity;
- membuat commit kosong;
- melakukan backdated commit;
- melakukan spam push;
- memanipulasi contribution graph;
- membuat aktivitas palsu yang seolah-olah merupakan pekerjaan development.

Jumlah **50–100 jobs/day** mengacu pada pekerjaan/data-processing yang dijalankan worker, bukan jumlah commit.

---

# 4. Target Users

### Primary User

Developer yang ingin memiliki automated GitHub analytics/data-processing pipeline.

### Secondary User

Recruiter atau developer lain yang melihat repository sebagai portfolio project.

Repository harus dapat menjelaskan dengan jelas:

> Worker melakukan automated data processing menggunakan Python dan GitHub Actions.

---

# 5. Core Features

## 5.1 Daily Worker

Worker dijalankan satu kali setiap hari.

Jumlah job:

```text
minimum = 50
maximum = 100
```

Jumlah job ditentukan secara deterministic berdasarkan tanggal.

Contoh:

```text
2026-10-02 → 73 jobs
2026-10-03 → 91 jobs
2026-10-04 → 58 jobs
```

Tujuannya agar rerun pada tanggal yang sama tidak menghasilkan jumlah job berbeda.

---

# 6. Analytics Job

Setiap job memiliki:

```json
{
  "job_id": 1,
  "metric": "commits",
  "value": 125,
  "status": "success",
  "duration_ms": 421
}
```

Minimum fields:

| Field | Type | Description |
|---|---|---|
| `job_id` | integer | ID job |
| `metric` | string | Jenis metric |
| `value` | number | Nilai hasil analytics |
| `status` | string | Status job |
| `duration_ms` | integer | Durasi pemrosesan |

Metric awal:

```text
commits
pull_requests
issues
stars
forks
workflow_runs
```

Arsitektur harus memungkinkan penambahan metric baru tanpa mengubah keseluruhan worker.

---

# 7. Data Processing

Worker harus:

1. Generate/load source data.
2. Process analytics job.
3. Validate result.
4. Store result.
5. Calculate aggregate statistics.
6. Generate dashboard.

Setiap job harus menghasilkan result yang dapat ditelusuri menggunakan `job_id`.

---

# 8. JSON Output

Lokasi:

```text
data/json/
```

Format filename:

```text
YYYY-MM-DD.json
```

Contoh:

```text
data/json/2026-10-02.json
```

Format:

```json
{
  "generated_at": "2026-10-02T20:00:00Z",
  "jobs": 73,
  "successful_jobs": 71,
  "success_rate": 97.26,
  "average_duration_ms": 421.3,
  "results": [
    {
      "job_id": 1,
      "metric": "commits",
      "value": 125,
      "status": "success",
      "duration_ms": 421
    }
  ]
}
```

---

# 9. CSV Output

Lokasi:

```text
data/csv/
```

Filename:

```text
YYYY-MM-DD.csv
```

Example:

```text
data/csv/2026-10-02.csv
```

Columns:

```text
job_id
metric
value
status
duration_ms
```

CSV harus dapat dibuka langsung menggunakan Excel, Google Sheets, atau pandas.

---

# 10. Dashboard

File:

```text
DASHBOARD.md
```

Dashboard diperbarui setiap workflow berhasil dijalankan.

Minimal menampilkan:

### Daily Statistics

```text
Jobs processed
Successful jobs
Failed/warning jobs
Success rate
Average duration
```

### Metric Summary

Contoh:

| Metric | Total |
|---|---:|
| Commits | 1,204 |
| Issues | 642 |
| Pull Requests | 381 |
| Stars | 92 |
| Forks | 47 |

### Latest Run

```text
Last run:
2026-10-02 20:00 UTC

Jobs:
73

Success rate:
97.26%

Average duration:
421 ms
```

---

# 11. Repository Structure

Final repository:

```text
github-analytics-worker/
│
├── .github/
│   └── workflows/
│       └── daily.yml
│
├── data/
│   ├── json/
│   │   └── YYYY-MM-DD.json
│   │
│   └── csv/
│       └── YYYY-MM-DD.csv
│
├── src/
│   ├── __init__.py
│   ├── worker.py
│   ├── analytics.py
│   ├── models.py
│   └── dashboard.py
│
├── tests/
│   ├── test_worker.py
│   ├── test_analytics.py
│   └── test_dashboard.py
│
├── DASHBOARD.md
├── README.md
├── requirements.txt
├── pyproject.toml
└── .gitignore
```

---

# 12. Python Architecture

Pisahkan responsibility.

### `models.py`

Berisi data model.

```text
JobResult
DailyReport
```

### `analytics.py`

Berisi logic analytics.

```text
run_job()
calculate_statistics()
aggregate_metrics()
```

### `dashboard.py`

Berisi dashboard generation.

```text
generate_dashboard()
```

### `worker.py`

Sebagai entry point.

```text
main()
```

Flow:

```text
worker.py
    ↓
analytics.py
    ↓
models.py
    ↓
dashboard.py
```

---

# 13. GitHub Actions

Workflow:

```text
.github/workflows/daily.yml
```

Trigger utama:

```yaml
schedule:
  - cron: "0 20 * * *"
```

Artinya sekitar:

```text
03:00 WIB
```

Workflow juga harus mendukung:

```yaml
workflow_dispatch:
```

sehingga developer dapat menjalankan worker secara manual.

---

# 14. GitHub Actions Flow

```text
Checkout repository
        ↓
Setup Python 3.12
        ↓
Install dependencies
        ↓
Run tests
        ↓
Run worker
        ↓
Generate JSON
        ↓
Generate CSV
        ↓
Generate dashboard
        ↓
git diff
        ↓
Commit changes
        ↓
Push
```

Jika tidak ada perubahan:

```text
No changes → no commit
```

---

# 15. Git Commit Convention

Commit otomatis menggunakan format:

```text
chore: daily analytics YYYY-MM-DD
```

Contoh:

```text
chore: daily analytics 2026-10-02
```

Jangan membuat commit jika tidak ada perubahan.

---

# 16. Error Handling

Jika satu job gagal:

```text
Job 37 → warning
```

worker **tidak langsung menghentikan seluruh pipeline**.

Worker tetap melanjutkan:

```text
Job 38
Job 39
...
Job 73
```

Kemudian dashboard mencatat:

```text
Total jobs: 73
Successful: 71
Warning: 2
```

Namun jika terjadi error fatal seperti:

```text
cannot write output directory
invalid configuration
corrupted source data
```

worker harus exit dengan non-zero status agar GitHub Actions menandai workflow sebagai failed.

---

# 17. Testing

Minimal test coverage:

### Worker

- menghasilkan 50–100 jobs;
- job ID unik;
- semua result memiliki required fields.

### Analytics

- aggregate calculation benar;
- success rate benar;
- average duration benar.

### Output

- JSON valid;
- CSV memiliki header;
- dashboard berhasil dibuat.

Command:

```bash
pytest
```

---

# 18. Local Development

Developer dapat menjalankan:

```bash
python -m src.worker
```

atau:

```bash
python src/worker.py
```

Output:

```text
Processed 73 analytics jobs.
Generated:
data/json/2026-10-02.json
data/csv/2026-10-02.csv
DASHBOARD.md
```

---

# 19. Dependencies

Gunakan Python standard library sebanyak mungkin.

Target:

```text
Python 3.12+
```

External dependencies hanya ditambahkan jika memang diperlukan.

Initial project:

```text
requirements.txt
```

dapat kosong.

---

# 20. Data Retention

Default:

```text
1 JSON file/day
1 CSV file/day
```

Jangan overwrite data tanggal sebelumnya.

Contoh:

```text
data/json/
├── 2026-10-01.json
├── 2026-10-02.json
├── 2026-10-03.json
└── ...
```

---

# 21. Reproducibility

Worker menggunakan deterministic seed berdasarkan tanggal.

Contoh:

```text
seed = "2026-10-02"
```

Dengan demikian workflow yang dijalankan dua kali pada tanggal yang sama menghasilkan dataset yang konsisten.

Namun timestamp eksekusi tetap dicatat secara terpisah.

---

# 22. Security

Tidak boleh menyimpan:

```text
GitHub token
SSH private key
password
API secret
```

di repository.

Jika API GitHub nantinya digunakan, credential harus disimpan melalui:

```text
GitHub Actions Secrets
```

atau:

```text
GitHub Actions Variables
```

---

# 23. Future GitHub API Integration

Versi berikutnya dapat mengganti synthetic analytics dengan data GitHub API nyata.

Contoh:

```text
GitHub API
    ↓
Repository metadata
    ↓
Commits
Issues
Pull Requests
Stars
Forks
Workflow Runs
    ↓
Analytics Worker
    ↓
JSON / CSV
    ↓
Dashboard
```

Target repository dapat dikonfigurasi melalui environment variable:

```text
GITHUB_REPOSITORY
```

atau configuration file.

---

# 24. Success Criteria

Project dianggap berhasil apabila:

- [ ] Worker dapat berjalan secara lokal.
- [ ] Worker menghasilkan 50–100 jobs.
- [ ] JSON berhasil dibuat.
- [ ] CSV berhasil dibuat.
- [ ] Dashboard berhasil dibuat.
- [ ] Tests berhasil.
- [ ] GitHub Actions berhasil berjalan.
- [ ] Scheduled workflow berjalan setiap hari.
- [ ] Manual workflow dapat dijalankan.
- [ ] Workflow otomatis commit ketika artifact berubah.
- [ ] Workflow tidak membuat commit jika tidak ada perubahan.
- [ ] Tidak ada credential yang disimpan di repository.
- [ ] Repository dapat dipahami developer lain tanpa penjelasan tambahan.

---

# 25. Definition of Done

MVP dianggap selesai ketika repository dapat melakukan:

```text
git clone
    ↓
python -m src.worker
    ↓
50–100 jobs
    ↓
JSON
CSV
Dashboard
    ↓
git commit
git push
```

dan:

```text
GitHub Actions
    ↓
Daily schedule
    ↓
Run worker
    ↓
Generate artifacts
    ↓
Update dashboard
    ↓
Commit changes
```

tanpa intervensi manual.

---

# 26. Future Improvements

Setelah MVP stabil, fitur berikut dapat ditambahkan:

1. GitHub REST API integration.
2. Repository comparison.
3. Weekly analytics.
4. Monthly analytics.
5. Trend calculation.
6. Historical dashboard.
7. GitHub Pages dashboard.
8. Chart generation.
9. SQLite storage.
10. Failure notifications.
11. Job retry mechanism.
12. Parallel job execution.
13. Performance benchmarking.
14. Docker support.
15. Multi-repository analytics.

---

## Final Product Vision

Project akhirnya bukan sekadar automation script, tetapi sebuah mini data pipeline:

```text
                 ┌─────────────────┐
                 │ GitHub Actions  │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Python Worker   │
                 └────────┬────────┘
                          │
                    50–100 Jobs
                          │
                          ▼
                 ┌─────────────────┐
                 │ Analytics Layer │
                 └────────┬────────┘
                          │
                ┌─────────┴─────────┐
                ▼                   ▼
             JSON                  CSV
                │                   │
                └─────────┬─────────┘
                          ▼
                 ┌─────────────────┐
                 │ Markdown        │
                 │ Dashboard       │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Git Repository  │
                 └─────────────────┘
```

Fokus utamanya adalah **automation + data processing + reproducibility + CI/CD**, sehingga project ini punya nilai teknis yang jelas sebagai portfolio.