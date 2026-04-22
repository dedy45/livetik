# 🤖 Kiro IDE Guide - Livetik Development

> Panduan khusus untuk development livetik menggunakan **Kiro IDE** (bukan VSCode).  
> Kiro adalah AI-powered development environment dengan workflow dan tools yang berbeda.

---

## 1. Perbedaan Kiro vs VSCode

| Aspek | VSCode | Kiro IDE |
|-------|--------|----------|
| **Nature** | Traditional code editor | AI-powered development environment |
| **Workflow** | Manual coding + AI assist | AI-first with human oversight |
| **File Operations** | Manual edit via editor | AI tools: `fsWrite`, `strReplace`, `readFile` |
| **Terminal** | Integrated terminal | `executePwsh` tool (PowerShell) |
| **Git** | Built-in Git UI | Command-line via `executePwsh` |
| **Search** | Ctrl+F, Ctrl+Shift+F | `grepSearch`, `fileSearch` tools |
| **Debugging** | Breakpoints, debugger | Log analysis + health checks |
| **Extensions** | VSCode extensions | Kiro Powers (MCP servers) |
| **Context** | Open files | Explicit file reads via tools |

---

## 2. Kiro Development Workflow

### 2a. Typical Development Session

```
1. User Request
   ↓
2. Kiro reads relevant docs (ARCHITECTURE.md, ERROR_HANDLING.md)
   ↓
3. Kiro analyzes codebase (readFile, grepSearch)
   ↓
4. Kiro makes changes (fsWrite, strReplace)
   ↓
5. Kiro runs tests/checks (executePwsh)
   ↓
6. Kiro commits (executePwsh git commands)
```

### 2b. File Operations

**VSCode:**
```
1. Open file in editor
2. Edit manually
3. Save (Ctrl+S)
```

**Kiro:**
```
1. readFile("path/to/file.py")
2. strReplace(oldStr, newStr) or fsWrite(path, content)
3. Auto-saved immediately
```

### 2c. Search Operations

**VSCode:**
```
Ctrl+Shift+F → Search in files
Ctrl+P → Quick open file
```

**Kiro:**
```
grepSearch(query="function_name", includePattern="**/*.py")
fileSearch(query="adapter")
```

### 2d. Terminal Commands

**VSCode:**
```
Terminal → Type command → Enter
```

**Kiro:**
```
executePwsh(command="python -m pytest", cwd="apps/worker")
```

---

## 3. Kiro-Specific Best Practices

### 3a. Always Read Docs First

Kiro harus membaca dokumentasi sebelum membuat perubahan:

```
✅ GOOD:
1. readFile("docs/ARCHITECTURE.md")
2. readFile("docs/ERROR_HANDLING.md")
3. Understand system design
4. Make informed changes

❌ BAD:
1. Langsung edit file tanpa context
2. Guess implementation details
3. Ignore existing patterns
```

### 3b. Use Health Checks

Kiro punya script health check yang komprehensif:

```bash
# Before making changes
scripts\health-check.bat

# After making changes
scripts\health-check.bat

# Monitor runtime
scripts\monitor-runtime.bat
```

### 3c. Follow Error Handling Matrix

Setiap error harus mapped ke `docs/ERROR_HANDLING.md`:

```python
# ✅ GOOD: Error dengan code dan recovery
raise TikTokError(
    code="TIKTOK_DISCONNECT",
    message="WebSocket dropped",
    recovery="Auto-reconnect 3× exp backoff"
)

# ❌ BAD: Generic error
raise Exception("Connection failed")
```

### 3d. Respect Architecture Boundaries

Berdasarkan `docs/ARCHITECTURE.md`:

```
adapters/     → External integrations (TikTok, LLM, TTS, OBS)
core/         → Business logic (persona, guardrail, queue)
ipc/          → Inter-process communication (WebSocket, REST)
telemetry/    → Logging, cost tracking
```

**Don't mix concerns:**
```python
# ❌ BAD: LLM logic in TikTok adapter
# adapters/tiktok.py
def on_comment(comment):
    reply = call_llm(comment)  # WRONG!

# ✅ GOOD: Emit event, let queue handle
# adapters/tiktok.py
def on_comment(comment):
    emit_event(CommentReceived(comment))
```

---

## 4. Kiro Tools Reference

### 4a. File Operations

| Tool | Purpose | Example |
|------|---------|---------|
| `readFile` | Read file content | `readFile("apps/worker/src/banghack/adapters/tiktok.py")` |
| `readMultipleFiles` | Read multiple files | `readMultipleFiles(["file1.py", "file2.py"])` |
| `fsWrite` | Create/overwrite file | `fsWrite("new_file.py", content)` |
| `strReplace` | Replace text in file | `strReplace(path, oldStr, newStr)` |
| `deleteFile` | Delete file | `deleteFile("temp.txt")` |
| `listDirectory` | List directory contents | `listDirectory("apps/worker", depth=2)` |

### 4b. Search Operations

| Tool | Purpose | Example |
|------|---------|---------|
| `grepSearch` | Search text in files | `grepSearch(query="def.*comment", includePattern="**/*.py")` |
| `fileSearch` | Find files by name | `fileSearch(query="tiktok")` |

### 4c. Shell Operations

| Tool | Purpose | Example |
|------|---------|---------|
| `executePwsh` | Run PowerShell command | `executePwsh(command="python -m pytest", cwd="apps/worker")` |
| `controlPwshProcess` | Start/stop background process | `controlPwshProcess(action="start", command="pnpm dev")` |

### 4d. Code Operations

| Tool | Purpose | Example |
|------|---------|---------|
| `readCode` | Read code with AST | `readCode("apps/worker/src/banghack/core/queue.py")` |
| `getDiagnostics` | Get compile errors | `getDiagnostics(["apps/controller/src/routes/+page.svelte"])` |
| `semanticRename` | Rename symbol | `semanticRename(path, line, char, oldName, newName)` |

---

## 5. Livetik-Specific Workflows

### 5a. Adding New Error Type

Based on `docs/ERROR_HANDLING.md`:

```
1. Read ERROR_HANDLING.md
2. Add error to matrix:
   - Code: DOMAIN_SPECIFIC
   - Severity: High/Medium/Low
   - Recovery strategy
   - File pertama dibuka
3. Implement in code:
   - Define error class
   - Add to error taxonomy
   - Update health check script
4. Update docs
5. Test with health-check.bat
```

### 5b. Adding New Adapter

Based on `docs/ARCHITECTURE.md`:

```
1. Read ARCHITECTURE.md
2. Create adapter file in adapters/
3. Implement adapter interface:
   - Input: external events
   - Output: domain events
4. Add to main.py orchestrator
5. Add error codes to ERROR_HANDLING.md
6. Update health check
7. Test integration
```

### 5c. Modifying UI Component

Based on `docs/DESIGN.md`:

```
1. Read DESIGN.md
2. Check component library (lib/components)
3. Follow design principles:
   - Operator-first
   - Status pills (green/yellow/red)
   - Event-stream UI
   - Zero modal
   - Keyboard-first
4. Use Tailwind v4 @theme variables
5. Test responsiveness
6. Update DESIGN.md if needed
```

---

## 6. Health Check Integration

Kiro dapat menggunakan health check untuk validasi:

### 6a. Before Making Changes

```bash
# Check system health
scripts\health-check.bat

# Output:
# - Health score: 95%
# - Status: HEALTHY
# - All dependencies OK
```

### 6b. After Making Changes

```bash
# Verify changes didn't break anything
scripts\health-check.bat

# If FAIL:
# - Read error message
# - Check ERROR_HANDLING.md
# - Fix issue
# - Re-run health check
```

### 6c. During Development

```bash
# Monitor runtime
scripts\monitor-runtime.bat

# Output:
# - Process status
# - Port status
# - Recent errors
# - Overall status: HEALTHY/DEGRADED/STOPPED
```

---

## 7. Error Handling Workflow

### 7a. When Error Occurs

```
1. User reports error or health check fails
   ↓
2. Kiro reads ERROR_HANDLING.md
   ↓
3. Find error code in matrix
   ↓
4. Check "File pertama dibuka"
   ↓
5. Read that file
   ↓
6. Analyze root cause
   ↓
7. Apply recovery strategy from matrix
   ↓
8. Test with health check
```

### 7b. Example: TIKTOK_DISCONNECT

```
Error Code: TIKTOK_DISCONNECT
Domain: TikTok
Severity: High
Recovery: Auto-reconnect 3× exp backoff
File pertama: adapters/tiktok.py

Kiro workflow:
1. readFile("docs/ERROR_HANDLING.md")
2. Find TIKTOK_DISCONNECT entry
3. readFile("apps/worker/src/banghack/adapters/tiktok.py")
4. Check reconnection logic
5. Verify exponential backoff implementation
6. Test with health check
```

---

## 8. Documentation-Driven Development

Kiro mengikuti prinsip **documentation-first**:

### 8a. Source of Truth

```
1. PRD.md          → What to build
2. ARCHITECTURE.md → How it's structured
3. DESIGN.md       → How it looks
4. ERROR_HANDLING.md → How to handle errors
5. PLAN.md         → What's next
```

### 8b. Before Any Change

```
✅ MUST READ:
- ARCHITECTURE.md (understand system)
- ERROR_HANDLING.md (understand error taxonomy)
- DESIGN.md (if UI change)

✅ SHOULD READ:
- PRD.md (understand requirements)
- PLAN.md (check roadmap)
```

### 8c. After Any Change

```
✅ MUST UPDATE:
- Code files
- Health check scripts (if new checks needed)
- ERROR_HANDLING.md (if new error types)

✅ SHOULD UPDATE:
- ARCHITECTURE.md (if structure changed)
- DESIGN.md (if UI changed)
- CHANGELOG.md (for releases)
```

---

## 9. Kiro vs VSCode: Practical Examples

### Example 1: Add New Error Code

**VSCode Workflow:**
```
1. Open ERROR_HANDLING.md
2. Manually add row to table
3. Open adapters/llm.py
4. Add error class
5. Save both files
6. Git commit
```

**Kiro Workflow:**
```
1. readFile("docs/ERROR_HANDLING.md")
2. strReplace(oldStr=table, newStr=table_with_new_row)
3. readFile("apps/worker/src/banghack/adapters/llm.py")
4. strReplace(oldStr=error_classes, newStr=error_classes_with_new)
5. executePwsh("git add . && git commit -m 'feat: add LLM_NEW_ERROR'")
```

### Example 2: Fix Bug

**VSCode Workflow:**
```
1. User reports bug
2. Open file in editor
3. Set breakpoint
4. Run debugger
5. Fix bug
6. Test manually
7. Commit
```

**Kiro Workflow:**
```
1. User reports bug
2. readFile("docs/ERROR_HANDLING.md") → find error code
3. readFile(file_pertama_dibuka)
4. Analyze code
5. strReplace(buggy_code, fixed_code)
6. executePwsh("scripts\health-check.bat")
7. executePwsh("git commit -m 'fix: ...'")
```

---

## 10. Best Practices Summary

### ✅ DO

1. **Always read docs first** (ARCHITECTURE.md, ERROR_HANDLING.md)
2. **Use health checks** before and after changes
3. **Follow error taxonomy** from ERROR_HANDLING.md
4. **Respect architecture boundaries** from ARCHITECTURE.md
5. **Update docs** when making structural changes
6. **Use specific error codes** not generic exceptions
7. **Test with health-check.bat** after changes
8. **Read existing code** before adding new code

### ❌ DON'T

1. **Don't guess** implementation details
2. **Don't skip** documentation reading
3. **Don't mix** concerns across modules
4. **Don't use** generic error messages
5. **Don't ignore** health check failures
6. **Don't break** existing patterns
7. **Don't forget** to update ERROR_HANDLING.md
8. **Don't assume** VSCode workflows apply

---

## 11. Quick Reference

### Common Commands

```bash
# Health check
scripts\health-check.bat

# Runtime monitor
scripts\monitor-runtime.bat

# Start development
scripts\dev.bat

# Backup to GitHub
scripts\backup-github.bat

# Fix SvelteKit warnings
scripts\fix-svelte-tsconfig.bat
```

### Common File Paths

```
docs/ARCHITECTURE.md          → System architecture
docs/ERROR_HANDLING.md        → Error taxonomy
docs/DESIGN.md                → UI/UX design
docs/TROUBLESHOOTING.md       → Common issues
apps/worker/src/banghack/     → Worker code
apps/controller/src/          → Controller code
scripts/                      → Utility scripts
```

### Error Code Prefixes

```
TIKTOK_    → adapters/tiktok.py
LLM_       → adapters/llm.py
TTS_       → adapters/tts.py
GUARDRAIL_ → core/guardrail.py
OBS_       → adapters/obs.py
IPC_       → ipc/ws_server.py or ipc/http_api.py
CONFIG_    → config/settings.py
QUEUE_     → core/queue.py
```

---

**Last Updated:** 2026-04-22  
**For:** Kiro IDE users developing livetik
