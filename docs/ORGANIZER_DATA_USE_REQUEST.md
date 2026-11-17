# Organizer clarification required before unpaid-model dev evaluation

**Recipient:** ple-bench@google.com (published contact in official PLE competition guide)
**Subject:** PLE dev-set data use with Gemini API Free Tier — permission and no-cost options

Hello PLE team,

I'm participating in the PLE Harness Competition with Aegis PLE:
https://github.com/samertall/ple-aegis-harness

My Hugging Face account has been granted access to the gated 29-task development dataset. The harness has passed its GitHub CI, official kit configuration validation and Docker packaging, and its public smoke/MCP protocol was tested using a deterministic simulated model. The authentic engineering dev-set evaluation and artifacts have not yet been run.

I'd like to complete the required development evaluation without enabling any paid API or cloud billing. I have access to Gemini 3.8 Flash through Google AI Studio, and am exploring its Unpaid/Free Tier endpoint. However, Google's Gemini API terms say unpaid-service inputs and outputs may be used for improving products and ML technologies, while the PLE gated dataset has restrictions on training, distillation, redistribution, and benchmark integrity.

Could you clarify:

1. Is it permitted to send gated PLE development-task prompts and engineering source files to the **unpaid Gemini API Free Tier**, given its data-improvement terms? Does this also cover grader/judge prompts that might include gated task content?
2. If that processing is **not** allowed, is there an official sponsored model endpoint, free development inference allowance, or another approved zero-cost approach to generate authentic eval/run.py dev-set artifacts?
3. Can a participant use Gemini 3.8 Flash as both the Stage 2 google-cloud/gemini-3.8-flash sponsored model and a Gemini API Free Tier local development model, assuming the actual model identity matches?
4. Is any additional restriction relevant to publishing the kit-exported artifacts/ directory to a public GitHub repository?

I won't transmit restricted task material to an unpaid endpoint or treat simulated results as benchmark evidence until this is clarified.

Thank you,
Samer Tallauze

---

This is a **draft**, not a sent email. Don't attach gated task files or private API keys. Organizer contact: https://ple-bench.com/competition/guide. Google unpaid-service terms: https://aistudio.google.com/docs/terms
