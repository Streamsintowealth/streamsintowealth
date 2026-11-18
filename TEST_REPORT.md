# Integration test report — 18 November 2026

Source: latest six-page Streams Into Wealth RECONNECT_DATA bundle from Teaching Finance – P6.

## Confirmed against the source package
- Six intended pages are present and use the existing Streams Into Wealth branding.
- Markets & Sectors includes an interactive five-indicator checklist covering real GDP, unemployment, Core PCE inflation, ISM manufacturing/services, and Federal Reserve policy rate.
- Each section accepts prior/latest figures and shows a directional signal.
- The eight-stage display covers trough, early/mid/late expansion, peak and early/mid/late contraction.
- A stage marker moves with the estimated result, which includes sector/industry research guidance.
- Links to official macro sources and the educational-verification notice are preserved.
- Added missing root-level data.js dependency (from the preceding Streams Into Wealth master package) to prevent a 404 on the new six-page bundle.

## Local verification
- All inline JavaScript blocks passed `node --check`.
- Browser content smoke-test loaded Home, Research, Opportunities, Econ Data, Political Leaders, and Markets without syntax errors.
- The economic checklist accepted example inputs, showed 5 completed sections, estimated a stage, and moved its pointer.
- `CRWD` on Opportunities displayed CrowdStrike and SWOT content; `Wes Moore` on Political Leaders returned content.
- Note: the test browser blocks local HTTP/file navigation and third-party resources; pages were evaluated as injected HTML with remote fonts/images disabled in test only. A History API warning in the injected Markets test is specific to about:blank origin and not a deployed-site failure.

## Not claimed
- Automatic live macro readings: visitors enter verified numbers manually.
- Official NBER recession dating or predictive accuracy: this is an educational heuristic.
- Live GitHub Pages deployment tested: not performed; publish and verify the links there.
- 800 fully researched company profiles: not established by this package.
