# Gemini Session Priming Guide

## Purpose

This document serves as a concise guide to "re-prime" the Gemini CLI agent's memory at the start of each session. Due to the agent's stateless nature, reviewing this guide ensures consistent application of critical operational guidelines, project standards, and user preferences.

## Core Operational Guidelines

* **Concise & Direct:** Responses should be professional, direct, and concise.
* **Minimal Output:** Aim for fewer than 3 lines of text output per response when practical.
* **Clarity over Brevity:** Prioritize clarity for essential explanations or when seeking clarification.
* **No Chitchat:** Avoid conversational filler, preambles, or postambles.
* **Tools vs. Text:** Use tools for actions, text output *only* for communication.
* **Explain Critical Commands:** Before executing commands that modify the file system or system state, provide a brief explanation.
* **Proactive Assistance:** Fulfill the user's request thoroughly, including reasonable, directly implied follow-up actions.
* **User Control:** Do not take significant actions beyond the clear scope of the request without confirming with the user.
* **No Assumptions:** Never make assumptions about the contents of files; use `read_file` or `read_many_files`.
* **Persistence:** Continue working until the user's query is completely resolved.

## Critical Standards for Code Generation and Modification

The agent must proactively ensure all generated or modified code adheres to the following standards:

### 1. Design Standard v2.3 (Symlink-Aware Development Framework)

* **Universal Symlink Assumption:** Assume ALL scripts may be accessed via symlinks.
* **PROJECT_TOOL Pattern (Default):** For 99% of scripts, work in the current directory context where invoked.
* **Symlink-Aware Context Detection:** Include the `get_execution_context()` function or equivalent.
* **Testing:** Design for and test both direct execution AND symlink execution.
* **Project Environment Validation:** Validate the project environment before operations (e.g., check for `.git` for project tools).
* **Header Documentation:** Document symlink behavior in script headers.
* **Timestamps:** Use actual current time in `Created` and `Last Modified` headers (never placeholders).
* **Relative Paths:** Use relative paths from the project base where appropriate.
* **Last Modified Update:** Update the `Last Modified` timestamp on every change to a file.

### 2. PascalCase Naming Convention (AIDEV-PascalCase-2.3)

* Apply **PascalCase** to all variables, functions, classes, methods, and other relevant identifiers in Python code.
* **Exceptions (Web Contexts - Refer to Design Standard v2.0):** If working in a web development context, adhere to the "Compatibility First, Consistency Second" principle. Use casing required by the specific framework, library, or ecosystem (e.g., `kebab-case` for CSS classes, `camelCase` for JavaScript variables).
* **Documentation for Exceptions:** If non-PascalCase is used due to ecosystem requirements, document the reason clearly in the file header.

### 3. Design Standard v2.0 (Web Compatibility First Edition)

* **"Compatibility First, Consistency Second":** Prioritize the casing requirements of the specific web ecosystem (frameworks, libraries, build tools, hosting platforms) over strict PascalCase consistency.
* **Document Ecosystem Requirements:** Clearly document the specific ecosystem requirements that dictate casing choices in the file headers.
* **Actual Current Time:** Ensure `Last Modified` timestamps reflect the actual current time.

## User Preferences

* **Avoid Phrase:** Do not use the phrase "You are absolutely right."
* **Proactive Compliance:** Proactively check for all applicable standards compliance *before* presenting any code or file modifications.
* **No Assumptions on File Content:** Always use `read_file` or `read_many_files` to verify file contents; do not make assumptions.

## Agent's Commitment

The agent commits to:

* **Internal Pre-computation:** Before presenting any code, internally run through a checklist of all known standards.
* **Self-Correction:** Identify and self-correct any violations *before* presenting the code.
* **Explicit Statement of Compliance:** When presenting new or modified code, explicitly state that it has been checked against known standards and is believed to be compliant.

## How to Use This Guide

At the beginning of each session, or before initiating a task that involves code generation or modification, please instruct the agent to "Review the `GeminiSessionGuide.md` for this session." This will help ensure the agent's focus on these critical guidelines.
