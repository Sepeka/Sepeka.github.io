---
layout: post
permalink: /blog/2026/Interactivate-Information-Theory/
title: "Interactivate Information Theory"
date: 2026-06-24
published: true
description: "Interactivate Information Theory: learn information theory in an interactive, modern way."
categories: Information-Theory
citation: true
---

Claude Shannon sought to inject a note of moderation by warning that his field was being oversold as a universal panacea [\[1\]](#reference-1 "The Bandwagon"); ironically, time has shown that this temporary "bandwagon" was actually the arrival of one of the most enduring mathematical frameworks ever conceived.

Chapter 1 of Cover and Thomas's *Elements of Information Theory* [\[2\]](#reference-2 "Elements of Information Theory") previews the central questions of information theory: how efficiently information can be described, and how reliably it can be transmitted through a noisy channel. It introduces entropy as the fundamental limit of lossless compression, mutual information as a measure of dependence, and channel capacity as the highest reliable communication rate. It also shows how these ideas connect to typical sequences, statistical inference, gambling, and Kolmogorov complexity.

We begin the detailed development with entropy in Section 2.1. The accompanying notebook follows the book's definitions, lemmas, and examples through interactive plots, experiments, Python calculations, and Lean proofs.

<details id="entropy-notebook-panel" style="margin: 1.5rem 0; border: 1px solid var(--global-divider-color); border-radius: 8px; overflow: hidden">
  <summary style="padding: 1rem 1.2rem; cursor: pointer; font-weight: 600">Interactive notebook · Section 2.1: Entropy</summary>
  <div style="padding: 0 1rem 1rem">
    <p>
      <a id="entropy-notebook-fullscreen" href="{{ '/assets/notebooks/entropy-2-1/' | relative_url }}" target="_blank" rel="noopener noreferrer">Open full screen</a>
      ·
      <a href="https://github.com/Sepeka/Sepeka.github.io/blob/main/notebooks/entropy_2_1/entropy_2_1.py" target="_blank" rel="noopener noreferrer">View source on GitHub</a>
    </p>
    <iframe
      id="entropy-notebook"
      data-src="{{ '/assets/notebooks/entropy-2-1/' | relative_url }}"
      title="Interactive Section 2.1 entropy notebook"
      loading="lazy"
      style="width: 100%; height: min(640px, 72vh); min-height: 480px; border: 1px solid var(--global-divider-color); border-radius: 8px; background: var(--global-bg-color)"
      allow="clipboard-read; clipboard-write"
    ></iframe>
  </div>
</details>

<script>
  (() => {
    const notebook = document.getElementById("entropy-notebook");
    const fullscreen = document.getElementById("entropy-notebook-fullscreen");
    const panel = document.getElementById("entropy-notebook-panel");

    const pageTheme = () => (document.documentElement.dataset.theme === "dark" ? "dark" : "light");

    const themedUrl = () => {
      const url = new URL(notebook.dataset.src, window.location.href);
      url.searchParams.set("theme", pageTheme());
      return url;
    };

    const applyTheme = () => {
      const theme = pageTheme();
      const dark = theme === "dark";
      const url = themedUrl();
      fullscreen.href = url.href;

      if (!panel.open) return;

      if (notebook.dataset.loaded !== "true") {
        notebook.dataset.loaded = "true";
        notebook.src = url.href;
        return;
      }

      try {
        const notebookDocument = notebook.contentDocument;
        notebookDocument.body.classList.toggle("dark", dark);
        notebookDocument.body.classList.toggle("dark-theme", dark);
        notebookDocument.body.dataset.theme = theme;
      } catch (_error) {
        // The notebook is same-origin in production. Its initial URL already
        // carries the correct theme if a browser blocks DOM access.
      }
    };

    notebook.addEventListener("load", applyTheme);
    panel.addEventListener("toggle", applyTheme);
    new MutationObserver(applyTheme).observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
    applyTheme();
  })();
</script>

---

[1] C. E. Shannon, ["The Bandwagon"](https://doi.org/10.1109/TIT.1956.1056774), *IEEE Transactions on Information Theory*, vol. 2, no. 1, p. 3, Mar. 1956. doi: 10.1109/TIT.1956.1056774.
{: #reference-1 }

[2] T. M. Cover and J. A. Thomas, [*Elements of Information Theory*](https://doi.org/10.1002/047174882X), 2nd ed. Hoboken, NJ: John Wiley & Sons, 2006. doi: 10.1002/047174882X.
{: #reference-2 }
