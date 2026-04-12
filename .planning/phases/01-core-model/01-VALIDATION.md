---
phase: 1
slug: core-model
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-12
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pytest.ini` or `pyproject.toml` |
| **Quick run command** | `pytest tests/ -x` |
| **Full suite command** | `pytest tests/` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/ -x`
- **After every plan wave:** Run `pytest tests/`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 01-01-01 | 01-01 | 0 | CORE-01 | T-01-01 | Pydantic Field(...) enforces required fields | unit | `pytest tests/models/test_device.py::test_required_fields -x` | ❌ W0 | ⬜ pending |
| 01-01-02 | 01-01 | 0 | CORE-02 | T-01-01 | from_dict() parses nested dictionary | unit | `pytest tests/models/test_device.py::test_from_dict -x` | ❌ W0 | ⬜ pending |
| 01-01-03 | 01-01 | 0 | CORE-04 | T-01-01 | Pydantic validation enforces type correctness | unit | `pytest tests/models/test_device.py::test_type_validation -x` | ❌ W0 | ⬜ pending |
| 01-01-04 | 01-01 | 0 | DEV-01 | T-01-01 | Device supports serial, asset_tag | unit | `pytest tests/models/test_device.py::test_optional_fields -x` | ❌ W0 | ⬜ pending |
| 01-01-05 | 01-01 | 0 | DEV-02 | T-01-01 | Device supports device_type with manufacturer | unit | `pytest tests/models/test_device.py::test_device_type -x` | ❌ W0 | ⬜ pending |
| 01-01-06 | 01-01 | 0 | DEV-03 | T-01-01 | Device supports role assignment | unit | `pytest tests/models/test_device.py::test_role -x` | ❌ W0 | ⬜ pending |
| 01-01-07 | 01-01 | 0 | DEV-04 | T-01-01 | Device supports platform specification | unit | `pytest tests/models/test_device.py::test_platform -x` | ❌ W0 | ⬜ pending |
| 01-01-08 | 01-01 | 0 | DEV-05 | T-01-01 | Device supports site assignment | unit | `pytest tests/models/test_device.py::test_site -x` | ❌ W0 | ⬜ pending |
| 01-01-09 | 01-01 | 0 | DEV-06 | T-01-01 | Device supports status field | unit | `pytest tests/models/test_device.py::test_status -x` | ❌ W0 | ⬜ pending |
| 01-01-10 | 01-01 | 0 | DEV-07 | T-01-01 | Device supports custom_fields | unit | `pytest tests/models/test_device.py::test_custom_fields -x` | ❌ W0 | ⬜ pending |
| 01-01-11 | 01-01 | 0 | DEV-08 | T-01-01 | Device supports business_unit mapping | unit | `pytest tests/models/test_device.py::test_business_unit -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/models/test_device.py` — stubs for CORE-01, CORE-02, CORE-04, DEV-01 through DEV-08
- [ ] `tests/conftest.py` — shared fixtures for models
- [ ] `pip install --break-system-packages pytest` — if no framework detected

*If none: "Existing infrastructure covers all phase requirements."*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Status field validation | DEV-06 | Needs user confirmation on valid values | Manually verify error raised for invalid status |

*If none: "All phase behaviors have automated verification."*

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
