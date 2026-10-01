// Re-run on every page load: Material's instant navigation does not fire DOMContentLoaded.
document$.subscribe(function () {
  mermaid.initialize({ startOnLoad: false, securityLevel: "strict" });
  mermaid.run({ querySelector: ".mermaid" });
});
