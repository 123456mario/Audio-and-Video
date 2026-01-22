# AI Coding Rules (Vibe Coding)

## 🤖 Git Workflow Rules
1.  **Commit Frequency**:
    *   **Auto-Commit**: Perform a commit immediately after completing a specific feature or bug fix.
    *   **Checkpoint**: Always commit with `chore: save before major change` BEFORE starting a big refactor or complex coding task.
2.  **Commit Messages**:
    *   Use Korean (Hangul) for descriptions to be friendly.
    *   Format: `type: message`
        *   `feat`: New feature (기능 추가)
        *   `fix`: Bug fix (버그 수정)
        *   `docs`: Documentation (문서 작업)
        *   `chore`: Maintenance/Config (잡일/설정)
    *   Example: `feat: 마스터 볼륨 제어 기능 추가`

## 🛡️ Safety First
*   **Never delete** user files without explicit permission.
*   **Check .gitignore** before adding new large files.
*   **Run Check**: `git status` -> `git add .` -> `git commit -m "..."`

## 🧠 Context Awareness
*   When the user asks "What changed?", use `git log --oneline` or `git diff` to explain.
*   If a bug appears after an edit, offer `git reset --soft HEAD~1` to undo the last step safely.
